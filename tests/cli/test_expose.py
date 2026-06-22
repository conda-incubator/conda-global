"""Tests for ``conda global expose`` and ``conda global hide``."""

from __future__ import annotations

import argparse
import stat

import pytest
from conda.common.path import BIN_DIRECTORY

from conda_global.cli.expose import execute_expose, execute_hide
from conda_global.exceptions import ToolNotFoundError
from conda_global.manifest import Manifest
from conda_global.models import ToolEnv


@pytest.fixture
def tool_with_binary(mock_conda_home, monkeypatch):
    """Create a tool env with a fake binary."""
    for mod in (
        "conda.base.constants",
        "conda_global.binaries",
    ):
        monkeypatch.setattr(f"{mod}.on_win", False)
    monkeypatch.setattr("conda_trampoline._ON_WIN", False)

    env_dir = mock_conda_home / "envs" / "ruff"
    bin_dir = env_dir / BIN_DIRECTORY
    bin_dir.mkdir(parents=True)
    binary = bin_dir / "ruff"
    binary.write_bytes(b"#!/bin/sh\n")
    binary.chmod(binary.stat().st_mode | stat.S_IXUSR)

    trampoline_dir = mock_conda_home / "bin" / "trampoline"
    trampoline_dir.mkdir(parents=True)
    (trampoline_dir / "_cg_trampoline").write_bytes(b"fake trampoline")

    Manifest(mock_conda_home / "manifest.toml").add(
        ToolEnv(name="ruff", dependencies={"ruff": "*"})
    )

    return mock_conda_home


@pytest.mark.parametrize(
    "mapping,expected_key",
    [
        pytest.param("ruff", "ruff", id="simple"),
        pytest.param("my-ruff=ruff", "my-ruff", id="renamed"),
    ],
)
def test_expose(tool_with_binary, rich_console, mapping, expected_key):
    args = argparse.Namespace(mapping=mapping, environment="ruff")
    result = execute_expose(args, console=rich_console)
    assert result == 0
    assert "Exposed" in rich_console.file.getvalue()

    loaded = Manifest(tool_with_binary / "manifest.toml").load()
    assert expected_key in loaded["ruff"].exposed


def test_expose_nonexistent_tool(mock_conda_home, rich_console):
    args = argparse.Namespace(mapping="gh", environment="nonexistent")
    with pytest.raises(ToolNotFoundError):
        execute_expose(args, console=rich_console)


def test_hide_binary(tool_with_binary, rich_console):
    manifest = Manifest(tool_with_binary / "manifest.toml")
    tool = manifest.load()["ruff"]
    tool.exposed["ruff"] = "ruff"
    manifest.save(manifest.load() | {"ruff": tool})

    trampoline = tool_with_binary / "bin" / "ruff"
    trampoline.touch()

    result = execute_hide(
        argparse.Namespace(name="ruff", environment="ruff"),
        console=rich_console,
    )
    assert result == 0
    assert "Hidden" in rich_console.file.getvalue()
