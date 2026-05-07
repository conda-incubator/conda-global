# conda-global

Install CLI tools into isolated conda environments and make them
available on PATH via trampolines — no activation needed.

`conda-global` brings the same ideas pioneered by
[pixi global](https://pixi.sh/latest/reference/cli/#global) and
[pipx](https://pipx.pypa.io/) into the conda CLI. It covers the entire
conda package ecosystem: Python, R, Rust, C/C++, and anything else
conda can install.

## Install

```bash
conda install -c conda-forge conda-global
```

Then add the global binary directory to your PATH:

```bash
conda global ensurepath
```

A standalone `cg` alias is also available — `cg install ruff` is
equivalent to `conda global install ruff`.

## Quick example

![Install ruff, use it, list tools, and show dependency tree](../demos/quickstart.gif)

```bash
$ conda global install ruff
  Installing tool ruff...
  Installed tool ruff
  Commands now available:
    ruff    → ~/.cg/bin/ruff

$ ruff --version
ruff 0.11.6

$ conda global list
Tool   Dependencies   Channel       Exposed   Pinned
ruff   ruff           conda-forge   ruff
```

## How it works

Each tool gets its own isolated conda environment. A small Rust
trampoline binary reads a JSON config, sets up the environment
variables, and launches the real binary — with zero activation
overhead.

```
~/.conda/
├── global.toml           ← manifest (source of truth)
└── global/
    ├── bin/
    │   ├── ruff            ← trampoline (hardlink)
    │   ├── gh              ← trampoline (hardlink)
    │   └── trampoline/
    │       ├── _cg_trampoline  ← master binary
    │       ├── ruff.json       ← config for ruff
    │       └── gh.json         ← config for gh
    └── envs/
        ├── ruff/           ← isolated env
        │   ├── bin/ruff      ← real binary
        │   └── conda-meta/
        └── gh/             ← isolated env
            ├── bin/gh        ← real binary
            └── conda-meta/
```

## Why conda-global?

:::::::{grid} 1 1 2 2
:gutter: 3

::::::{grid-item-card} {octicon}`package;1em` Any conda package
Install tools from any channel — conda-forge, bioconda, nvidia, or
your own. Not limited to Python packages.
::::::

::::::{grid-item-card} {octicon}`zap;1em` Zero overhead
Rust trampolines launch tools directly via `execvp` on Unix or
`CreateProcess` on Windows. No shell activation, no startup delay.
::::::

::::::{grid-item-card} {octicon}`shield-lock;1em` Full isolation
Each tool lives in its own conda environment. No dependency conflicts
between tools, ever.
::::::

::::::{grid-item-card} {octicon}`sync;1em` Portable manifest
Share `global.toml` across machines. Run `conda global sync` to reconcile.
::::::

:::::::

## Navigation

:::::::{grid} 1 1 2 2
:gutter: 3

::::::{grid-item-card} {octicon}`rocket;1em` Getting started
:link: quickstart
:link-type: doc

Install conda-global and your first tool in under a minute.
::::::

::::::{grid-item-card} {octicon}`mortar-board;1em` Tutorials
:link: tutorials/index
:link-type: doc

Step-by-step guides for common workflows.
::::::

::::::{grid-item-card} {octicon}`star;1em` Features
:link: features
:link-type: doc

Trampolines, binary exposure, manifest sync, and more.
::::::

::::::{grid-item-card} {octicon}`gear;1em` Configuration
:link: configuration
:link-type: doc

Manifest format, filesystem layout, and environment variables.
::::::

::::::{grid-item-card} {octicon}`terminal;1em` CLI reference
:link: reference/cli
:link-type: doc

Every command and flag.
::::::

::::::{grid-item-card} {octicon}`light-bulb;1em` Motivation
:link: motivation
:link-type: doc

Why conda-global exists and how it relates to pipx and pixi.
::::::

::::::{grid-item-card} {octicon}`log;1em` Changelog
:link: changelog
:link-type: doc

Release history and notable changes.
::::::

:::::::

```{toctree}
:hidden:
:caption: Tutorials

quickstart
tutorials/index
```

```{toctree}
:hidden:
:caption: How-to guides

guides/managing-tools
guides/sharing-manifests
```

```{toctree}
:hidden:
:caption: Reference

reference/cli
configuration
```

```{toctree}
:hidden:
:caption: Explanation

features
motivation
```

```{toctree}
:hidden:
:caption: Project

changelog
```
