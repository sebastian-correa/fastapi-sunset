"""Behavior that gives an error response during this period."""

from __future__ import annotations

from typing import TYPE_CHECKING

from fastapi import status
from fastapi.responses import JSONResponse

from fastapi_sunset.behaviors import BasePeriodBehavior

if TYPE_CHECKING:
    from fastapi_sunset.configuration import SunsetConfiguration


class RespondError(BasePeriodBehavior):
    """Give an error response during this period."""

    message: str
    """Message to include in the `detail` key of the error response's body.

    Has access to the following format parameters from the `SunsetConfiguration`:
        - `sunset_on`.
        - `alternative_url`.
    """
    error_code: int = status.HTTP_410_GONE

    def behave_with(self, sunset_configuration: SunsetConfiguration) -> JSONResponse:
        """Emit a warning."""
        return JSONResponse(
            content={"detail": self.format_message(sunset_configuration)},
            status_code=self.error_code,
        )
