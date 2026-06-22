"""Argument parser and dispatch for conda-global CLI."""

from __future__ import annotations

import argparse


def generate_parser(parser: argparse.ArgumentParser | None = None) -> argparse.ArgumentParser:
    """Build the argument parser for ``conda global``."""
    from conda.cli.helpers import add_parser_channels

    if parser is None:
        parser = argparse.ArgumentParser(
            prog="conda global",
            description="Install and manage globally available CLI tools.",
        )

    sub = parser.add_subparsers(dest="subcmd")

    p_install = sub.add_parser("install", help="Install a tool into an isolated environment")
    p_install.add_argument("package", help="Package to install")
    p_install.add_argument(
        "-e",
        "--environment",
        default=None,
        help="Environment name (defaults to package name)",
    )
    add_parser_channels(p_install)
    p_install.add_argument(
        "--expose",
        action="append",
        default=None,
        help="Expose mapping as name=binary (repeatable)",
    )
    p_install.add_argument(
        "--force",
        action="store_true",
        default=False,
        help="Force reinstall if already exists",
    )

    p_uninstall = sub.add_parser("uninstall", help="Remove a tool and its environment")
    p_uninstall.add_argument(
        "environment_arg",
        nargs="?",
        metavar="environment",
        help="Environment to remove",
    )
    p_uninstall.add_argument(
        "-e",
        "--environment",
        default=None,
        help="Environment to remove",
    )

    p_add = sub.add_parser("add", help="Add a dependency to a tool environment")
    p_add.add_argument("package", help="Package to add")
    p_add.add_argument(
        "-e",
        "--environment",
        required=True,
        help="Target environment",
    )

    p_remove = sub.add_parser("remove", help="Remove a dependency from a tool environment")
    p_remove.add_argument("package", help="Package to remove")
    p_remove.add_argument(
        "-e",
        "--environment",
        required=True,
        help="Target environment",
    )

    p_list = sub.add_parser("list", help="List installed tools")
    p_list.add_argument("--json", action="store_true", default=False, help="Output as JSON")

    p_update = sub.add_parser("update", help="Update one or all tools")
    p_update.add_argument(
        "-e",
        "--environment",
        default=None,
        help="Environment to update (all if omitted)",
    )

    sub.add_parser("sync", help="Reconcile filesystem with manifest")

    p_expose = sub.add_parser("expose", help="Make a binary available on PATH")
    p_expose.add_argument("mapping", help="Mapping as exposed_name=binary_name")
    p_expose.add_argument(
        "-e",
        "--environment",
        required=True,
        help="Source environment",
    )

    p_hide = sub.add_parser("hide", help="Remove a binary from PATH")
    p_hide.add_argument("name", help="Exposed name to remove")
    p_hide.add_argument(
        "-e",
        "--environment",
        required=True,
        help="Source environment",
    )

    p_run = sub.add_parser("run", help="Run a tool without permanent install")
    p_run.add_argument("package", help="Package to run")
    add_parser_channels(p_run)
    p_run.add_argument("args", nargs=argparse.REMAINDER, help="Arguments to pass")

    p_tree = sub.add_parser("tree", help="Show dependency tree")
    p_tree.add_argument(
        "-e",
        "--environment",
        required=True,
        help="Environment to inspect",
    )

    sub.add_parser("edit", help="Open global.toml in $EDITOR")

    sub.add_parser("ensurepath", help="Add the global bin directory to PATH")

    p_pin = sub.add_parser("pin", help="Prevent a tool from being upgraded")
    p_pin.add_argument(
        "-e",
        "--environment",
        required=True,
        help="Environment to pin",
    )

    p_unpin = sub.add_parser("unpin", help="Allow upgrades for a tool")
    p_unpin.add_argument(
        "-e",
        "--environment",
        required=True,
        help="Environment to unpin",
    )

    p_migrate = sub.add_parser(
        "migrate",
        help="Migrate data from ~/.cg/ to ~/.conda/global/",
    )
    p_migrate.add_argument(
        "--force",
        action="store_true",
        default=False,
        help="Overwrite if target directory already exists",
    )

    return parser


def configure_parser(parser: argparse.ArgumentParser) -> None:
    """Configure the parser supplied by conda's plugin manager."""
    generate_parser(parser)


def _handle_error(exc: Exception) -> int:
    """Render an error with Rich and return its exit code."""
    from conda.base.context import context as conda_context

    if conda_context.json or conda_context.debug:
        raise exc

    from rich.console import Console

    from . import status

    console = Console(stderr=True, highlight=False)
    status.print_error(console, exc)
    return getattr(exc, "return_code", 1)


def execute(args: argparse.Namespace | tuple[str]) -> int:
    """Dispatch to the appropriate subcommand handler."""
    from ..exceptions import CondaGlobalError

    if isinstance(args, tuple):
        args = generate_parser().parse_args([str(arg) for arg in args])

    subcmd = getattr(args, "subcmd", None)
    if not subcmd:
        generate_parser().print_help()
        return 0

    try:
        if subcmd == "install":
            from .install import execute_install

            return execute_install(args)
        elif subcmd == "uninstall":
            from .uninstall import execute_uninstall

            return execute_uninstall(args)
        elif subcmd == "add":
            from .add import execute_add

            return execute_add(args)
        elif subcmd == "remove":
            from .remove import execute_remove

            return execute_remove(args)
        elif subcmd == "list":
            from .list import execute_list

            return execute_list(args)
        elif subcmd == "update":
            from .update import execute_update

            return execute_update(args)
        elif subcmd == "sync":
            from .sync import execute_sync

            return execute_sync(args)
        elif subcmd == "expose":
            from .expose import execute_expose

            return execute_expose(args)
        elif subcmd == "hide":
            from .expose import execute_hide

            return execute_hide(args)
        elif subcmd == "run":
            from .run import execute_run

            return execute_run(args)
        elif subcmd == "tree":
            from .tree import execute_tree

            return execute_tree(args)
        elif subcmd == "edit":
            from .edit import execute_edit

            return execute_edit(args)
        elif subcmd == "ensurepath":
            from .ensurepath import execute_ensurepath

            return execute_ensurepath(args)
        elif subcmd == "pin":
            from .pin import execute_pin

            return execute_pin(args)
        elif subcmd == "unpin":
            from .pin import execute_unpin

            return execute_unpin(args)
        elif subcmd == "migrate":
            from .migrate import execute_migrate

            return execute_migrate(args)
        else:
            generate_parser().print_help()
            return 1
    except CondaGlobalError as exc:
        return _handle_error(exc)
