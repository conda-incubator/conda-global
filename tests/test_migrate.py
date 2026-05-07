"""Tests for data directory migration."""

from __future__ import annotations

from pathlib import Path

import pytest

from conda_global.migrate import (
    MigrationStatus,
    find_legacy_manifest,
    migrate_data_dir,
    remove_legacy_dir,
)


@pytest.fixture
def fake_home(tmp_path, monkeypatch):
    """Redirect Path.home() and legacy_data_dir to tmp_path-based dirs."""
    home = tmp_path / "home"
    home.mkdir()
    legacy = home / ".cg"
    new = home / ".conda" / "global"
    manifest = home / ".conda" / "global.toml"
    monkeypatch.setattr(Path, "home", staticmethod(lambda: home))
    monkeypatch.setattr("conda_global.migrate.legacy_data_dir", lambda: legacy)
    return {"home": home, "legacy": legacy, "new": new, "manifest": manifest}


@pytest.mark.parametrize(
    "setup,expected_status",
    [
        pytest.param("legacy_only", MigrationStatus.MIGRATED, id="migrates"),
        pytest.param("both_exist", MigrationStatus.SKIPPED, id="skips-both-exist"),
        pytest.param("neither", MigrationStatus.NOT_NEEDED, id="not-needed"),
        pytest.param("new_only", MigrationStatus.NOT_NEEDED, id="new-only"),
    ],
)
def test_migrate_data_dir(fake_home, setup, expected_status):
    legacy = fake_home["legacy"]
    new = fake_home["new"]

    if setup == "legacy_only":
        legacy.mkdir(parents=True)
        (legacy / "global.toml").write_text("[envs.gh]\n")
    elif setup == "both_exist":
        legacy.mkdir(parents=True)
        new.mkdir(parents=True)
    elif setup == "new_only":
        new.mkdir(parents=True)

    result = migrate_data_dir()
    assert result == expected_status

    if expected_status == MigrationStatus.MIGRATED:
        assert new.exists()
        assert fake_home["manifest"].read_text() == "[envs.gh]\n"


def test_migrate_copies_manifest_toml_name(fake_home):
    """If legacy already uses manifest.toml, it's copied to ~/.conda/global.toml."""
    legacy = fake_home["legacy"]
    legacy.mkdir(parents=True)
    (legacy / "manifest.toml").write_text("[envs.ruff]\n")

    result = migrate_data_dir()
    assert result == MigrationStatus.MIGRATED
    assert fake_home["manifest"].read_text() == "[envs.ruff]\n"


@pytest.mark.parametrize(
    "filename",
    [
        pytest.param("manifest.toml", id="new-name"),
        pytest.param("global.toml", id="old-name"),
    ],
)
def test_find_legacy_manifest(tmp_path, monkeypatch, filename):
    legacy = tmp_path / ".cg"
    legacy.mkdir()
    (legacy / filename).write_text("[envs]")
    monkeypatch.setattr("conda_global.migrate.legacy_data_dir", lambda: legacy)

    assert find_legacy_manifest() == legacy / filename


def test_find_legacy_manifest_missing(tmp_path, monkeypatch):
    monkeypatch.setattr("conda_global.migrate.legacy_data_dir", lambda: tmp_path / "nope")
    assert find_legacy_manifest() is None


def test_remove_legacy_dir(tmp_path, monkeypatch):
    legacy = tmp_path / ".cg"
    legacy.mkdir()
    (legacy / "envs").mkdir()
    (legacy / "envs" / "gh").mkdir()
    monkeypatch.setattr("conda_global.migrate.legacy_data_dir", lambda: legacy)

    remove_legacy_dir()
    assert not legacy.exists()


def test_remove_legacy_dir_noop_when_missing(tmp_path, monkeypatch):
    monkeypatch.setattr("conda_global.migrate.legacy_data_dir", lambda: tmp_path / "nope")
    remove_legacy_dir()
