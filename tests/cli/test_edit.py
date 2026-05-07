"""Tests for ``conda global edit``."""

from __future__ import annotations

import argparse

import pytest

from conda_global.cli.edit import execute_edit


@pytest.fixture
def fake_editor(fake_subprocess_run, monkeypatch):
    """Patch subprocess.run for the edit module."""
    recorded, set_rc, run_fn = fake_subprocess_run
    monkeypatch.setattr("conda_global.cli.edit.subprocess.run", run_fn)
    return recorded, set_rc


@pytest.mark.parametrize(
    "visual,editor,expected_cmd",
    [
        pytest.param(None, "nano", "nano", id="editor-only"),
        pytest.param("code", "nano", "code", id="visual-preferred"),
        pytest.param(None, None, "vi", id="default-vi"),
    ],
)
def test_edit_selects_editor(
    mock_conda_home,
    rich_console,
    monkeypatch,
    fake_editor,
    visual,
    editor,
    expected_cmd,
):
    recorded, _ = fake_editor
    if visual:
        monkeypatch.setenv("VISUAL", visual)
    else:
        monkeypatch.delenv("VISUAL", raising=False)
    if editor:
        monkeypatch.setenv("EDITOR", editor)
    else:
        monkeypatch.delenv("EDITOR", raising=False)

    execute_edit(argparse.Namespace(), console=rich_console)

    assert recorded[0][0] == expected_cmd
    assert "manifest.toml" in recorded[0][1]


def test_edit_creates_file_if_missing(
    mock_conda_home,
    rich_console,
    monkeypatch,
    fake_editor,
):
    monkeypatch.setenv("EDITOR", "vi")
    monkeypatch.delenv("VISUAL", raising=False)

    execute_edit(argparse.Namespace(), console=rich_console)

    assert (mock_conda_home / "manifest.toml").exists()


def test_edit_returns_editor_exit_code(
    mock_conda_home,
    rich_console,
    monkeypatch,
    fake_editor,
):
    _, set_rc = fake_editor
    set_rc(1)
    monkeypatch.setenv("EDITOR", "vi")
    monkeypatch.delenv("VISUAL", raising=False)

    assert execute_edit(argparse.Namespace(), console=rich_console) == 1
