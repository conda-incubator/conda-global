"""Handler for ``conda global install``."""

from __future__ import annotations

from typing import TYPE_CHECKING

from conda.base.constants import on_win
from conda.base.context import context
from conda_trampoline import TrampolineManager
from rich.console import Console

from ..binaries import discover_binaries, find_binary
from ..envs import EnvironmentManager
from ..exceptions import BinaryNotFoundError, ToolExistsError
from ..manifest import Manifest
from ..models import ToolEnv, validate_name
from ..paths import global_bin_dir
from . import status

if TYPE_CHECKING:
    import argparse


def execute_install(
    args: argparse.Namespace,
    *,
    console: Console | None = None,
) -> int:
    """Install a tool into an isolated environment."""
    console = console or Console(highlight=False)
    package = args.package
    env_name = args.environment or package
    channels = list(context.channels)
    force = args.force

    envs = EnvironmentManager()
    manifest = Manifest()
    trampolines = TrampolineManager(global_bin_dir())

    if envs.exists(env_name) and not force:
        raise ToolExistsError(env_name)

    status.message(
        console,
        "Installing",
        "tool",
        env_name,
        style="bold blue",
        ellipsis=True,
    )

    prefix = envs.create(env_name, [package], channels)

    expose_mappings: dict[str, str] = {}
    if args.expose:
        for mapping in args.expose:
            if "=" in mapping:
                exposed_name, binary_name = mapping.split("=", 1)
            else:
                exposed_name = binary_name = mapping
            validate_name(exposed_name, kind="exposed binary")
            validate_name(binary_name, kind="binary")
            expose_mappings[exposed_name] = binary_name
    else:
        available = discover_binaries(prefix)
        if package in available:
            expose_mappings[package] = package
        elif available:
            expose_mappings[available[0]] = available[0]

    tool = ToolEnv(
        name=env_name,
        channels=channels,
        dependencies={package: "*"},
        exposed=expose_mappings,
    )
    bin_dir = tool.bin_path(envs.envs_dir)

    for exposed_name, binary_name in expose_mappings.items():
        binary_path = find_binary(prefix, binary_name)
        if binary_path is None:
            raise BinaryNotFoundError(binary_name, env_name)
        trampolines.deploy(
            exposed_name=exposed_name,
            exe_path=binary_path,
            path_diff=str(bin_dir),
        )

    manifest.add(tool)

    status.message(console, "Installed", "tool", env_name)
    if expose_mappings:
        _print_exposed(console, trampolines, expose_mappings)
    return 0


def _print_exposed(
    console: Console,
    trampolines: TrampolineManager,
    exposed: dict[str, str],
) -> None:
    """Print the post-install summary of exposed commands."""
    console.print("  Commands now available:")
    ext = ".exe" if on_win else ""
    for name in sorted(exposed):
        path = trampolines.bin_dir / f"{name}{ext}"
        console.print(f"    [bold]{name}[/bold]    [dim]→ {path}[/dim]")
