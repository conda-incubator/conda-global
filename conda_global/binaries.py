"""Find binaries in tool environments."""

from __future__ import annotations

import stat
from pathlib import Path

from conda.base.constants import on_win
from conda.common.path import BIN_DIRECTORY
from conda.core.prefix_data import PrefixData


def discover_binaries(prefix: Path) -> list[str]:
    """Return a list of executable binary names in a conda prefix.

    Looks in ``bin/`` on Unix or ``Scripts/`` on Windows.
    """
    bin_dir = prefix / BIN_DIRECTORY
    if not bin_dir.is_dir():
        return []

    binaries = []
    for entry in sorted(bin_dir.iterdir()):
        if not entry.is_file():
            continue
        if on_win:
            if entry.suffix.lower() in (".exe", ".bat", ".cmd"):
                binaries.append(entry.stem)
        else:
            if _is_executable(entry):
                binaries.append(entry.name)
    return binaries


def discover_package_binaries(prefix: Path, package: str) -> list[str]:
    """Return executable binary names owned by an installed package."""
    record = PrefixData(prefix).get(package, None)
    files = getattr(record, "files", None)
    if not files:
        return []

    bin_path = Path(BIN_DIRECTORY)
    binaries = []

    for file in sorted(files):
        path = Path(file)
        if path.parent != bin_path:
            continue

        candidate = prefix / path
        if not candidate.is_file():
            continue

        if on_win:
            if candidate.suffix.lower() in (".exe", ".bat", ".cmd"):
                binaries.append(candidate.stem)
        elif _is_executable(candidate):
            binaries.append(candidate.name)

    return binaries


def _is_executable(path: Path) -> bool:
    """Check if a file has the executable bit set."""
    return bool(path.stat().st_mode & (stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH))


def find_binary(prefix: Path, name: str) -> Path | None:
    """Find a specific binary by name in a conda prefix."""
    bin_dir = prefix / BIN_DIRECTORY
    if not bin_dir.is_dir():
        return None

    if on_win:
        for ext in (".exe", ".bat", ".cmd", ""):
            candidate = bin_dir / f"{name}{ext}"
            if candidate.is_file():
                return candidate
    else:
        candidate = bin_dir / name
        if candidate.is_file():
            return candidate

    return None
