"""Migration from legacy ~/.cg/ to ~/.conda/global/.

Migration is NOT automatic — existing installs continue using ~/.cg/
until the user explicitly runs ``conda global migrate``. The migrate
command copies the manifest to the new location and runs a fresh sync
(reinstall), avoiding issues with stale paths in conda-meta or
trampoline configs.
"""

from __future__ import annotations

import shutil
from enum import Enum
from pathlib import Path

from .paths import legacy_data_dir


class MigrationStatus(Enum):
    MIGRATED = "migrated"
    SKIPPED = "skipped"
    NOT_NEEDED = "not_needed"


def find_legacy_manifest() -> Path | None:
    """Find the manifest file in the legacy directory."""
    legacy = legacy_data_dir()
    if not legacy.is_dir():
        return None
    for name in ("manifest.toml", "global.toml"):
        candidate = legacy / name
        if candidate.is_file():
            return candidate
    return None


def migrate_data_dir(*, force: bool = False) -> MigrationStatus:
    """Migrate from ~/.cg/ to ~/.conda/global/ via reinstall.

    Copies the manifest to ``~/.conda/global.toml``, then the caller
    is responsible for running sync to reinstall all tools. After sync
    succeeds, the old directory can be removed.

    Returns the migration status:
    - MIGRATED: manifest copied, ready for sync + cleanup
    - SKIPPED: new directory already exists and force is False
    - NOT_NEEDED: legacy directory does not exist
    """
    legacy = legacy_data_dir()
    new_dir = Path.home() / ".conda" / "global"

    if not legacy.is_dir():
        return MigrationStatus.NOT_NEEDED

    if new_dir.exists() and not force:
        return MigrationStatus.SKIPPED

    new_dir.mkdir(parents=True, exist_ok=True)

    old_manifest = find_legacy_manifest()
    if old_manifest is not None:
        target = Path.home() / ".conda" / "global.toml"
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(str(old_manifest), str(target))

    return MigrationStatus.MIGRATED


def remove_legacy_dir() -> None:
    """Remove the legacy ~/.cg/ directory after successful sync."""
    legacy = legacy_data_dir()
    if legacy.is_dir():
        shutil.rmtree(str(legacy))
