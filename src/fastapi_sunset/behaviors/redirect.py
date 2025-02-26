"""Redirect users to the given URL during this period."""

from __future__ import annotations

from typing import TYPE_CHECKING

from fastapi.responses import RedirectResponse

from fastapi_sunset.behaviors.base import BasePeriodBehavior

if TYPE_CHECKING:
    from fastapi_sunset.configuration import SunsetConfiguration


class RedirectUsers(BasePeriodBehavior):
    """Redirect to the given URL during this period."""

    url: str

    def behave_with(self, sunset_configuration: SunsetConfiguration) -> RedirectResponse:  # noqa: ARG002
        """Redirect to the given URL."""
        return RedirectResponse(url=self.url)
