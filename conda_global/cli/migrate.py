"""Handler for ``conda global migrate``."""

from __future__ import annotations

from typing import TYPE_CHECKING

from rich.console import Console

if TYPE_CHECKING:
    import argparse


def execute_migrate(args: argparse.Namespace, *, console: Console | None = None) -> int:
    """Execute the ``conda global migrate`` subcommand.

    Copies the manifest from ~/.cg/ to ~/.conda/global/, runs a fresh
    sync (reinstall of all tools), then removes the old directory.
    """
    if console is None:
        console = Console(stderr=True, highlight=False)

    from ..migrate import MigrationStatus, migrate_data_dir, remove_legacy_dir
    from ..paths import _legacy_data_dir

    legacy = _legacy_data_dir()
    force = getattr(args, "force", False)

    result = migrate_data_dir(force=force)

    if result == MigrationStatus.NOT_NEEDED:
        console.print(f"Nothing to migrate: [bold]{legacy}[/bold] does not exist.")
        return 0

    if result == MigrationStatus.SKIPPED:
        console.print(
            f"[bold yellow]Skipped:[/bold yellow] [bold]{legacy}[/bold] and the new "
            "location both exist. Use --force to overwrite."
        )
        return 1

    from ..migrate import _new_data_dir

    new = _new_data_dir()
    console.print(f"[bold cyan]Migrating[/bold cyan] [bold]{legacy}[/bold] → [bold]{new}[/bold]")
    console.print()

    from .sync import execute_sync

    console.print("[bold]Reinstalling tools in new location...[/bold]")
    sync_result = execute_sync(args, console=console)

    if sync_result != 0:
        console.print(
            "[bold red]Error:[/bold red] sync failed. "
            "Old directory preserved, new location may be incomplete."
        )
        return sync_result

    remove_legacy_dir()
    console.print()
    console.print("[bold cyan]Migrated[/bold cyan] successfully.")
    console.print()
    console.print("[bold yellow]Action required:[/bold yellow] update your PATH.")
    console.print(f"  Replace: [bold]{legacy / 'bin'}[/bold]")
    console.print(f"  With:    [bold]{new / 'bin'}[/bold]")
    console.print()
    console.print("  Or run: [bold]conda global ensurepath[/bold]")
    return 0
