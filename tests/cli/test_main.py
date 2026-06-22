"""Tests for CLI parser and ``execute`` dispatch."""

from __future__ import annotations

import argparse
from typing import TYPE_CHECKING

import pytest
from conda.base.context import context, reset_context
from conda.common.constants import NULL

from conda_global.cli.main import configure_parser, execute, generate_parser

if TYPE_CHECKING:
    from pathlib import Path


def test_generate_parser_migrate_accept_force_flag():
    parser = generate_parser()
    args = parser.parse_args(["migrate", "--force"])
    assert args.subcmd == "migrate"
    assert args.force is True


def test_configure_parser_uses_existing_parser():
    parser = argparse.ArgumentParser(prog="conda global")
    configure_parser(parser)

    args = parser.parse_args(["install", "gh"])

    assert args.subcmd == "install"
    assert args.package == "gh"


@pytest.mark.parametrize(
    ("argv", "environment_arg", "environment"),
    [
        (["uninstall", "httpie"], "httpie", None),
        (["uninstall", "-e", "httpie"], None, "httpie"),
    ],
    ids=["positional", "flag"],
)
def test_generate_parser_uninstall_accepts_environment_forms(
    argv,
    environment_arg,
    environment,
):
    args = generate_parser().parse_args(argv)
    assert args.subcmd == "uninstall"
    assert args.environment_arg == environment_arg
    assert args.environment == environment


@pytest.mark.parametrize("subcmd", ["install", "run"])
def test_generate_parser_accepts_channel_customization(subcmd):
    parser = generate_parser()
    args = parser.parse_args(
        [subcmd, "-c", "conda-forge", "--use-local", "--override-channels", "gh"]
    )
    assert args.subcmd == subcmd
    assert args.channel == ["conda-forge"]
    assert args.use_local is True
    assert args.override_channels is True


@pytest.mark.parametrize("subcmd", ["install", "run"])
def test_generate_parser_leaves_use_local_unset_by_default(subcmd):
    parser = generate_parser()
    args = parser.parse_args([subcmd, "gh"])
    assert args.use_local is NULL


def test_standalone_main_initializes_conda_context(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
):
    old_search_path = context._search_path
    old_argparse_args = context._argparse_args
    condarc = tmp_path / "condarc"
    condarc.write_text("channels:\n  - https://repo.anaconda.com/pkgs/main\n")
    monkeypatch.setenv("CONDARC", str(condarc))

    recorded: dict[str, tuple[str, ...]] = {}

    def fake_execute(args):
        recorded["channels"] = context.channels
        return 0

    monkeypatch.setattr("conda_global.cli.main.execute", fake_execute)

    try:
        from conda_global.__main__ import main

        with pytest.raises(SystemExit) as exc_info:
            main(["install", "-c", "conda-forge", "gh"])
    finally:
        reset_context(old_search_path, old_argparse_args)

    assert exc_info.value.code == 0
    assert recorded["channels"] == (
        "conda-forge",
        "https://repo.anaconda.com/pkgs/main",
    )


def test_execute_without_subcommand_prints_help(capsys):
    args = argparse.Namespace(subcmd=None)
    assert execute(args) == 0
    out = capsys.readouterr().out
    lowered = out.lower()
    assert "subcommands" in lowered or "install" in out


def test_execute_unknown_subcommand(capsys):
    args = argparse.Namespace(subcmd="not-a-real-command")
    assert execute(args) == 1
    out = capsys.readouterr().out
    assert "install" in out or "subcommands" in out.lower()


def test_execute_routes_migrate(monkeypatch):
    args = argparse.Namespace(subcmd="migrate", force=True)
    recorded: list[argparse.Namespace] = []

    def fake_migrate(ns, **kwargs):
        recorded.append(ns)
        return 42

    monkeypatch.setattr("conda_global.cli.migrate.execute_migrate", fake_migrate)
    assert execute(args) == 42
    assert recorded == [args]


def test_execute_routes_sync(monkeypatch):
    args = argparse.Namespace(subcmd="sync")

    def fake(ns, **kwargs):
        return 7

    monkeypatch.setattr("conda_global.cli.sync.execute_sync", fake)
    assert execute(args) == 7


def test_execute_accepts_argv_tuple(monkeypatch):
    recorded: list[argparse.Namespace] = []

    def fake(ns, **kwargs):
        recorded.append(ns)
        return 7

    monkeypatch.setattr("conda_global.cli.sync.execute_sync", fake)

    assert execute(("sync",)) == 7
    assert recorded[0].subcmd == "sync"


@pytest.mark.parametrize(
    "subcmd,target",
    [
        ("install", "conda_global.cli.install.execute_install"),
        ("uninstall", "conda_global.cli.uninstall.execute_uninstall"),
        ("add", "conda_global.cli.add.execute_add"),
        ("remove", "conda_global.cli.remove.execute_remove"),
        ("list", "conda_global.cli.list.execute_list"),
        ("update", "conda_global.cli.update.execute_update"),
        ("expose", "conda_global.cli.expose.execute_expose"),
        ("hide", "conda_global.cli.expose.execute_hide"),
        ("run", "conda_global.cli.run.execute_run"),
        ("tree", "conda_global.cli.tree.execute_tree"),
        ("edit", "conda_global.cli.edit.execute_edit"),
        ("ensurepath", "conda_global.cli.ensurepath.execute_ensurepath"),
        ("pin", "conda_global.cli.pin.execute_pin"),
        ("unpin", "conda_global.cli.pin.execute_unpin"),
    ],
)
def test_execute_dispatches_to_handler(subcmd, target, monkeypatch):
    ns = argparse.Namespace(subcmd=subcmd)

    def fake(*a, **k):
        return 99

    monkeypatch.setattr(target, fake)
    assert execute(ns) == 99
