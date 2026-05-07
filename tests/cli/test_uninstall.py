"""Tests for ``conda global uninstall``."""

from __future__ import annotations

import argparse

import pytest

from conda_global.cli.uninstall import execute_uninstall
from conda_global.exceptions import ToolNotFoundError
from conda_global.manifest import Manifest


def test_uninstall_removes_env_and_manifest(
    mock_conda_home,
    mock_trampoline,
    seeded_manifest,
    rich_console,
    monkeypatch,
):
    monkeypatch.setattr("conda_trampoline._ON_WIN", False)

    seeded_manifest("gh", exposed={"gh": "gh"})

    env_dir = mock_conda_home / "envs" / "gh"
    env_dir.mkdir(parents=True)
    (env_dir / "conda-meta").mkdir()

    trampoline = mock_conda_home / "bin" / "gh"
    trampoline.write_bytes(b"fake")

    result = execute_uninstall(
        argparse.Namespace(environment="gh"),
        console=rich_console,
    )
    assert result == 0

    output = rich_console.file.getvalue()
    assert "Uninstalling" in output
    assert "Uninstalled" in output

    assert "gh" not in Manifest(mock_conda_home / "manifest.toml").load()
    assert not env_dir.exists()
    assert not trampoline.exists()


def test_uninstall_removes_multiple_trampolines(
    mock_conda_home,
    mock_trampoline,
    seeded_manifest,
    rich_console,
    monkeypatch,
):
    monkeypatch.setattr("conda_trampoline._ON_WIN", False)

    seeded_manifest("ruff", exposed={"ruff": "ruff", "ruff-format": "ruff"})

    env_dir = mock_conda_home / "envs" / "ruff"
    env_dir.mkdir(parents=True)
    (env_dir / "conda-meta").mkdir()

    for name in ("ruff", "ruff-format"):
        t = mock_conda_home / "bin" / name
        t.write_bytes(b"fake")

    result = execute_uninstall(
        argparse.Namespace(environment="ruff"),
        console=rich_console,
    )
    assert result == 0
    assert not (mock_conda_home / "bin" / "ruff").exists()
    assert not (mock_conda_home / "bin" / "ruff-format").exists()


def test_uninstall_nonexistent_tool(mock_conda_home, rich_console):
    with pytest.raises(ToolNotFoundError):
        execute_uninstall(
            argparse.Namespace(environment="nonexistent"),
            console=rich_console,
        )
