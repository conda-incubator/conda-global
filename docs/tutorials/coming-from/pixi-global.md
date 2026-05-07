# Coming from pixi global

[`pixi global`](https://pixi.sh/) is pixi's excellent built-in tool
manager. If you're already familiar with it, this guide maps each
command to its conda-global equivalent — the concepts are very similar
since conda-global's design is directly inspired by pixi.

## Command mapping

| pixi global | conda-global | Notes |
|-------------|-------------|-------|
| `pixi global install <pkg>` | `conda global install <pkg>` | |
| `pixi global remove <pkg>` | `conda global uninstall -e <pkg>` | |
| `pixi global update <pkg>` | `conda global update -e <pkg>` | |
| `pixi global update-all` | `conda global update` | Skips pinned tools |
| `pixi global list` | `conda global list` | Also supports `--json` |
| `pixi global expose add <mapping>` | `conda global expose <mapping> -e <env>` | |
| `pixi global expose remove <name>` | `conda global hide <name> -e <env>` | |
| `pixi global sync` | `conda global sync` | Same concept |
| `pixi global edit` | `conda global edit` | Opens the manifest in `$EDITOR` |
| — | `conda global run <pkg>` | Ephemeral run without permanent install |
| — | `conda global add <dep> -e <env>` | Add a dependency to an existing env |
| — | `conda global remove <dep> -e <env>` | Remove a dependency |
| — | `conda global pin -e <env>` | Prevent upgrades |
| — | `conda global tree -e <env>` | Show dependency tree |
| — | `conda global ensurepath` | Add bin dir to PATH |

## Key differences

Solver
: pixi uses the rattler solver. conda-global uses conda's solver
  infrastructure (and respects solver plugins like
  conda-rattler-solver). Both solve against the same conda channels
  and produce compatible environments.

Integration
: pixi is a polished standalone tool with its own CLI and ecosystem.
  conda-global is a conda plugin — it runs as `conda global`, sharing
  conda's configuration, channels, and authentication.

Manifest location
: pixi global stores its manifest at
  `~/.pixi/manifests/pixi-global.toml`. conda-global uses
  `manifest.toml` in the data directory. The formats are different.

Launcher
: Both use compiled trampoline binaries for zero-overhead execution.
  conda-global uses Rust trampolines with hardlinks, similar to
  pixi's approach.

Extra commands
: conda-global adds `run` (ephemeral execution), `pin`/`unpin`,
  `tree`, and `ensurepath` which pixi global does not have.

Shorthand
: conda-global provides a `cg` alias for faster typing:

  ```bash
  cg install ruff    # same as conda global install ruff
  ```

## Migration workflow

1. List your pixi global tools:

   ```bash
   pixi global list
   ```

2. Install each one with conda-global:

   ```bash
   conda global install ruff
   conda global install gh
   conda global install bat
   ```

3. Verify they work:

   ```bash
   ruff --version
   gh --version
   bat --version
   ```

4. Make sure conda-global's bin directory is on PATH:

   ```bash
   conda global ensurepath
   ```

5. Once satisfied, remove the pixi versions:

   ```bash
   pixi global remove ruff
   pixi global remove gh
   pixi global remove bat
   ```

## When to keep pixi global

pixi global is a great choice and there is no need to switch if:

- You use pixi as your primary workflow tool — pixi global integrates
  seamlessly with the rest of the pixi experience
- You use pixi's project-level features (`pixi.toml` workspaces) and
  want one tool for everything
- You don't use conda or prefer pixi's solver and UX

conda-global is designed for users who already use conda as their
package manager and want tool management integrated into the conda
CLI, sharing conda's configuration, channels, and solver plugins.
