"""Handler for ``conda global uninstall``."""

from __future__ import annotations

from typing import TYPE_CHECKING

from conda_trampoline import TrampolineManager
from rich.console import Console

from ..envs import EnvironmentManager
from ..exceptions import EnvironmentArgumentError, ToolNotFoundError
from ..manifest import Manifest
from ..paths import global_bin_dir
from . import status

if TYPE_CHECKING:
    import argparse


def execute_uninstall(
    args: argparse.Namespace,
    *,
    console: Console | None = None,
) -> int:
    """Remove a tool and its environment."""
    console = console or Console(highlight=False)
    env_arg = getattr(args, "environment_arg", None)
    env_flag = getattr(args, "environment", None)
    if env_arg and env_flag and env_arg != env_flag:
        raise EnvironmentArgumentError(f"conflicting environments: {env_arg!r} and {env_flag!r}")
    env_name = env_flag or env_arg
    if not env_name:
        raise EnvironmentArgumentError("environment is required")

    manifest = Manifest()
    tools = manifest.load()
    if env_name not in tools:
        raise ToolNotFoundError(env_name, list(tools.keys()))

    status.message(
        console,
        "Uninstalling",
        "tool",
        env_name,
        style="bold blue",
        ellipsis=True,
    )

    tool = tools[env_name]
    trampolines = TrampolineManager(global_bin_dir())
    for exposed_name in tool.exposed:
        trampolines.remove(exposed_name)

    EnvironmentManager().remove(env_name)
    manifest.remove(env_name)

    status.message(console, "Uninstalled", "tool", env_name)
    return 0
