from __future__ import annotations

import builtins
import warnings
from importlib.metadata import version
from typing import TYPE_CHECKING

import pytest

from fastapi_sunset import __version__
from fastapi_sunset._version_manager import _VersionManager

if TYPE_CHECKING:
    from collections.abc import Mapping, Sequence
    from types import ModuleType


class TestVersionManager:
    """Test the `_VersionManager` class."""

    @pytest.fixture
    def version_manager(self) -> _VersionManager:
        """Create a new `_VersionManager` instance."""
        return _VersionManager()

    def test_get_version_attribute_import_error(
        self, version_manager: _VersionManager, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test getting `__version__` & `__version_tuple__`  with unavailable `_version` module."""
        real_import = builtins.__import__

        def mock_import(
            name: str,
            globals: Mapping[str, object] | None = None,  # noqa: A002; builtins.__import__ signature.
            locals: Mapping[str, object] | None = None,  # noqa: A002; builtins.__import__ signature.
            fromlist: Sequence[str] = (),
            level: int = 0,
        ) -> ModuleType:
            """Fail to import `_version` but treat other imports normally."""
            if name == "fastapi_sunset._version":
                raise ImportError
            return real_import(name, globals=globals, locals=locals, fromlist=fromlist, level=level)

        monkeypatch.setattr(builtins, "__import__", mock_import)

        with pytest.warns(
            UserWarning, match="Real version information not available, returning dummy values."
        ):
            version = version_manager.get_version_attribute("__version__")

        with warnings.catch_warnings():  # Doesn't warn.
            warnings.simplefilter("error")
            version_tuple = version_manager.get_version_attribute("__version_tuple__")

        assert version == "0.0.0"
        assert version_tuple == (0, 0, 0)

    def test_get_version_attribute_succeeds(self, version_manager: _VersionManager) -> None:
        """Test `get_version_attribute` doesn't raise on `__version__` and `__version_tuple__`."""
        # Check fetch works (doesn't raise) since comparing against the imported values is circular.
        version_manager.get_version_attribute("__version_tuple__")
        version_manager.get_version_attribute("__version__")

    def test_get_version_attribute_error(self, version_manager: _VersionManager) -> None:
        """Test `get_version_attribute` raises with an invalid attribute name."""
        with pytest.raises(ValueError, match="VersionManager can only provide attributes"):
            version_manager.get_version_attribute("invalid_attribute")  # type: ignore[reportArgumentType]; testing an invalid value.


def test_bundled_version_matches_inferred() -> None:
    """Ensure the version in the package matches the version in the metadata."""
    assert __version__ == version("fastapi-sunset")
    assert __version__ == version("fastapi_sunset")
