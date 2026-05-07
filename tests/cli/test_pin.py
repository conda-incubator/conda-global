"""Tests for ``conda global pin`` and ``conda global unpin``."""

from __future__ import annotations

import argparse

import pytest

from conda_global.cli.pin import execute_pin, execute_unpin
from conda_global.exceptions import ToolNotFoundError
from conda_global.manifest import Manifest
from conda_global.models import ToolEnv


@pytest.mark.parametrize(
    "handler,initial,expected,label",
    [
        pytest.param(execute_pin, False, True, "Pinned", id="pin"),
        pytest.param(execute_unpin, True, False, "Unpinned", id="unpin"),
    ],
)
def test_pin_unpin(mock_conda_home, rich_console, handler, initial, expected, label):
    manifest = Manifest(mock_conda_home / "manifest.toml")
    manifest.add(ToolEnv(name="gh", dependencies={"gh": "*"}, pinned=initial))

    result = handler(argparse.Namespace(environment="gh"), console=rich_console)
    assert result == 0
    assert manifest.load()["gh"].pinned is expected
    assert label in rich_console.file.getvalue()


@pytest.mark.parametrize("handler", [execute_pin, execute_unpin])
def test_pin_nonexistent_tool(mock_conda_home, rich_console, handler):
    with pytest.raises(ToolNotFoundError):
        handler(argparse.Namespace(environment="nonexistent"), console=rich_console)
