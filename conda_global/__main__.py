"""Standalone CLI entry point for ``cg``.

``cg`` runs ``conda global`` commands::

    cg install gh
    cg list
    cg uninstall gh
"""

from __future__ import annotations


def main(args: list[str] | None = None) -> None:
    """Entry point for the ``cg`` console script."""
    from .cli.main import execute, generate_parser

    parser = generate_parser()
    parser.prog = "cg"

    parsed = parser.parse_args(args)
    raise SystemExit(execute(parsed))


if __name__ == "__main__":
    main()
