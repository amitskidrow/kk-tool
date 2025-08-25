from __future__ import annotations

__all__ = ["__version__"]

try:
    try:
        # Python 3.8+
        from importlib.metadata import version as _pkg_version  # type: ignore
    except Exception:  # pragma: no cover
        from importlib_metadata import version as _pkg_version  # type: ignore
    __version__ = _pkg_version("kktool")
except Exception:
    # Fallback if package metadata is unavailable (e.g., running from source)
    __version__ = "0.1.0"

