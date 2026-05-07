"""Tests for path helpers."""

from __future__ import annotations

from pathlib import Path

import pytest

from conda_global import paths


@pytest.mark.parametrize(
    "func,expected_suffix",
    [
        (paths.global_envs_dir, "envs"),
        (paths.global_bin_dir, "bin"),
        (paths.trampoline_config_dir, "bin/trampoline"),
        (paths.trampoline_master_path, "bin/trampoline/_cg_trampoline"),
    ],
)
def test_path_helpers(func, expected_suffix, monkeypatch, tmp_path):
    data = tmp_path / "conda-global"
    monkeypatch.setattr("conda_global.paths.data_dir", lambda: data)
    assert func() == data / expected_suffix


def test_manifest_path_default(monkeypatch, tmp_path):
    data = tmp_path / "conda-global"
    data.mkdir()
    monkeypatch.setattr("conda_global.paths.data_dir", lambda: data)
    assert paths.manifest_path() == data / "manifest.toml"


@pytest.mark.parametrize(
    "legacy_exists,expected_suffix",
    [
        pytest.param(False, ".conda/global", id="fresh-install"),
        pytest.param(True, ".cg", id="legacy-exists"),
    ],
)
def test_data_dir_default(monkeypatch, tmp_path, legacy_exists, expected_suffix):
    home = tmp_path / "home"
    home.mkdir()
    if legacy_exists:
        (home / ".cg").mkdir()
    monkeypatch.delenv("CONDA_GLOBAL_HOME", raising=False)
    monkeypatch.setattr(Path, "home", staticmethod(lambda: home))
    assert paths.data_dir() == home / expected_suffix


def test_data_dir_respects_env_var(monkeypatch, tmp_path):
    monkeypatch.setenv("CONDA_GLOBAL_HOME", str(tmp_path / "custom"))
    assert paths.data_dir() == tmp_path / "custom"
    assert paths.global_envs_dir() == tmp_path / "custom" / "envs"
    assert paths.manifest_path() == tmp_path / "custom" / "manifest.toml"


def test_data_dir_env_var_tilde_expansion(monkeypatch):
    monkeypatch.setenv("CONDA_GLOBAL_HOME", "~/my-conda")
    assert paths.data_dir() == Path.home() / "my-conda"


def test_data_dir_env_var_empty_falls_through(monkeypatch, tmp_path):
    home = tmp_path / "home"
    home.mkdir()
    monkeypatch.setenv("CONDA_GLOBAL_HOME", "")
    monkeypatch.setattr(Path, "home", staticmethod(lambda: home))
    assert paths.data_dir() == home / ".conda" / "global"


def test_legacy_data_dir():
    assert paths._legacy_data_dir() == Path.home() / ".cg"
