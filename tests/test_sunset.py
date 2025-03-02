from collections.abc import Awaitable, Callable
from datetime import datetime, timezone
from typing import TypeVar
from unittest.mock import AsyncMock, Mock

import pytest
from fastapi import Request, Response, status
from fastapi.responses import JSONResponse
from starlette.types import ASGIApp

from fastapi_sunset.behaviors.base import BasePeriodBehavior
from fastapi_sunset.configuration import SunsetConfiguration
from fastapi_sunset.sunset import SunsetEndpointsMiddleware, _make_headers

T = TypeVar("T", bound=str | None)


class TestMakeHeaders:
    """Test the _make_headers function."""

    @pytest.fixture
    def sunset_on(self) -> datetime:
        """Return a datetime object for the sunset date."""
        return datetime(2024, 1, 1, tzinfo=timezone.utc)

    def test_date_and_link(self, sunset_on: datetime) -> None:
        """Test the headers when both a date and link are provided."""
        headers = _make_headers(sunset_on, "https://new.example.com")

        assert headers == {
            "Sunset": "Mon, 01 Jan 2024 00:00:00 GMT",
            "Link": '<https://new.example.com>; rel="sunset"',
        }

    def test_date_only(self, sunset_on: datetime) -> None:
        """Test the headers when only a date is provided."""
        headers = _make_headers(sunset_on, None)

        assert headers == {"Sunset": "Mon, 01 Jan 2024 00:00:00 GMT"}

    def test_no_date(self) -> None:
        """Test the headers when you give a `null` date regardless of the link."""
        with pytest.raises(AttributeError):
            _make_headers(None, None)  # type: ignore[reportArgumentType]; this is what we're testing.

        with pytest.raises(AttributeError):
            _make_headers(None, "https://new.example.com")  # type: ignore[reportArgumentType]; this is what we're testing.


class TestSunsetEndpointMiddlewareRegistry:
    """Test the SunsetEndpointsMiddleware registry."""

    @pytest.fixture
    def mock_middleware(self) -> SunsetEndpointsMiddleware:
        """Return a mock middleware instance with no configurations attached."""
        return SunsetEndpointsMiddleware(Mock(spec=ASGIApp))

    @pytest.fixture
    def mock_sunset_configuration(self) -> SunsetConfiguration:
        """Return a mock sunset configuration."""
        sunset_configuration = Mock(spec=SunsetConfiguration)
        sunset_configuration.sunset_on = datetime(2024, 1, 1, tzinfo=timezone.utc)
        sunset_configuration.alternative_url = "/api/v2/deprecated"
        return sunset_configuration

    def test_register_sunset_configuration(
        self,
        mock_middleware: SunsetEndpointsMiddleware,
        mock_sunset_configuration: SunsetConfiguration,
    ) -> None:
        """Test that registering a sunset configuration works."""
        mock_middleware.register_sunset_configuration("/test", mock_sunset_configuration)

        assert "/test" in mock_middleware._sunset_registry
        assert mock_middleware._sunset_registry["/test"] is mock_sunset_configuration

    def test_register_duplicate_sunset_configuration(
        self,
        mock_middleware: SunsetEndpointsMiddleware,
        mock_sunset_configuration: SunsetConfiguration,
    ) -> None:
        """Test that registering a duplicate sunset configuration raises an error."""
        mock_middleware.register_sunset_configuration("/test", mock_sunset_configuration)

        with pytest.raises(ValueError, match="Endpoint /test already has a sunset configuration."):
            mock_middleware.register_sunset_configuration("/test", mock_sunset_configuration)

    def test_register_sunset_configurations(
        self,
        mock_middleware: SunsetEndpointsMiddleware,
        mock_sunset_configuration: SunsetConfiguration,
    ) -> None:
        """Test that registering multiple sunset configurations works."""
        mock_middleware.register_sunset_configurations(
            **{"/test1": mock_sunset_configuration, "/test2": mock_sunset_configuration}
        )

        assert "/test1" in mock_middleware._sunset_registry
        assert "/test2" in mock_middleware._sunset_registry


