"""Handler for ``conda global edit``."""

from __future__ import annotations

import os
import subprocess
from typing import TYPE_CHECKING

from rich.console import Console

from ..paths import manifest_path

if TYPE_CHECKING:
    import argparse


def execute_edit(
    args: argparse.Namespace,
    *,
    console: Console | None = None,
) -> int:
    """Open global.toml in $EDITOR."""
    console = console or Console(highlight=False)
    path = manifest_path()

    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("", encoding="utf-8")

    editor = os.environ.get("VISUAL") or os.environ.get("EDITOR", "vi")
    result = subprocess.run([editor, str(path)])
    return result.returncode
