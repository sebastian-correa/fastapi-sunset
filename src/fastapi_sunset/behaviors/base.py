"""Base for all period behaviors.

Users can subclass this to create their own behaviors for different periods of the sunset by
overriding the `behave_with` method and adding any additional attributes they need.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from pydantic import BaseModel

if TYPE_CHECKING:
    from fastapi_sunset.configuration import SunsetConfiguration


class BasePeriodBehavior(BaseModel):
    """Do nothing special (i.e., continue running the endpoint as usual) during this period."""

    include_headers: bool = True

    def format_message(self, sunset_configuration: SunsetConfiguration) -> str:
        """If the behavior has a `message`, format it with `sunset_on` and `alternative_url`.

        Args:
            sunset_configuration (SunsetConfiguration): The configuration for the whole endpoint
                sunset, of which this behavior is a part of.

        Returns:
            str: The formatted `message` if the behavior has one. If no `message` is found, returns
                an empty string.
        """
        plain_message = getattr(self, "message", "")
        try:
            return plain_message.format(
                sunset_on=sunset_configuration.sunset_on,
                alternative_url=sunset_configuration.alternative_url,
            )
        except KeyError as ke:
            msg = (
                "Only `sunset_on` and `alternative_url` are supported as `message` format "
                f"parameters. It seems you included the {ke} placeholder in the `message`: "
                f"{plain_message}."
            )
            raise RuntimeError(msg) from ke

    def behave_with(self, sunset_configuration: SunsetConfiguration) -> None:
        """Raise NotImplementedError as we don't expect users to use the base behavior."""
        msg = "You should implement different behaviors in subclasses of BasePeriodBehavior."
        raise NotImplementedError(msg)
