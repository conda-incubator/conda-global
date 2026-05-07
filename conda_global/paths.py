"""Path helpers for conda-global filesystem layout."""

from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path


@lru_cache(maxsize=1)
def data_dir() -> Path:
    """Return the base data directory for conda-global.

    Resolution order:
    1. ``CONDA_GLOBAL_HOME`` environment variable (explicit override)
    2. ``~/.cg/`` if it already exists (legacy installs keep working)
    3. ``~/.conda/global/`` (new default for fresh installs)
    """
    env = os.environ.get("CONDA_GLOBAL_HOME")
    if env:
        return Path(env).expanduser().resolve()
    legacy = legacy_data_dir()
    if legacy.is_dir():
        return legacy
    return Path.home() / ".conda" / "global"


def legacy_data_dir() -> Path:
    """Return the old default data directory (~/.cg/)."""
    return Path.home() / ".cg"


def global_envs_dir() -> Path:
    """Return the directory for tool environments."""
    return data_dir() / "envs"


def global_bin_dir() -> Path:
    """Return the directory for trampoline binaries."""
    return data_dir() / "bin"


def trampoline_config_dir() -> Path:
    """Return the directory for trampoline configs."""
    return global_bin_dir() / "trampoline"


def trampoline_master_path() -> Path:
    """Return the path to the master trampoline binary."""
    return trampoline_config_dir() / "_cg_trampoline"


@lru_cache(maxsize=1)
def manifest_path() -> Path:
    """Return the path to the global manifest.

    New location: ``~/.conda/global.toml`` (sibling to the data dir).
    Falls back to ``<data_dir>/global.toml`` or ``<data_dir>/manifest.toml``
    for legacy installs where the manifest lived inside the data directory.
    """
    new = Path.home() / ".conda" / "global.toml"
    if new.exists():
        return new
    base = data_dir()
    for name in ("global.toml", "manifest.toml"):
        candidate = base / name
        if candidate.exists():
            return candidate
    return new
