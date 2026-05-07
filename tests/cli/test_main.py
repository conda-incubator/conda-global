"""Tests for CLI parser and ``execute`` dispatch."""

from __future__ import annotations

import argparse

import pytest

from conda_global.cli.main import execute, generate_parser


def test_generate_parser_migrate_accept_force_flag():
    parser = generate_parser()
    args = parser.parse_args(["migrate", "--force"])
    assert args.subcmd == "migrate"
    assert args.force is True


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
