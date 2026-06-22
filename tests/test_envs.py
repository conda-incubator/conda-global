"""Tests for environment management."""

from __future__ import annotations

from types import SimpleNamespace

import pytest

from conda_global.envs import EnvironmentManager


@pytest.mark.parametrize(
    "setup,expected",
    [
        pytest.param(None, False, id="dir-missing"),
        pytest.param("dir-only", False, id="dir-no-conda-meta"),
        pytest.param("with-conda-meta", True, id="dir-with-conda-meta"),
    ],
)
def test_exists(tmp_path, setup, expected):
    if setup == "dir-only":
        (tmp_path / "gh").mkdir()
    elif setup == "with-conda-meta":
        (tmp_path / "gh").mkdir()
        (tmp_path / "gh" / "conda-meta").mkdir()

    assert EnvironmentManager(tmp_path).exists("gh") is expected


def test_remove(tmp_path):
    env_dir = tmp_path / "gh"
    env_dir.mkdir()
    (env_dir / "conda-meta").mkdir()
    (env_dir / "conda-meta" / "history").write_text("test")

    envs = EnvironmentManager(tmp_path)
    assert envs.exists("gh")

    envs.remove("gh")
    assert not env_dir.exists()


def test_remove_nonexistent(tmp_path):
    EnvironmentManager(tmp_path).remove("nonexistent")


def test_create_uses_configured_channels_when_omitted(tmp_path, monkeypatch):
    received: dict[str, object] = {}

    class FakeTransaction:
        def download_and_extract(self):
            received["downloaded"] = True

        def execute(self):
            received["executed"] = True

    class FakeSolver:
        def __init__(self, prefix, channels, subdirs, *, specs_to_add):
            received["prefix"] = prefix
            received["channels"] = channels
            received["subdirs"] = subdirs
            received["specs"] = specs_to_add

        def solve_for_transaction(self):
            return FakeTransaction()

    monkeypatch.setattr("conda_global.envs.Channel", lambda channel: channel)
    monkeypatch.setattr("conda_global.envs.MatchSpec", lambda package: package)
    monkeypatch.setattr(
        "conda_global.envs.context",
        SimpleNamespace(
            channels=["https://repo.anaconda.com/pkgs/main"],
            plugin_manager=SimpleNamespace(
                get_cached_solver_backend=lambda name=None: FakeSolver,
            ),
            subdirs=["osx-arm64"],
        ),
    )

    prefix = EnvironmentManager(tmp_path).create("gh", ["gh"])

    assert prefix == tmp_path / "gh"
    assert received["channels"] == ["https://repo.anaconda.com/pkgs/main"]
    assert received["specs"] == ["gh"]
    assert received["downloaded"] is True
    assert received["executed"] is True
