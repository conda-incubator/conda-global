"""Tests for path helpers."""

from __future__ import annotations

from pathlib import Path

import pytest

from conda_global import paths


@pytest.fixture(autouse=True)
def _clear_path_caches():
    """Clear lru_cache on path helpers between tests."""
    paths.data_dir.cache_clear()
    paths.manifest_path.cache_clear()
    yield
    paths.data_dir.cache_clear()
    paths.manifest_path.cache_clear()


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
    home = tmp_path / "home"
    home.mkdir()
    (home / ".conda").mkdir()
    monkeypatch.setattr(Path, "home", staticmethod(lambda: home))
    monkeypatch.setattr("conda_global.paths.data_dir", lambda: tmp_path / "data")
    assert paths.manifest_path() == home / ".conda" / "global.toml"


def test_manifest_path_prefers_home_global_toml(monkeypatch, tmp_path):
    """When ~/.conda/global.toml exists, use it (not sibling files under data_dir)."""
    home = tmp_path / "home"
    home.mkdir()
    (home / ".conda").mkdir(parents=True)
    manifest_file = home / ".conda" / "global.toml"
    manifest_file.write_text("[envs]\n")
    monkeypatch.setattr(Path, "home", staticmethod(lambda: home))
    data = tmp_path / "ignored-data"
    data.mkdir()
    (data / "manifest.toml").write_text("[other]\n")
    monkeypatch.setattr("conda_global.paths.data_dir", lambda: data)
    assert paths.manifest_path() == manifest_file


def test_manifest_path_manifest_toml_fallback_in_data_dir(monkeypatch, tmp_path):
    home = tmp_path / "home"
    home.mkdir()
    (home / ".conda").mkdir()
    data = tmp_path / "data"
    data.mkdir()
    (data / "global.toml").write_text("[envs]")
    monkeypatch.setattr(Path, "home", staticmethod(lambda: home))
    monkeypatch.setattr("conda_global.paths.data_dir", lambda: data)
    assert paths.manifest_path() == data / "global.toml"


def test_manifest_path_manifest_toml_name_in_data_dir(monkeypatch, tmp_path):
    home = tmp_path / "home"
    home.mkdir()
    (home / ".conda").mkdir()
    data = tmp_path / "data"
    data.mkdir()
    (data / "manifest.toml").write_text("[envs]")
    monkeypatch.setattr(Path, "home", staticmethod(lambda: home))
    monkeypatch.setattr("conda_global.paths.data_dir", lambda: data)
    assert paths.manifest_path() == data / "manifest.toml"


@pytest.mark.parametrize(
    "legacy_exists,manifest_exists,expected_suffix",
    [
        pytest.param(False, False, ".conda/global", id="fresh-install"),
        pytest.param(True, False, ".cg", id="legacy-not-migrated"),
        pytest.param(True, True, ".conda/global", id="legacy-migrated"),
        pytest.param(False, True, ".conda/global", id="new-with-manifest"),
    ],
)
def test_data_dir_default(monkeypatch, tmp_path, legacy_exists, manifest_exists, expected_suffix):
    home = tmp_path / "home"
    home.mkdir()
    if legacy_exists:
        (home / ".cg").mkdir()
    if manifest_exists:
        (home / ".conda").mkdir(parents=True, exist_ok=True)
        (home / ".conda" / "global.toml").write_text("[envs]\n")
    monkeypatch.delenv("CONDA_GLOBAL_HOME", raising=False)
    monkeypatch.setattr(Path, "home", staticmethod(lambda: home))
    assert paths.data_dir() == home / expected_suffix


def test_data_dir_respects_env_var(monkeypatch, tmp_path):
    monkeypatch.setenv("CONDA_GLOBAL_HOME", str(tmp_path / "custom"))
    assert paths.data_dir() == tmp_path / "custom"
    assert paths.global_envs_dir() == tmp_path / "custom" / "envs"


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
    assert paths.legacy_data_dir() == Path.home() / ".cg"
