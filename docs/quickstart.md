# Quick start

This guide gets you from zero to running your first globally installed
tool in under a minute.

## Prerequisites

- conda 25.1 or later
- A shell (bash, zsh, fish, or PowerShell)

## Install conda-global

```bash
conda install -c conda-forge conda-global
```

## Set up your PATH

Run the `ensurepath` command to add the conda-global bin directory
to your shell configuration:

```bash
conda global ensurepath
```

Then restart your shell (or `source` the appropriate rc file).

:::{tip}
You only need to run `conda global ensurepath` once. It adds the
bin directory to your shell's PATH configuration.
:::

## Install your first tool

![Quick start demo: install, use, list, tree, uninstall](../demos/quickstart.gif)

```bash
$ conda global install gh
  Installing tool gh...
  Installed tool gh
  Commands now available:
    gh    → ~/.cg/bin/gh
```

That's it. The `gh` command is now available from anywhere:

```bash
$ gh --version
gh version 2.74.0 (2025-05-05)
```

## What just happened?

1. conda-global created an isolated environment in its data directory
2. It installed the `gh` package from conda-forge into that environment
3. It deployed a Rust trampoline binary to the bin directory
4. It recorded the tool in the manifest (`manifest.toml`)

The trampoline is a tiny native binary that reads a JSON config and
launches the real `gh` binary with the correct environment — no shell
activation needed.

## Try more commands

```bash
# List everything installed
$ conda global list
Tool   Dependencies   Channel       Exposed   Pinned
gh     gh             conda-forge   gh

# Install another tool
$ conda global install ruff

# Run a tool without installing it permanently
$ conda global run bat -- README.md

# Update all tools
$ conda global update

# Remove a tool
$ conda global uninstall -e gh
```

## The `cg` shorthand

The standalone `cg` binary is available as a shorter alias for
`conda global`. The two are interchangeable:

```bash
cg install ruff        # same as: conda global install ruff
cg list                # same as: conda global list
```

## Next steps

- {doc}`tutorials/first-tool` — A deeper walkthrough with custom channels
  and expose mappings
- {doc}`tutorials/coming-from/pipx` — Translate your pipx workflow to
  conda-global
- {doc}`features` — How trampolines, manifests, and pinning work
- {doc}`reference/cli` — Every command and flag
