"""Shared fixtures for CLI tests."""

from __future__ import annotations

import shutil
import stat

import pytest
from conda.common.path import BIN_DIRECTORY

from conda_global.manifest import Manifest
from conda_global.models import ToolEnv


@pytest.fixture
def mock_trampoline(mock_conda_home):
    """Set up a fake master trampoline binary in mock_conda_home."""
    trampoline_dir = mock_conda_home / "bin" / "trampoline"
    trampoline_dir.mkdir(parents=True)
    master = trampoline_dir / "_cg_trampoline"
    master.write_bytes(b"fake trampoline")
    return mock_conda_home


@pytest.fixture
def fake_envs_create(mock_conda_home, monkeypatch):
    """Replace EnvironmentManager.create with a fake that builds a prefix.

    Creates the prefix dir with a ``conda-meta/`` and a single executable
    binary matching the first package name. Returns a list of recorded
    calls for assertions.
    """
    for mod in (
        "conda.base.constants",
        "conda_global.binaries",
        "conda_global.cli.install",
    ):
        monkeypatch.setattr(f"{mod}.on_win", False)
    monkeypatch.setattr("conda_trampoline._ON_WIN", False)
    monkeypatch.setattr("conda_global.binaries._is_executable", lambda path: True)

    calls: list[dict] = []
    envs_dir = mock_conda_home / "envs"
    envs_dir.mkdir(exist_ok=True)

    def _fake_create(self, name, packages, channels=None):
        prefix = envs_dir / name
        prefix.mkdir(parents=True, exist_ok=True)
        (prefix / "conda-meta").mkdir(exist_ok=True)
        bin_dir = prefix / BIN_DIRECTORY
        bin_dir.mkdir(exist_ok=True)
        for pkg in packages:
            pkg_name = pkg.split(">")[0].split("<")[0].split("=")[0]
            binary = bin_dir / pkg_name
            binary.write_bytes(b"#!/bin/sh\n")
            binary.chmod(binary.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
        calls.append({"name": name, "packages": packages, "channels": channels})
        return prefix

    def _fake_remove(self, name):
        prefix = envs_dir / name
        if prefix.exists():
            shutil.rmtree(prefix)

    monkeypatch.setattr(
        "conda_global.envs.EnvironmentManager.create",
        _fake_create,
    )
    monkeypatch.setattr(
        "conda_global.envs.EnvironmentManager.remove",
        _fake_remove,
    )
    return calls


@pytest.fixture
def fake_subprocess_run(monkeypatch):
    """Return a fake subprocess.run implementation and captured calls."""
    recorded: list[list[str]] = []
    rc = [0]

    def _run(cmd, **kwargs):
        recorded.append(cmd)

        class FakeResult:
            returncode = rc[0]

        return FakeResult()

    def _set_rc(code):
        rc[0] = code

    return recorded, _set_rc, _run


@pytest.fixture
def seeded_manifest(mock_conda_home):
    """Return a helper that seeds the manifest with a ToolEnv."""
    manifest = Manifest(mock_conda_home / "manifest.toml")

    def _seed(
        name: str = "gh",
        dependencies: dict[str, str] | None = None,
        exposed: dict[str, str] | None = None,
        channels: list[str] | None = None,
        pinned: bool = False,
    ) -> ToolEnv:
        tool = ToolEnv(
            name=name,
            channels=channels or [],
            dependencies=dependencies or {name: "*"},
            exposed=exposed or {},
            pinned=pinned,
        )
        manifest.add(tool)
        return tool

    return _seed
