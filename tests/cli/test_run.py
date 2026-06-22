"""Tests for ``conda global run``."""

from __future__ import annotations

import argparse
from types import SimpleNamespace

import pytest

from conda_global.cli.run import execute_run
from conda_global.exceptions import BinaryNotFoundError


def _run_args(
    package="gh",
    channel=None,
    args=None,
):
    return argparse.Namespace(
        package=package,
        channel=channel,
        args=args,
    )


@pytest.fixture
def fake_subprocess(fake_subprocess_run, monkeypatch):
    """Patch subprocess.run for the run module."""
    recorded, set_rc, run_fn = fake_subprocess_run
    monkeypatch.setattr("conda_global.cli.run.subprocess.run", run_fn)
    return recorded, set_rc


def test_run_executes_and_cleans_up(
    mock_conda_home,
    fake_envs_create,
    rich_console,
    fake_subprocess,
):
    recorded, _ = fake_subprocess

    result = execute_run(_run_args(), console=rich_console)
    assert result == 0
    assert len(recorded) == 1
    assert "gh" in recorded[0][0]
    assert not (mock_conda_home / "envs" / "_cg_run_gh").exists()
    assert "Running" in rich_console.file.getvalue()


@pytest.mark.parametrize(
    "input_args,expected_tail",
    [
        pytest.param(["--version"], ["--version"], id="plain-args"),
        pytest.param(["--", "--help"], ["--help"], id="strips-double-dash"),
        pytest.param(
            ["-v", "--format=json"],
            ["-v", "--format=json"],
            id="multiple-args",
        ),
    ],
)
def test_run_forwards_args(
    mock_conda_home,
    fake_envs_create,
    rich_console,
    fake_subprocess,
    input_args,
    expected_tail,
):
    recorded, _ = fake_subprocess
    execute_run(_run_args(args=input_args), console=rich_console)
    assert recorded[0][1:] == expected_tail


def test_run_returns_subprocess_exit_code(
    mock_conda_home,
    fake_envs_create,
    rich_console,
    fake_subprocess,
):
    _, set_rc = fake_subprocess
    set_rc(42)
    assert execute_run(_run_args(), console=rich_console) == 42


def test_run_binary_not_found(
    mock_conda_home,
    fake_envs_create,
    monkeypatch,
):
    monkeypatch.setattr(
        "conda_global.cli.run.find_binary",
        lambda prefix, name: None,
    )

    with pytest.raises(BinaryNotFoundError):
        execute_run(_run_args(package="missing"))

    assert not (mock_conda_home / "envs" / "_cg_run_missing").exists()


def test_run_custom_channel(
    mock_conda_home,
    fake_envs_create,
    rich_console,
    fake_subprocess,
    monkeypatch,
):
    monkeypatch.setattr(
        "conda_global.cli.run.context",
        SimpleNamespace(channels=["bioconda", "conda-forge"]),
    )

    execute_run(
        _run_args(channel=["bioconda", "conda-forge"]),
        console=rich_console,
    )
    assert fake_envs_create[0]["channels"] == ["bioconda", "conda-forge"]


def test_run_uses_configured_channels_when_omitted(
    mock_conda_home,
    fake_envs_create,
    rich_console,
    fake_subprocess,
    monkeypatch,
):
    configured = ["https://repo.anaconda.com/pkgs/main"]
    monkeypatch.setattr(
        "conda_global.cli.run.context",
        SimpleNamespace(channels=configured),
    )

    assert execute_run(_run_args(), console=rich_console) == 0
    assert fake_envs_create[0]["channels"] == configured


def test_run_uses_resolved_context_channels(
    mock_conda_home,
    fake_envs_create,
    rich_console,
    fake_subprocess,
    monkeypatch,
):
    monkeypatch.setattr(
        "conda_global.cli.run.context",
        SimpleNamespace(channels=["local", "bioconda"]),
    )

    result = execute_run(
        _run_args(channel=["bioconda"]),
        console=rich_console,
    )

    assert result == 0
    assert fake_envs_create[0]["channels"] == ["local", "bioconda"]
