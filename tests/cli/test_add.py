"""Tests for ``conda global add``."""

from __future__ import annotations

import argparse

import pytest

from conda_global.cli.add import execute_add
from conda_global.exceptions import ToolNotFoundError
from conda_global.manifest import Manifest


def test_add_package(
    mock_conda_home,
    fake_envs_create,
    seeded_manifest,
    rich_console,
):
    seeded_manifest("ruff", dependencies={"ruff": "*"})

    args = argparse.Namespace(package="black", environment="ruff")
    result = execute_add(args, console=rich_console)
    assert result == 0

    output = rich_console.file.getvalue()
    assert "Adding" in output
    assert "Added" in output

    tools = Manifest(mock_conda_home / "manifest.toml").load()
    assert "black" in tools["ruff"].dependencies

    specs = fake_envs_create[0]["packages"]
    assert "ruff" in specs
    assert "black" in specs


def test_add_nonexistent_tool(mock_conda_home, rich_console):
    args = argparse.Namespace(package="numpy", environment="nonexistent")
    with pytest.raises(ToolNotFoundError):
        execute_add(args, console=rich_console)
