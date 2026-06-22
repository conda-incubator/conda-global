"""Tests for ``conda global install``."""

from __future__ import annotations

import argparse
from types import SimpleNamespace

import pytest

from conda_global.cli.install import execute_install
from conda_global.exceptions import ToolExistsError
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
