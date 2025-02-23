"""Behavior that does nothing (i.e., continue running the endpoint as usual) during this period."""

from __future__ import annotations

from typing import TYPE_CHECKING

from fastapi_sunset.behaviors import BasePeriodBehavior

if TYPE_CHECKING:
    from fastapi_sunset.configuration import SunsetConfiguration


class DoNothing(BasePeriodBehavior):
    """Do nothing special (i.e., continue running the endpoint as usual) during this period."""

    def behave_with(self, sunset_configuration: SunsetConfiguration) -> None:
        """Do nothing."""
