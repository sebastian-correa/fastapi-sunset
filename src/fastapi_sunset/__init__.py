"""A lightweight and RFC 8594 compliant FastAPI middleware to facilitate endpoint deprecation."""

from fastapi_sunset.behaviors import (
    BasePeriodBehavior,
    DoNothing,
    RedirectUsers,
    RespondError,
    WarnDevelopers,
)
from fastapi_sunset.configuration import SunsetConfiguration
from fastapi_sunset.sunset import SunsetEndpointsMiddleware

__all__ = [
    "BasePeriodBehavior",
    "DoNothing",
    "RedirectUsers",
    "RespondError",
    "SunsetConfiguration",
    "SunsetEndpointsMiddleware",
    "WarnDevelopers",
]
