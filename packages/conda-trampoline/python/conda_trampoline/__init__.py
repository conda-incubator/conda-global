"""Python API for the conda-trampoline binary.

Deploy, hardlink, and remove trampoline binaries and their JSON configs.
This module has no dependencies beyond the standard library.
"""

from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

_ON_WIN = sys.platform == "win32"


class TrampolineManager:
    """Manages trampoline binaries and their JSON configs.

    *bin_dir* is the directory where exposed trampolines live.  Callers
    must pass it explicitly — this package does not know about any
    particular filesystem layout.

    Usage::

        trampolines = TrampolineManager(Path("~/.conda/global/bin"))
        trampolines.deploy("gh", exe_path, "/path/to/bin")
        trampolines.remove("gh")
    """

    def __init__(self, bin_dir: Path) -> None:
        self.bin_dir = bin_dir

    @property
    def config_dir(self) -> Path:
        """Directory for the master binary and JSON configs."""
        return self.bin_dir / "trampoline"

    @property
    def master_path(self) -> Path:
        """Path to the master trampoline binary."""
        return self.config_dir / "_cg_trampoline"

    @property
    def extension(self) -> str:
        """Platform-appropriate binary extension."""
        return ".exe" if _ON_WIN else ""

    def ensure_master(self) -> Path:
        """Ensure the master trampoline binary exists, deploying it if needed."""
        self.config_dir.mkdir(parents=True, exist_ok=True)

        if not self.master_path.is_file():
            source = find_trampoline_binary()
            shutil.copy2(source, self.master_path)
            if not _ON_WIN:
                self.master_path.chmod(0o755)

        return self.master_path

    def deploy(
        self,
        exposed_name: str,
        exe_path: Path,
        path_diff: str,
        env: dict[str, str] | None = None,
    ) -> Path:
        """Deploy a trampoline for an exposed binary.

        Creates a hardlink from ``<bin_dir>/<exposed_name>`` to the master
        trampoline, and writes the JSON config.

        Falls back to copying if hardlinking fails.
        """
        master = self.ensure_master()
        self.bin_dir.mkdir(parents=True, exist_ok=True)

        trampoline_path = self.bin_dir / f"{exposed_name}{self.extension}"

        if not trampoline_path.exists():
            try:
                trampoline_path.hardlink_to(master)
            except OSError:
                shutil.copy2(master, trampoline_path)

        if not _ON_WIN:
            trampoline_path.chmod(0o755)

        config = {
            "exe": str(exe_path),
            "path_diff": path_diff,
            "env": env or {},
        }
        config_path = self.config_dir / f"{exposed_name}.json"
        config_path.write_text(json.dumps(config, indent=2), encoding="utf-8")

        return trampoline_path

    def remove(self, exposed_name: str) -> None:
        """Remove a trampoline binary and its config."""
        trampoline_path = self.bin_dir / f"{exposed_name}{self.extension}"
        config_path = self.config_dir / f"{exposed_name}.json"

        if trampoline_path.exists():
            trampoline_path.unlink()
        if config_path.exists():
            config_path.unlink()


def find_trampoline_binary() -> Path:
    """Locate the trampoline binary provided by the conda-trampoline package.

    The binary is installed to the environment's scripts directory by maturin.
    For development the cargo target directory is checked as a fallback.
    """
    package_dir = Path(__file__).parent
    prefix = Path(sys.prefix)

    if _ON_WIN:
        candidates = [
            prefix / "Scripts" / "_cg_trampoline.exe",
            package_dir / "_cg_trampoline.exe",
            package_dir.parent / "target" / "release" / "_cg_trampoline.exe",
        ]
    else:
        candidates = [
            prefix / "bin" / "_cg_trampoline",
            package_dir / "_cg_trampoline",
            package_dir.parent / "target" / "release" / "_cg_trampoline",
        ]
    for candidate in candidates:
        resolved = candidate.resolve()
        if resolved.is_file():
            return resolved
    msg = "trampoline binary not found in package"
    raise FileNotFoundError(msg)
