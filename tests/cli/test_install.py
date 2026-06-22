"""Tests for ``conda global install``."""

from __future__ import annotations

import argparse
import stat
from types import SimpleNamespace

import pytest
from conda.base.constants import on_win
from conda.common.path import BIN_DIRECTORY

from conda_global.cli.install import execute_install
from conda_global.exceptions import BinaryNotFoundError, ToolExistsError
from conda_global.manifest import Manifest


def _install_args(
    package="gh",
    environment=None,
    channel=None,
    expose=None,
    force=False,
):
    return argparse.Namespace(
        package=package,
        environment=environment,
        channel=channel,
        expose=expose,
        force=force,
    )


def test_install_basic(
    mock_conda_home,
    mock_trampoline,
    fake_envs_create,
    rich_console,
):
    result = execute_install(_install_args(), console=rich_console)
    assert result == 0

    output = rich_console.file.getvalue()
    assert "Installing" in output
    assert "Installed" in output

    tools = Manifest(mock_conda_home / "manifest.toml").load()
    assert "gh" in tools
    assert tools["gh"].dependencies == {"gh": "*"}
    assert "gh" in tools["gh"].exposed

    assert len(fake_envs_create) == 1
    assert fake_envs_create[0]["name"] == "gh"
    assert fake_envs_create[0]["packages"] == ["gh"]


def test_install_custom_env_name(
    mock_conda_home,
    mock_trampoline,
    fake_envs_create,
    rich_console,
):
    result = execute_install(
        _install_args(package="gh", environment="github-cli"),
        console=rich_console,
    )
    assert result == 0

    tools = Manifest(mock_conda_home / "manifest.toml").load()
    assert "github-cli" in tools
    assert fake_envs_create[0]["name"] == "github-cli"


def test_install_custom_channel(
    mock_conda_home,
    mock_trampoline,
    fake_envs_create,
    rich_console,
    monkeypatch,
):
    monkeypatch.setattr(
        "conda_global.cli.install.context",
        SimpleNamespace(channels=["nvidia", "conda-forge"]),
    )

    result = execute_install(
        _install_args(channel=["nvidia", "conda-forge"]),
        console=rich_console,
    )
    assert result == 0

    tools = Manifest(mock_conda_home / "manifest.toml").load()
    assert tools["gh"].channels == ["nvidia", "conda-forge"]


def test_install_uses_configured_channels_when_omitted(
    mock_conda_home,
    mock_trampoline,
    fake_envs_create,
    rich_console,
    monkeypatch,
):
    configured = ["https://repo.anaconda.com/pkgs/main"]
    monkeypatch.setattr(
        "conda_global.cli.install.context",
        SimpleNamespace(channels=configured),
    )

    result = execute_install(_install_args(), console=rich_console)

    assert result == 0
    assert fake_envs_create[0]["channels"] == configured
    tools = Manifest(mock_conda_home / "manifest.toml").load()
    assert tools["gh"].channels == configured


def test_install_uses_resolved_context_channels(
    mock_conda_home,
    mock_trampoline,
    fake_envs_create,
    rich_console,
    monkeypatch,
):
    monkeypatch.setattr(
        "conda_global.cli.install.context",
        SimpleNamespace(channels=["local", "nvidia"]),
    )

    result = execute_install(
        _install_args(channel=["nvidia"]),
        console=rich_console,
    )

    assert result == 0
    assert fake_envs_create[0]["channels"] == ["local", "nvidia"]


