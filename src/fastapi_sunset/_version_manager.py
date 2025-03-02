"""Manage __version__ and __version_tuple__ loading."""

import warnings
from typing import Literal


class _VersionManager:
    """Manage __version__ and __version_tuple__ loading."""

    def __init__(self) -> None:
        self._warned = False

    def get_version_attribute(
        self, name: Literal["__version__", "__version_tuple__"]
    ) -> str | tuple[int | str, ...]:
        """Get version information lazily.

        If the `_version.py` module is available (most cases), return its version information.
        Otherwise, emit a warning on first access and return dummy values so that users of the code
        from source can still use the package.

        Attrs:
            name (Literal["__version__", "__version_tuple__"]): The attribute name to retrieve.

        Returns:
            str | tuple[int | str, ...]: The version information.
        """
        if name not in ("__version__", "__version_tuple__"):
            msg = (
                "VersionManager can only provide attributes `__version__` and "
                f"`__version_tuple__`, but you asked for `{name}`."
            )
            raise ValueError(msg)

        try:
            from fastapi_sunset._version import __version__, __version_tuple__
        except ImportError:
            if not self._warned:
                message = (
                    "Real version information not available, returning dummy values. Are you "
                    "running from source? The `_version.py` module containing the version "
                    "information is generated when building the package, so consider building the "
                    "package first. Alternatively, you can manually set the version information by "
                    "including your own `_version.py` with `__version__` and `__version_tuple__` "
                    " in your source copy. This warning won't be emitted again."
                )
                warnings.warn(message, stacklevel=2)
                self._warned = True
            return "0.0.0" if name == "__version__" else (0, 0, 0)
        else:
            return __version__ if name == "__version__" else __version_tuple__
