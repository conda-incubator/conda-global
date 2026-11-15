"""Tests for ``conda global ensurepath``."""

from __future__ import annotations

import argparse
import sys
from unittest.mock import patch

import pytest

from conda_global.cli.ensurepath import execute_ensurepath


@pytest.mark.parametrize(
    "in_path,needs_restart,append_ok,expected_rc,expected_text",
    [
        pytest.param(True, False, False, 0, "already on your PATH", id="already-in-path"),
        pytest.param(False, True, False, 0, "already configured", id="needs-restart"),
        pytest.param(False, False, True, 0, "Added", id="appended"),
        pytest.param(False, False, False, 1, "could not add", id="append-failed"),
    ],
)
def test_ensurepath(
    mock_conda_home,
    rich_console,
    monkeypatch,
    in_path,
    needs_restart,
    append_ok,
    expected_rc,
    expected_text,
):
    monkeypatch.setattr("userpath.in_current_path", lambda _, **__: in_path)
    monkeypatch.setattr("userpath.need_shell_restart", lambda _, **__: needs_restart)
    monkeypatch.setattr("userpath.append", lambda loc, app, **__: append_ok)

    result = execute_ensurepath(argparse.Namespace(), console=rich_console)
    assert result == expected_rc
    assert expected_text in rich_console.file.getvalue()


def _mock_userpath(monkeypatch):
    """Mock userpath functions to return False so we reach shell detection."""
    monkeypatch.setattr("userpath.in_current_path", lambda _, **__: False)
    monkeypatch.setattr("userpath.need_shell_restart", lambda _, **__: False)
    monkeypatch.setattr("userpath.append", lambda loc, app, shells=None, **__: True)


@pytest.mark.parametrize(
    "shell_name,env_var,env_value",
    [
        pytest.param("fish", "FISH_VERSION", "3.6.0", id="fish"),
        pytest.param("zsh", "ZSH_VERSION", "5.9", id="zsh"),
        pytest.param("bash", "BASH_VERSION", "5.2.15", id="bash"),
        pytest.param("xonsh", "XONSH_VERSION", "0.13.0", id="xonsh"),
    ],
)
@pytest.mark.skipif(sys.platform == "win32", reason="Unix shell detection")
def test_shell_via_env_var(
    mock_conda_home, rich_console, monkeypatch, shell_name, env_var, env_value
):
    """Shell detected via environment variable."""
    _mock_userpath(monkeypatch)
    monkeypatch.setattr(
        "os.environ.get", lambda key, default=None: env_value if key == env_var else default
    )

    result = execute_ensurepath(argparse.Namespace(), console=rich_console)
    assert result == 0


@pytest.mark.parametrize(
    "shell_name,config_path",
    [
        pytest.param("fish", "~/.config/fish/config.fish", id="fish"),
        pytest.param("zsh", "~/.zshrc", id="zsh"),
        pytest.param("bash", "~/.bashrc", id="bash-bashrc"),
        pytest.param("bash", "~/.bash_profile", id="bash-bash_profile"),
        pytest.param("xonsh", "~/.xonshrc", id="xonsh"),
    ],
)
@pytest.mark.skipif(sys.platform == "win32", reason="Unix shell detection")
def test_shell_via_config_file(
    mock_conda_home, rich_console, monkeypatch, shell_name, config_path
):
    """Shell detected via config file."""
    _mock_userpath(monkeypatch)
    monkeypatch.setattr("os.environ.get", lambda key, default=None: default)
    with patch("pathlib.Path.expanduser") as mock_expanduser:
        mock_expanduser.return_value.exists.return_value = True
        result = execute_ensurepath(argparse.Namespace(), console=rich_console)
    assert result == 0


@pytest.mark.skipif(sys.platform == "win32", reason="Unix shell detection")
def test_fallback_to_bash(mock_conda_home, rich_console, monkeypatch):
    """Fallback to bash when no shells detected."""
    _mock_userpath(monkeypatch)
    monkeypatch.setattr("os.environ.get", lambda key, default=None: default)
    with patch("pathlib.Path.expanduser") as mock_expanduser:
        mock_expanduser.return_value.exists.return_value = False
        result = execute_ensurepath(argparse.Namespace(), console=rich_console)
    assert result == 0


def test_explicit_shell_arg_bypasses_detection(mock_conda_home, rich_console, monkeypatch):
    """Explicit --shell argument bypasses auto-detection."""
    _mock_userpath(monkeypatch)
    args = argparse.Namespace(shell=["fish", "zsh"])
    result = execute_ensurepath(args, console=rich_console)
    assert result == 0


@pytest.mark.parametrize(
    "shell_list",
    [
        pytest.param(["fish"], id="single"),
        pytest.param(["bash", "zsh", "fish"], id="multiple"),
        pytest.param([], id="empty"),
    ],
)
def test_shell_arg(mock_conda_home, rich_console, monkeypatch, shell_list):
    """Test --shell argument handling."""
    _mock_userpath(monkeypatch)
    args = argparse.Namespace(shell=shell_list)
    if not shell_list:
        monkeypatch.setattr("os.environ.get", lambda key, default=None: default)
        with patch("pathlib.Path.expanduser") as mock_expanduser:
            mock_expanduser.return_value.exists.return_value = False
            result = execute_ensurepath(args, console=rich_console)
    else:
        result = execute_ensurepath(args, console=rich_console)
    assert result == 0