class TestSunsetEndpointMiddlewareDispatch:
    """Test the dispatch method of the SunsetEndpointsMiddleware class."""

    @pytest.fixture
    def mock_request(self) -> Mock:
        """Mock request object that simulates an API hit to /api/v1/deprecated."""
        request = Mock(spec=Request)
        request.url.path = "/api/v1/deprecated"
        return request

    @pytest.fixture
    def default_response(self) -> Response:
        """Return a default response."""
        return JSONResponse(
            content={"response_type": "default"},
            status_code=status.HTTP_200_OK,
            headers={"response_type": "default"},
        )

    @pytest.fixture
    def mock_call_next(self, default_response: Response) -> AsyncMock:
        """A mock `call_next` function that returns the default response.

        Args:
            default_response (Response): The default response to return when calling the returned
                function.

        Returns:
            AsyncMock: The mock `call_next` callable, with spec
                `Callable[[Request], Awaitable[Response]]`.
        """
        call_next = AsyncMock(spec=Callable[[Request], Awaitable[Response]])
        call_next.return_value = default_response
        return call_next

    def _build_mock_sunset_configuration(
        self, *, include_headers: bool = False
    ) -> SunsetConfiguration:
        """Build a Mock SunsetConfiguration instance.

        Notes:
            - `find_period_behavior` returns a Mock `BasePeriodBehavior` instance.
                - It has `include_headers` set to the given value.
                - Its `behave_with` method returns `None`.
            - The `alternative_url` is set to "/api/v2/deprecated".
            - The `sunset_on` is set to 2024-01-01T00:00:00+00:00.

        Args:
            include_headers (bool, optional): Whether the returned behavior includes headers or not.
                Defaults to False.

        Returns:
            SunsetConfiguration: The mocked `SunsetConfiguration`.
        """
        sunset_config = Mock(spec=SunsetConfiguration)
        behavior = Mock(spec=BasePeriodBehavior)
        behavior.include_headers = include_headers
        behavior.behave_with.return_value = None
        sunset_config.find_period_behavior.return_value = behavior
        sunset_config.sunset_on = datetime(2024, 1, 1, tzinfo=timezone.utc)
        sunset_config.alternative_url = "/api/v2/deprecated"
        return sunset_config

    @pytest.fixture
    def mock_sunset_configuration_headers(self) -> SunsetConfiguration:
        """Return a mock sunset configuration that includes sunset headers."""
        return self._build_mock_sunset_configuration(include_headers=True)

    @pytest.fixture
    def mock_sunset_configuration_no_headers(self) -> SunsetConfiguration:
        """Return a mock sunset configuration that includes no sunset headers."""
        return self._build_mock_sunset_configuration(include_headers=False)

    @pytest.fixture
    def mock_middleware(self) -> SunsetEndpointsMiddleware:
        """Return a mock middleware instance with no configurations attached."""
        return SunsetEndpointsMiddleware(Mock(spec=ASGIApp))

    @pytest.mark.asyncio
    async def test_dispatch_unregistered_endpoint(
        self,
        mock_middleware: SunsetEndpointsMiddleware,
        mock_sunset_configuration_headers: SunsetConfiguration,
        mock_request: Mock,
        mock_call_next: AsyncMock,
        default_response: Response,
    ) -> None:
        """Ensure call_next is called and nothing else happens if the endpoint is not registered."""
        mock_middleware.register_sunset_configuration(
            "/api/v1/different_deprecated", mock_sunset_configuration_headers
        )

        response = await mock_middleware.dispatch(mock_request, mock_call_next)

        assert mock_call_next.called
        assert response is default_response
        assert "Sunset" not in response.headers
        assert "Link" not in response.headers

    @pytest.mark.asyncio
    async def test_dispatch_with_include_headers(
        self,
        mock_middleware: SunsetEndpointsMiddleware,
        mock_sunset_configuration_headers: SunsetConfiguration,
        mock_request: Mock,
        mock_call_next: AsyncMock,
        default_response: Response,
    ) -> None:
        """Ensure headers are added when behavior include headers."""
        mock_middleware.register_sunset_configuration(
            "/api/v1/deprecated", mock_sunset_configuration_headers
        )

        response = await mock_middleware.dispatch(mock_request, mock_call_next)

        assert mock_call_next.called
        assert response is default_response  # Because behave_with returns None.
        assert "Sunset" in response.headers
        assert "Link" in response.headers
        assert response.headers["Sunset"] == "Mon, 01 Jan 2024 00:00:00 GMT"
        assert response.headers["Link"] == '</api/v2/deprecated>; rel="sunset"'

    @pytest.mark.asyncio
    async def test_dispatch_without_include_headers(
        self,
        mock_middleware: SunsetEndpointsMiddleware,
        mock_sunset_configuration_no_headers: SunsetConfiguration,
        mock_request: Mock,
        mock_call_next: AsyncMock,
        default_response: Response,
    ) -> None:
        """Ensure headers are not added when behavior does not include headers."""
        mock_middleware.register_sunset_configuration(
            "/api/v1/deprecated", mock_sunset_configuration_no_headers
        )
        response = await mock_middleware.dispatch(mock_request, mock_call_next)

        assert mock_call_next.called
        assert response is default_response  # Because behave_with returns None.
        assert "Sunset" not in response.headers
        assert "Link" not in response.headers

    @pytest.mark.asyncio
    async def test_dispatch_behavior_returns_response(
        self,
        mock_middleware: SunsetEndpointsMiddleware,
        mock_sunset_configuration_headers: SunsetConfiguration,
        mock_request: Mock,
        mock_call_next: AsyncMock,
    ) -> None:
        """Ensure call_next is not called when behavior responds."""
        behavior = mock_sunset_configuration_headers.find_period_behavior.return_value
        behavior_response = JSONResponse(
            content={"message": "endpoint deprecated"}, status_code=410
        )
        behavior.behave_with.return_value = behavior_response
        mock_sunset_configuration_headers.find_period_behavior.return_value = behavior

        mock_middleware.register_sunset_configuration(
            "/api/v1/deprecated", mock_sunset_configuration_headers
        )

        response = await mock_middleware.dispatch(mock_request, mock_call_next)

        assert not mock_call_next.called
        assert response is behavior_response
