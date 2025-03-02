"""A lightweight and RFC 8594 compliant FastAPI middleware to facilitate endpoint deprecation."""

from typing import Any

from fastapi_sunset._version_manager import _VersionManager
from fastapi_sunset.behaviors import (
    BasePeriodBehavior,
    DoNothing,
    RedirectUsers,
    RespondError,
    WarnDevelopers,
)
from fastapi_sunset.configuration import SunsetConfiguration
from fastapi_sunset.sunset import SunsetEndpointsMiddleware

_version_manager = _VersionManager()


def __getattr__(name: str) -> Any:
    """Fallback to lazy load version information."""
    if name in ("__version__", "__version_tuple__"):
        return _version_manager.get_version_attribute(name)
    message = f"Module 'fastapi_sunset' has no attribute '{name}'."
    raise AttributeError(message)


__all__ = [
    "BasePeriodBehavior",
    "DoNothing",
    "RedirectUsers",
    "RespondError",
    "SunsetConfiguration",
    "SunsetEndpointsMiddleware",
    "WarnDevelopers",
]

__version__: str
__version_tuple__: tuple[str | int, ...]
