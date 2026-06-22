"""Conda plugin hooks for conda-global."""

from __future__ import annotations

from typing import TYPE_CHECKING

from conda.plugins import hookimpl

if TYPE_CHECKING:
    from collections.abc import Iterable

    from conda.plugins.types import CondaSubcommand


@hookimpl
def conda_subcommands() -> Iterable[CondaSubcommand]:
    from conda.plugins.types import CondaSubcommand

    from .cli.main import configure_parser, execute

    yield CondaSubcommand(
        name="global",
        summary="Install and manage globally available CLI tools.",
        action=execute,
        configure_parser=configure_parser,
    )
