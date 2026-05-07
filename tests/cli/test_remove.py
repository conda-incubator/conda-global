"""Tests for ``conda global remove``."""

from __future__ import annotations

import argparse

import pytest

from conda_global.cli.remove import execute_remove
from conda_global.exceptions import ToolNotFoundError
from conda_global.manifest import Manifest


def test_remove_package(
    mock_conda_home,
    fake_envs_create,
    seeded_manifest,
    rich_console,
):
    seeded_manifest("ruff", dependencies={"ruff": "*", "black": "*"})

    args = argparse.Namespace(package="black", environment="ruff")
    result = execute_remove(args, console=rich_console)
    assert result == 0

    output = rich_console.file.getvalue()
    assert "Removing" in output
    assert "Removed" in output

    tools = Manifest(mock_conda_home / "manifest.toml").load()
    assert "black" not in tools["ruff"].dependencies
    assert "ruff" in tools["ruff"].dependencies
    assert "black" not in fake_envs_create[0]["packages"]


def test_remove_nonexistent_package(
    mock_conda_home,
    seeded_manifest,
    rich_console,
):
    seeded_manifest("ruff")

    args = argparse.Namespace(package="nope", environment="ruff")
    result = execute_remove(args, console=rich_console)
    assert result == 1
    assert "not in environment" in rich_console.file.getvalue()


def test_remove_nonexistent_tool(mock_conda_home, rich_console):
    args = argparse.Namespace(package="numpy", environment="nonexistent")
    with pytest.raises(ToolNotFoundError):
        execute_remove(args, console=rich_console)
