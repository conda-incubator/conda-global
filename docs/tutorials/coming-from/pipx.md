# Coming from pipx

If you already use [pipx](https://pipx.pypa.io/), this guide maps
each pipx command to its conda-global equivalent.

## Command mapping

| pipx | conda-global | Notes |
|------|-------------|-------|
| `pipx install <pkg>` | `conda global install <pkg>` | Works with any conda package, not just Python |
| `pipx uninstall <pkg>` | `conda global uninstall <pkg>` | |
| `pipx upgrade <pkg>` | `conda global update -e <pkg>` | |
| `pipx upgrade-all` | `conda global update` | Skips pinned tools |
| `pipx list` | `conda global list` | Also supports `--json` |
| `pipx run <pkg>` | `conda global run <pkg>` | Creates a temp env, cleans up after |
| `pipx inject <pkg> <dep>` | `conda global add <dep> -e <pkg>` | |
| `pipx uninject <pkg> <dep>` | `conda global remove <dep> -e <pkg>` | |
| `pipx ensurepath` | `conda global ensurepath` | Same concept |
| `pipx pin <pkg>` | `conda global pin -e <pkg>` | Prevents upgrades |
| `pipx unpin <pkg>` | `conda global unpin -e <pkg>` | |
| — | `conda global expose <mapping> -e <env>` | Expose additional binaries |
| — | `conda global hide <name> -e <env>` | Remove an exposed binary |
| — | `conda global sync` | Reconcile filesystem with manifest |
| — | `conda global tree -e <env>` | Show dependency tree |
| — | `conda global edit` | Open manifest in editor |

## Key differences

Package ecosystem
: pipx installs Python packages from PyPI. conda-global installs
  packages from conda channels — Python, R, Rust, C/C++, and more.

Isolation mechanism
: pipx creates virtualenvs. conda-global creates full conda
  environments, so compiled dependencies (OpenSSL, CUDA, etc.)
  are properly isolated too.

Launcher
: pipx uses Python wrapper scripts. conda-global uses a compiled
  Rust trampoline that calls `execvp` directly — no interpreter
  startup.

Manifest
: pipx has no manifest file. conda-global writes `~/.conda/global.toml`,
  which can be shared across machines and synced with
  `conda global sync`.

Environment naming
: pipx names environments after the package. conda-global defaults
  to the package name but lets you override it with `-e`:

  ```bash
  conda global install gh -e github-cli
  ```

## Migration workflow

1. List your pipx tools:

   ```bash
   pipx list --short
   ```

2. Install each one with conda-global:

   ```bash
   conda global install ruff
   conda global install black
   conda global install gh
   ```

3. Verify they work:

   ```bash
   ruff --version
   black --version
   gh --version
   ```

4. Once satisfied, remove the pipx versions:

   ```bash
   pipx uninstall ruff
   pipx uninstall black
   pipx uninstall gh
   ```

:::{tip}
Many popular Python tools are available on conda-forge with the same
name as on PyPI. If a package isn't available, check
[anaconda.org](https://anaconda.org/) or request it on
[conda-forge/staged-recipes](https://github.com/conda-forge/staged-recipes).
:::
