from __future__ import annotations

import argparse

from conda_global.plugin import conda_subcommands


def test_registers_global_subcommand():
    subcommands = list(conda_subcommands())

    assert len(subcommands) == 1
    subcommand = subcommands[0]
    assert subcommand.name == "global"
    assert subcommand.summary == "Install and manage globally available CLI tools."
    assert callable(subcommand.action)
    assert subcommand.configure_parser is not None

    parser = argparse.ArgumentParser(prog="conda global")
    assert subcommand.configure_parser(parser) is None
    args = parser.parse_args(["sync"])
    assert args.subcmd == "sync"
