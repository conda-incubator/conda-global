"""Data models for conda-global."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from conda.base.constants import on_win

if TYPE_CHECKING:
    from pathlib import Path

SAFE_NAME_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")


def validate_name(name: str, *, kind: str = "environment") -> None:
    """Reject names that could escape their intended directory.

    Raises ``ValueError`` for names containing path separators, ``..``,
    null bytes, or other unsafe characters.
    """
    if not name or not SAFE_NAME_RE.match(name) or ".." in name:
        raise ValueError(
            f"Invalid {kind} name: {name!r}. "
            f"Names must start with an alphanumeric character and contain "
            f"only letters, digits, dots, hyphens, and underscores."
        )


@dataclass
class ExposedBinary:
    """A binary exposed on PATH via a trampoline."""

    exposed_name: str
    binary_name: str
    env_name: str


@dataclass
class ToolEnv:
    """A globally installed tool environment."""

    name: str
    channels: list[str] = field(default_factory=lambda: ["conda-forge"])
    dependencies: dict[str, str] = field(default_factory=dict)
    exposed: dict[str, str] = field(default_factory=dict)
    pinned: bool = False

    def __post_init__(self) -> None:
        validate_name(self.name, kind="environment")

    @property
    def specs(self) -> list[str]:
        """Return dependency specs suitable for passing to the solver."""
        return [f"{name}{ver}" if ver != "*" else name for name, ver in self.dependencies.items()]

    def prefix_path(self, envs_dir: Path) -> Path:
        """Return the conda prefix path for this tool within *envs_dir*."""
        return envs_dir / self.name

    def bin_path(self, envs_dir: Path) -> Path:
        """Return the platform-correct binary directory within the prefix."""
        return self.prefix_path(envs_dir) / ("Scripts" if on_win else "bin")
