"""Shared test fixtures for conda-global."""

from __future__ import annotations

from io import StringIO

import pytest
from rich.console import Console


@pytest.fixture
def rich_console() -> Console:
    """A Rich console that captures output for testing."""
    return Console(
        file=StringIO(),
        width=120,
        force_terminal=True,
        highlight=False,
    )


@pytest.fixture
def mock_conda_home(tmp_path, monkeypatch):
    """Mock the data directory and manifest path to a temporary path.

    CLI handlers construct ``Manifest()``, ``EnvironmentManager()``, and
    ``TrampolineManager()`` with default paths, so we patch the path
    functions they fall back to.
    """
    data = tmp_path / "conda-global"
    data.mkdir()
    manifest = data / "manifest.toml"
    _manifest_fn = lambda: manifest  # noqa: E731
    monkeypatch.setattr("conda_global.paths.data_dir", lambda: data)
    monkeypatch.setattr("conda_global.paths.manifest_path", _manifest_fn)
    monkeypatch.setattr("conda_global.manifest._default_manifest_path", _manifest_fn)
    monkeypatch.setattr("conda_global.cli.edit.manifest_path", _manifest_fn)
    return data
