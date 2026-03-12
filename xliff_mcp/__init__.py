"""XLIFF MCP Server - Process XLIFF translation files via Model Context Protocol."""

from __future__ import annotations

import re
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path

_PACKAGE_NAME = "xliff-mcp-server"
_VERSION_PATTERN = re.compile(r'^version = "(?P<version>[^"]+)"$', re.MULTILINE)
_PYPROJECT_PATH = Path(__file__).resolve().parent.parent / "pyproject.toml"


def _load_local_version() -> str:
    match = _VERSION_PATTERN.search(_PYPROJECT_PATH.read_text(encoding="utf-8"))
    if match is None:
        raise RuntimeError(f"Could not determine package version from {_PYPROJECT_PATH}")
    return match.group("version")


if _PYPROJECT_PATH.exists():
    __version__ = _load_local_version()
else:
    try:
        __version__ = version(_PACKAGE_NAME)
    except PackageNotFoundError:
        __version__ = "0.0.0"
