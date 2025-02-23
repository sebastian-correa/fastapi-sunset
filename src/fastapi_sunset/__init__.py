"""A lightweight and RFC 8594 compliant FastAPI middleware to facilitate endpoint deprecation."""

from fastapi_sunset.behaviors import BasePeriodBehavior, DoNothing, RedirectUsers, RespondError
from fastapi_sunset.configuration import SunsetConfiguration

__all__ = [
    "BasePeriodBehavior",
    "DoNothing",
    "RedirectUsers",
    "RespondError",
    "SunsetConfiguration",
]
