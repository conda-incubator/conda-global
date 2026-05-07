# Coming from Homebrew

If you use [Homebrew](https://brew.sh/) to install CLI tools, this
guide maps each brew command to its conda-global equivalent.

## Command mapping

| brew | conda-global | Notes |
|------|-------------|-------|
| `brew install <pkg>` | `conda global install <pkg>` | Installs into an isolated env, not system-wide |
| `brew uninstall <pkg>` | `conda global uninstall -e <pkg>` | |
| `brew upgrade <pkg>` | `conda global update -e <pkg>` | |
| `brew upgrade` | `conda global update` | Skips pinned tools |
| `brew list` | `conda global list` | Also supports `--json` |
| `brew pin <pkg>` | `conda global pin -e <pkg>` | Prevents upgrades |
| `brew unpin <pkg>` | `conda global unpin -e <pkg>` | |
| `brew deps <pkg>` | `conda global tree -e <pkg>` | Shows full dependency tree |
| — | `conda global run <pkg>` | Run without permanent install |
| — | `conda global sync` | Reconcile filesystem with manifest |
| — | `conda global edit` | Open manifest in editor |

## Key differences

Isolation
: Homebrew installs packages into a shared prefix (`/opt/homebrew/`
  or `/home/linuxbrew/`). Libraries are shared between formulae,
  which can cause conflicts during upgrades. conda-global gives each
  tool its own isolated conda environment — no shared state.

Package scope
: Homebrew is a general-purpose package manager (compilers, libraries,
  applications, fonts). conda-global focuses on CLI tools you want on
  PATH, similar to `brew install` for command-line utilities.

Cross-platform
: Homebrew works on macOS and Linux. conda-global works on macOS,
  Linux, and Windows, using the same manifest format everywhere.

Manifest
: Homebrew has no manifest. You reconstruct your setup with
  `brew bundle dump` (Brewfile). conda-global writes `manifest.toml`
  natively — sync it across machines with `conda global sync`.

Channels
: Homebrew has one repository (homebrew-core, plus taps). conda-global
  can pull from multiple channels (conda-forge, bioconda, nvidia, etc.)
  per tool:

  ```bash
  conda global install cuda-toolkit -c nvidia -c conda-forge
  ```

No root required
: Homebrew installs to a system directory and occasionally needs
  elevated permissions. conda-global installs everything under
  a user-space data directory — no elevated permissions needed.

## Migration workflow

1. List your brew-installed CLI tools:

   ```bash
   brew leaves
   ```

2. Install each one with conda-global (most popular CLI tools are on
   conda-forge with the same name):

   ```bash
   conda global install gh
   conda global install ripgrep
   conda global install bat
   conda global install fd-find
   ```

3. Verify they work:

   ```bash
   gh --version
   rg --version
   bat --version
   fd --version
   ```

4. Once satisfied, remove the brew versions:

   ```bash
   brew uninstall gh ripgrep bat fd
   ```

:::{tip}
Some package names differ between Homebrew and conda-forge. For
example, `fd` on Homebrew is `fd-find` on conda-forge. Check
[anaconda.org](https://anaconda.org/) if a name doesn't match.
:::

## When to keep Homebrew

Homebrew is still the right tool for:

- macOS GUI applications (`brew install --cask firefox`)
- System-level libraries other tools link against
- Packages not available on conda channels

conda-global complements Homebrew — use both where each fits best.
