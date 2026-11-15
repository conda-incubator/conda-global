"""Tests for ``conda global ensurepath``."""

from __future__ import annotations

import argparse

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
