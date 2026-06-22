"""Handler for ``conda global run``."""

from __future__ import annotations

import subprocess
import sys
from typing import TYPE_CHECKING

from conda.base.context import context
from rich.console import Console

from ..binaries import find_binary
from ..envs import EnvironmentManager
from ..exceptions import BinaryNotFoundError
from . import status

if TYPE_CHECKING:
    import argparse


def execute_run(
    args: argparse.Namespace,
    *,
    console: Console | None = None,
) -> int:
    """Run a tool from a temporary env without permanent install."""
    console = console or Console(highlight=False)
    package = args.package
    channels = list(context.channels)
    extra_args = args.args or []

    if extra_args and extra_args[0] == "--":
        extra_args = extra_args[1:]

    temp_name = f"_cg_run_{package}"
    envs = EnvironmentManager()

    status.message(
        console,
        "Running",
        "tool",
        package,
        style="bold blue",
        ellipsis=True,
    )

    try:
        prefix = envs.create(temp_name, [package], channels)
        binary_path = find_binary(prefix, package)
        if binary_path is None:
            raise BinaryNotFoundError(package, temp_name)

        result = subprocess.run(
            [str(binary_path), *extra_args],
            stdin=sys.stdin,
            stdout=sys.stdout,
            stderr=sys.stderr,
        )
        return result.returncode
    finally:
        envs.remove(temp_name)
