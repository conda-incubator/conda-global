"""Handler for ``conda global ensurepath``."""

from __future__ import annotations

import os
from pathlib import Path
from typing import TYPE_CHECKING

import userpath
from rich.console import Console

from ..paths import global_bin_dir

if TYPE_CHECKING:
    import argparse


def _detect_shells(args: argparse.Namespace) -> list[str] | None:
    """Detect which shells to configure."""
    if getattr(args, "shell", None):
        return args.shell

    shells = []

    if os.environ.get("FISH_VERSION") or Path("~/.config/fish/config.fish").expanduser().exists():
        shells.append("fish")

    if os.environ.get("ZSH_VERSION") or Path("~/.zshrc").expanduser().exists():
        shells.append("zsh")

    bashrc = Path("~/.bashrc").expanduser().exists()
    bash_profile = Path("~/.bash_profile").expanduser().exists()
    if os.environ.get("BASH_VERSION") or bashrc or bash_profile:
        shells.append("bash")

    if os.environ.get("XONSH_VERSION") or Path("~/.xonshrc").expanduser().exists():
        shells.append("xonsh")

    if not shells:
        shells = ["bash"]

    return shells


def execute_ensurepath(
    args: argparse.Namespace,
    *,
    console: Console | None = None,
) -> int:
    """Add the global binary directory to PATH."""
    console = console or Console(highlight=False)
    location = str(global_bin_dir())
    shells = _detect_shells(args)

    if userpath.in_current_path(location):
        console.print(f"[bold]{location}[/bold] is already on your PATH.")
        return 0

    if userpath.need_shell_restart(location, shells=shells):
        console.print(f"[bold]{location}[/bold] is already configured in your shell.")
        console.print("Restart your shell or open a new terminal for the change to take effect.")
        return 0

    if userpath.append(location, "conda-global", shells=shells):
        console.print(f"Added [bold]{location}[/bold] to your PATH.")
        console.print("Restart your shell or open a new terminal for the change to take effect.")
        return 0

    console.print(
        f"[bold red]Error:[/bold red] could not add {location} to PATH. "
        "You may need to add it manually."
    )
    return 1
