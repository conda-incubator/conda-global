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


def execute_ensurepath(
    args: argparse.Namespace,
    *,
    console: Console | None = None,
) -> int:
    """Add the global binary directory to PATH."""
    console = console or Console(highlight=False)
    location = str(global_bin_dir())

    if getattr(args, "shell", None):
        shells = args.shell
    else:
        shells = []
        fish_config = Path("~/.config/fish/config.fish").expanduser().exists()
        if os.environ.get("FISH_VERSION") or fish_config:
            shells.append("fish")
        zshrc = Path("~/.zshrc").expanduser().exists()
        if os.environ.get("ZSH_VERSION") or zshrc:
            shells.append("zsh")
        bashrc = Path("~/.bashrc").expanduser().exists()
        bash_profile = Path("~/.bash_profile").expanduser().exists()
        if os.environ.get("BASH_VERSION") or bashrc or bash_profile:
            shells.append("bash")
        xonshrc = Path("~/.xonshrc").expanduser().exists()
        if os.environ.get("XONSH_VERSION") or xonshrc:
            shells.append("xonsh")
        if not shells:
            shells = ["bash"]

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
