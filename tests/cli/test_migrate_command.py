"""Tests for ``conda global migrate`` CLI handler."""

from __future__ import annotations

import argparse
from pathlib import Path

import pytest
from rich.console import Console

from conda_global.cli.migrate import execute_migrate
from conda_global.migrate import MigrationStatus


@pytest.fixture
def migrate_args() -> argparse.Namespace:
    return argparse.Namespace(subcmd="migrate", force=False)


def test_execute_migrate_not_needed(monkeypatch, migrate_args, rich_console):
    monkeypatch.setattr(
        "conda_global.cli.migrate.migrate_data_dir",
        lambda **kw: MigrationStatus.NOT_NEEDED,
    )

    rc = execute_migrate(migrate_args, console=rich_console)
    assert rc == 0
    out = rich_console.file.getvalue()
    assert "Nothing to migrate" in out


def test_execute_migrate_skipped(monkeypatch, migrate_args, rich_console):
    monkeypatch.setattr(
        "conda_global.cli.migrate.migrate_data_dir",
        lambda **kw: MigrationStatus.SKIPPED,
    )

    rc = execute_migrate(migrate_args, console=rich_console)
    assert rc == 1
    assert "Skipped" in rich_console.file.getvalue()


def _path_fn(path: Path):
    def fn() -> Path:
        return path

    fn.cache_clear = lambda: None
    return fn


def test_execute_migrate_success_calls_sync_and_removes_legacy(
    monkeypatch, migrate_args, rich_console, tmp_path
):
    home = tmp_path / "home"
    home.mkdir()
    legacy = home / ".cg"
    legacy.mkdir()
    monkeypatch.setattr(Path, "home", staticmethod(lambda: home))
    monkeypatch.setattr("conda_global.cli.migrate.legacy_data_dir", lambda: legacy)

    monkeypatch.setattr(
        "conda_global.cli.migrate.migrate_data_dir",
        lambda **kw: MigrationStatus.MIGRATED,
    )

    sync_calls: list[tuple] = []

    def fake_sync(args, console=None):
        sync_calls.append((args, console))
        return 0

    monkeypatch.setattr("conda_global.cli.migrate.execute_sync", fake_sync)

    removed: list[bool] = []

    def fake_remove():
        removed.append(True)

    monkeypatch.setattr("conda_global.cli.migrate.remove_legacy_dir", fake_remove)

    monkeypatch.setattr(
        "conda_global.cli.migrate.data_dir",
        _path_fn(home / ".conda" / "global"),
    )
    monkeypatch.setattr(
        "conda_global.cli.migrate.manifest_path",
        _path_fn(home / ".conda" / "global.toml"),
    )

    rc = execute_migrate(migrate_args, console=rich_console)
    assert rc == 0
    assert len(sync_calls) == 1
    assert sync_calls[0][0] is migrate_args
    assert isinstance(sync_calls[0][1], Console)
    assert removed == [True]
    assert "Migrating" in rich_console.file.getvalue()
    assert "Migrated" in rich_console.file.getvalue()


def test_execute_migrate_sync_failure_preserves_legacy(
    monkeypatch, migrate_args, rich_console, tmp_path
):
    home = tmp_path / "home"
    home.mkdir()
    legacy = home / ".cg"
    legacy.mkdir()
    monkeypatch.setattr(Path, "home", staticmethod(lambda: home))
    monkeypatch.setattr("conda_global.cli.migrate.legacy_data_dir", lambda: legacy)

    monkeypatch.setattr(
        "conda_global.cli.migrate.migrate_data_dir",
        lambda **kw: MigrationStatus.MIGRATED,
    )
    monkeypatch.setattr(
        "conda_global.cli.migrate.execute_sync",
        lambda args, console=None: 2,
    )
    removed: list[bool] = []

    def fake_remove():
        removed.append(True)

    monkeypatch.setattr("conda_global.cli.migrate.remove_legacy_dir", fake_remove)

    monkeypatch.setattr(
        "conda_global.cli.migrate.data_dir",
        _path_fn(home / ".conda" / "global"),
    )
    monkeypatch.setattr(
        "conda_global.cli.migrate.manifest_path",
        _path_fn(home / ".conda" / "global.toml"),
    )

    rc = execute_migrate(migrate_args, console=rich_console)
    assert rc == 2
    assert removed == []
    assert "sync failed" in rich_console.file.getvalue()


def test_execute_migrate_passes_force_to_migrate_data_dir(monkeypatch, rich_console):
    calls: list[bool] = []

    def capture_force(*, force: bool = False):
        calls.append(force)
        return MigrationStatus.NOT_NEEDED

    monkeypatch.setattr("conda_global.cli.migrate.migrate_data_dir", capture_force)

    args_false = argparse.Namespace(subcmd="migrate", force=False)
    execute_migrate(args_false, console=rich_console)
    args_true = argparse.Namespace(subcmd="migrate", force=True)
    execute_migrate(args_true, console=rich_console)
    assert calls == [False, True]


def test_execute_migrate_uses_stderr_console_when_none(monkeypatch, migrate_args, capsys):
    monkeypatch.setattr(
        "conda_global.cli.migrate.migrate_data_dir",
        lambda **kw: MigrationStatus.NOT_NEEDED,
    )
    # Must not raise when console omitted
    rc = execute_migrate(migrate_args, console=None)
    assert rc == 0
    err = capsys.readouterr().err
    assert "Nothing to migrate" in err
