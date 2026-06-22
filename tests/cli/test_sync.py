"""Tests for ``conda global sync``."""

from __future__ import annotations

import argparse
import stat

from conda.common.path import BIN_DIRECTORY

from conda_global.cli.sync import execute_sync


def test_sync_empty_manifest(mock_conda_home, rich_console):
    args = argparse.Namespace()
    result = execute_sync(args, console=rich_console)
    assert result == 0
    assert "Nothing to sync" in rich_console.file.getvalue()


def test_sync_installs_missing_env(
    mock_conda_home,
    mock_trampoline,
    fake_envs_create,
    seeded_manifest,
    rich_console,
):
    seeded_manifest("gh", exposed={"gh": "gh"})

    args = argparse.Namespace()
    result = execute_sync(args, console=rich_console)
    assert result == 0

    output = rich_console.file.getvalue()
    assert "Syncing" in output
    assert "Synced 1 tool" in output

    assert len(fake_envs_create) == 1
    assert fake_envs_create[0]["name"] == "gh"


def test_sync_skips_existing_env(
    mock_conda_home,
    mock_trampoline,
    fake_envs_create,
    seeded_manifest,
    rich_console,
    monkeypatch,
):
    monkeypatch.setattr("conda_global.binaries.on_win", False)

    seeded_manifest("gh", exposed={"gh": "gh"})

    env_dir = mock_conda_home / "envs" / "gh"
    env_dir.mkdir(parents=True)
    (env_dir / "conda-meta").mkdir()
    bin_dir = env_dir / BIN_DIRECTORY
    bin_dir.mkdir()
    binary = bin_dir / "gh"
    binary.write_bytes(b"#!/bin/sh\n")
    binary.chmod(binary.stat().st_mode | stat.S_IXUSR)

    args = argparse.Namespace()
    result = execute_sync(args, console=rich_console)
    assert result == 0

    assert len(fake_envs_create) == 0

    assert (mock_conda_home / "bin" / "gh").exists()


def test_sync_multiple_tools(
    mock_conda_home,
    mock_trampoline,
    fake_envs_create,
    seeded_manifest,
    rich_console,
):
    seeded_manifest("gh", exposed={"gh": "gh"})
    seeded_manifest("ruff", exposed={"ruff": "ruff"})

    args = argparse.Namespace()
    result = execute_sync(args, console=rich_console)
    assert result == 0

    assert "Synced 2 tools" in rich_console.file.getvalue()