def test_install_exposes_package_owned_binaries(
    mock_conda_home,
    mock_trampoline,
    rich_console,
    monkeypatch,
):
    suffix = ".exe" if on_win else ""

    class FakeRecord:
        files = [
            f"{BIN_DIRECTORY}/http{suffix}",
            f"{BIN_DIRECTORY}/httpie{suffix}",
            f"{BIN_DIRECTORY}/https{suffix}",
        ]

    class FakePrefixData:
        def __init__(self, prefix):
            self.prefix = prefix

        def get(self, package, default=None):
            return FakeRecord()

    def fake_create(self, name, packages, channels=None):
        prefix = mock_conda_home / "envs" / name
        bin_dir = prefix / BIN_DIRECTORY
        bin_dir.mkdir(parents=True)
        (prefix / "conda-meta").mkdir()
        for binary_name in ("http", "httpie", "https", "python"):
            binary = bin_dir / f"{binary_name}{suffix}"
            binary.write_bytes(b"#!/bin/sh\n")
            if not on_win:
                binary.chmod(binary.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
        return prefix

    monkeypatch.setattr("conda_global.envs.EnvironmentManager.create", fake_create)
    monkeypatch.setattr("conda_global.binaries.PrefixData", FakePrefixData)

    result = execute_install(_install_args(package="httpie"), console=rich_console)

    assert result == 0
    tools = Manifest(mock_conda_home / "manifest.toml").load()
    assert tools["httpie"].exposed == {
        "http": "http",
        "httpie": "httpie",
        "https": "https",
    }


def test_install_falls_back_to_first_discovered_binary(
    mock_conda_home,
    mock_trampoline,
    rich_console,
    monkeypatch,
):
    suffix = ".exe" if on_win else ""

    def fake_create(self, name, packages, channels=None):
        prefix = mock_conda_home / "envs" / name
        bin_dir = prefix / BIN_DIRECTORY
        bin_dir.mkdir(parents=True)
        (prefix / "conda-meta").mkdir()
        binary = bin_dir / f"python-foo-helper{suffix}"
        binary.write_bytes(b"#!/bin/sh\n")
        if not on_win:
            binary.chmod(binary.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
        return prefix

    monkeypatch.setattr("conda_global.envs.EnvironmentManager.create", fake_create)

    result = execute_install(_install_args(package="python-foo"), console=rich_console)

    assert result == 0
    tools = Manifest(mock_conda_home / "manifest.toml").load()
    assert tools["python-foo"].exposed == {
        "python-foo-helper": "python-foo-helper",
    }


def test_install_without_binaries_records_tool(
    mock_conda_home,
    mock_trampoline,
    rich_console,
    monkeypatch,
):
    def fake_create(self, name, packages, channels=None):
        prefix = mock_conda_home / "envs" / name
        (prefix / BIN_DIRECTORY).mkdir(parents=True)
        (prefix / "conda-meta").mkdir()
        return prefix

    monkeypatch.setattr("conda_global.envs.EnvironmentManager.create", fake_create)

    result = execute_install(_install_args(package="library-only"), console=rich_console)

    assert result == 0
    tools = Manifest(mock_conda_home / "manifest.toml").load()
    assert tools["library-only"].exposed == {}
    assert "Commands now available" not in rich_console.file.getvalue()


@pytest.mark.parametrize(
    "expose_arg,expected_exposed",
    [
        pytest.param(["gh"], {"gh": "gh"}, id="simple"),
        pytest.param(["github=gh"], {"github": "gh"}, id="renamed"),
    ],
)
def test_install_expose(
    mock_conda_home,
    mock_trampoline,
    fake_envs_create,
    rich_console,
    expose_arg,
    expected_exposed,
):
    result = execute_install(
        _install_args(expose=expose_arg),
        console=rich_console,
    )
    assert result == 0

    tools = Manifest(mock_conda_home / "manifest.toml").load()
    assert tools["gh"].exposed == expected_exposed
    assert "Commands now available" in rich_console.file.getvalue()


def test_install_expose_missing_binary_raises(
    mock_trampoline,
    fake_envs_create,
    rich_console,
):
    with pytest.raises(BinaryNotFoundError):
        execute_install(_install_args(expose=["missing"]), console=rich_console)


@pytest.mark.parametrize(
    "force,expect_error",
    [
        pytest.param(False, True, id="rejects-existing"),
        pytest.param(True, False, id="force-overwrites"),
    ],
)
def test_install_existing_env(
    mock_conda_home,
    mock_trampoline,
    fake_envs_create,
    rich_console,
    force,
    expect_error,
):
    env_dir = mock_conda_home / "envs" / "gh"
    env_dir.mkdir(parents=True)
    (env_dir / "conda-meta").mkdir()

    if expect_error:
        with pytest.raises(ToolExistsError):
            execute_install(_install_args(force=force), console=rich_console)
    else:
        result = execute_install(_install_args(force=force), console=rich_console)
        assert result == 0
        assert len(fake_envs_create) == 1
