# conda-global

[![Tests](https://github.com/conda-incubator/conda-global/actions/workflows/tests.yml/badge.svg)](https://github.com/conda-incubator/conda-global/actions/workflows/tests.yml)
[![Docs](https://github.com/conda-incubator/conda-global/actions/workflows/docs.yml/badge.svg)](https://conda-incubator.github.io/conda-global/)
[![Codecov](https://img.shields.io/codecov/c/github/conda-incubator/conda-global)](https://codecov.io/gh/conda-incubator/conda-global)
[![PyPI](https://img.shields.io/pypi/v/conda-global)](https://pypi.org/project/conda-global/)
[![License](https://img.shields.io/github/license/conda-incubator/conda-global)](https://github.com/conda-incubator/conda-global/blob/main/LICENSE)
[![Python](https://img.shields.io/badge/python-3.10%E2%80%933.14-blue)](https://github.com/conda-incubator/conda-global)

Global tool installation for conda — install CLI tools into isolated environments
and make them available on PATH via trampolines.

## Overview

`conda-global` lets you install command-line tools (like `gh`, `ruff`, `bat`) into
isolated conda environments and expose them on your PATH without polluting any
project environment. It works like `pipx` for Python tools or `pixi global` for
the pixi ecosystem, but for the entire conda package ecosystem.

## Quick start

![Install ruff, use it, list tools, show dependency tree, and uninstall](demos/quickstart.gif)

```bash
# Install a tool
conda global install gh

# Use it from anywhere
gh --version

# List installed tools
conda global list

# Update all tools
conda global update

# Remove a tool
conda global uninstall -e gh
```

## How it works

Each tool gets its own isolated conda environment. A small Rust trampoline
binary (provided by the [`conda-trampoline`](https://pypi.org/project/conda-trampoline/)
package) acts as a launcher — it reads a JSON config, sets up the environment,
and launches the real binary with zero activation overhead.

All data lives under `~/.cg/` (`%USERPROFILE%\.cg` on Windows).
See the [docs](https://conda-incubator.github.io/conda-global/) for details.

## Installation

```bash
conda install -c conda-forge conda-global
```

Then add the bin directory to your PATH:

```bash
conda global ensurepath
```

## Commands

| Command | Description |
|---|---|
| `conda global install <pkg>` | Install a tool into an isolated environment |
| `conda global uninstall -e <env>` | Remove a tool and its environment |
| `conda global add <pkg> -e <env>` | Add a dependency to an existing tool env |
| `conda global remove <pkg> -e <env>` | Remove a dependency from a tool env |
| `conda global list` | List installed tools |
| `conda global update [-e <env>]` | Update one or all tools |
| `conda global sync` | Reconcile filesystem with manifest |
| `conda global expose <name>=<bin> -e <env>` | Expose a binary on PATH |
| `conda global hide <name> -e <env>` | Remove a binary from PATH |
| `conda global run <pkg> [-- <args>]` | Run a tool without installing |
| `conda global tree -e <env>` | Show dependency tree |
| `conda global pin -e <env>` | Prevent upgrades |
| `conda global unpin -e <env>` | Allow upgrades |
| `conda global ensurepath` | Add bin directory to PATH |
| `conda global edit` | Edit global.toml |

A standalone `cg` alias is also available (`cg install ruff`, etc.).

## License

BSD-3-Clause
