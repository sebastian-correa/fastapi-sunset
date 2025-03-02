"""Implement a middleware to handle deprecation of endpoints."""

from datetime import datetime, timezone

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.types import ASGIApp

from fastapi_sunset.configuration import SunsetConfiguration


def _make_headers(sunset_on: datetime, link: str | None) -> dict[str, str]:
    """Create the Sunset and Link headers if necessary.

    Args:
        sunset_on (datetime): When the endpoint will be deprecated.
        link (str | None): URL to the new endpoint or documentation. If None, won't include a `Link`
            header. Defaults to None.

    Returns:
        dict[str, str]: The headers to include in the response.
    """
    headers = {"Sunset": sunset_on.strftime("%a, %d %b %Y %H:%M:%S GMT")}
    if link:
        headers["Link"] = f'<{link}>; rel="sunset"'
    return headers


class SunsetEndpointsMiddleware(BaseHTTPMiddleware):
    """Handle deprecation of endpoints by adding a Sunset header and performing actions.

    Args:
        app (ASGIApp): The ASGI application to wrap.
        **sunset_configurations (SunsetConfiguration): URL paths and their sunset configurations.
            The path must match that of the `request.url.path`. See
            `self.register_sunset_configuration` for details.
    """

    def __init__(self, app: ASGIApp, **sunset_configurations: SunsetConfiguration) -> None:
        super().__init__(app)
        self._sunset_registry: dict[str, SunsetConfiguration] = {}
        self.register_sunset_configurations(**sunset_configurations)

    def register_sunset_configuration(
        self, endpoint_url: str, sunset_configuration: SunsetConfiguration
    ) -> None:
        """Register a sunset configuration to the middleware.

        Args:
            endpoint_url (str): The endpoint path to sunset. The path must match that of the
                `request.url.path`.
            sunset_configuration (SunsetConfiguration): The configuration to deprecate the given
                `endpoint_url`.

        Raises:
            ValueError: If the `endpoint_url` is already registered.
        """
        if endpoint_url in self._sunset_registry:
            msg = f"Endpoint {endpoint_url} already has a sunset configuration."
            raise ValueError(msg)
        self._sunset_registry[endpoint_url] = sunset_configuration

    def register_sunset_configurations(self, **sunset_configurations: SunsetConfiguration) -> None:
        """Register all the given sunset configurations to the middleware.

        Args:
            **sunset_configurations (SunsetConfiguration): Each key and value is passed to
                `self.register_sunset_configuration` as `endpoint_url` and `sunset_configuration
        """
        for endpoint_url, sunset_configuration in sunset_configurations.items():
            self.register_sunset_configuration(endpoint_url, sunset_configuration)

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        """Apply proper deprecation actions of the endpoint to the response where appropriate.

        Args:
            request (Request): The request being handled.
            call_next (RequestResponseEndpoint): The callable to await to continue the chain and get
                the response.

        Returns:
            Response: The response to the request with the proper headers set.
        """
        sunset_configuration = self._sunset_registry.get(request.url.path)
        if sunset_configuration is None:
            return await call_next(request)

        now = datetime.now(tz=timezone.utc)
        behavior = sunset_configuration.find_period_behavior(now)

        sunset_headers = (
            _make_headers(sunset_configuration.sunset_on, sunset_configuration.alternative_url)
            if behavior.include_headers
            else {}
        )

        outcome = behavior.behave_with(sunset_configuration)

        if outcome is not None:  # Returned a response so we cut the chain short.
            outcome.headers.update(sunset_headers)
            return outcome

        response = await call_next(request)
        response.headers.update(sunset_headers)

        return response
