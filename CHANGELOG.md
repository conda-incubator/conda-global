# Changelog

## Unreleased

### Changed

- Default data directory for new installs moved from `~/.cg/` to
  `~/.conda/global/`. Existing installs continue using `~/.cg/`
  until explicitly migrated. (#8)
- Manifest moved from inside the data directory to `~/.conda/global.toml`,
  a flat file alongside the data directory for easy discoverability.
- New `conda global migrate` subcommand performs a reinstall-based
  migration from `~/.cg/` to the new layout. Copies the manifest,
  runs a fresh `sync`, then removes the old directory.

## 0.1.1 (2026-04-01)

### Changes

- Move repository to `conda-incubator` organization
  ([governance#370](https://github.com/conda/governance/issues/370)).
- Update all project URLs to `conda-incubator/conda-global`.
- Simplify installation docs: remove pixi/mamba alternatives, mention
  standalone `cg` alias.
- Bump **conda-trampoline** wheel/sdist version to `0.1.1` (it was still
  `0.1.0` in `Cargo.toml` / `pyproject.toml`, so wheels did not match the tag).

## 0.1.0 (2026-04-01)

Initial release of conda-global and conda-trampoline.

### Features

- **Global tool management**: install CLI tools into isolated conda environments
  and expose them on PATH, similar to `pipx` or `pixi global` but for the full
  conda ecosystem.
- **Rust trampoline launcher** (`conda-trampoline`): a small binary that reads a
  JSON config and launches the real tool with zero conda activation overhead.
- **Manifest-driven**: all state is tracked in a single TOML file, making it
  easy to share, back up, and version-control your global tool set.
- **conda plugin**: registers as `conda global` via pluggy, so all commands are
  available as conda subcommands.
- **Standalone CLI**: also available as the `cg` command for convenience.

### Commands

- `conda global install` — install a tool into an isolated environment
- `conda global uninstall` — remove a tool and its environment
- `conda global add` / `remove` — manage dependencies in an existing tool env
- `conda global list` — list installed tools
- `conda global update` — update one or all tools
- `conda global sync` — reconcile filesystem state with the manifest
- `conda global expose` / `hide` — control which binaries are on PATH
- `conda global run` — run a tool without installing it
- `conda global tree` — show dependency tree for a tool env
- `conda global pin` / `unpin` — lock or unlock a tool from upgrades
- `conda global ensurepath` — add the bin directory to your shell PATH
- `conda global edit` — open `manifest.toml` in your editor
- `conda global status` — show summary of installed tools and PATH status

### Packages

This project ships as two packages:

- **`conda-global`** — the Python plugin and CLI
- **`conda-trampoline`** — the Rust trampoline binary, distributed as
  platform-specific wheels via maturin

### Platforms

- Linux (x86_64, aarch64)
- macOS (x86_64, Apple Silicon)
- Windows (x86_64)
