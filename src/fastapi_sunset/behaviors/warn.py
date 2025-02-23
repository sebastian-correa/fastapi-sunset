"""Behavior to warn developers during this period."""

from __future__ import annotations

import warnings
from typing import TYPE_CHECKING

from fastapi_sunset.behaviors import BasePeriodBehavior

if TYPE_CHECKING:
    from fastapi_sunset.configuration import SunsetConfiguration


class WarnDevelopers(BasePeriodBehavior):
    """Warn developers (not users) during this period."""

    message: str
    """Message to be displayed during in the warning during this period.

    Has access to the following format parameters from the `SunsetConfiguration`:
        - `sunset_on`.
        - `alternative_url`.
    """
    category: type[Warning] = FutureWarning

    def behave_with(self, sunset_configuration: SunsetConfiguration) -> None:
        """Emit a warning."""
        warnings.warn(self.format_message(sunset_configuration), self.category, stacklevel=2)
