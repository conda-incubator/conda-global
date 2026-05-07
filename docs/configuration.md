# Configuration

:::{note}
All paths below use `~/` as shorthand for your home directory:
`/home/<user>/` or `/Users/<user>/` on macOS/Linux,
`%USERPROFILE%` (typically `C:\Users\<user>\`) on Windows.
:::

## Manifest

The manifest at `~/.conda/global.toml` is the source of truth for
all globally installed tools. It is written by conda-global commands
and can also be edited by hand.

### Format

Each tool environment is defined under `[envs.<name>]`:

```toml
[envs.gh]
channels = ["conda-forge"]
dependencies = { gh = "*" }
exposed = { gh = "gh" }

[envs.ruff]
channels = ["conda-forge"]
dependencies = { ruff = ">=0.4" }
exposed = { ruff = "ruff" }
pinned = true

[envs.py314]
channels = ["conda-forge"]
dependencies = { python = "*", pip = "*" }
exposed = { "python3.14" = "python3.14", pip = "pip3.14" }
```

### Fields

`channels`
: List of conda channels to search when solving the environment.
  Order matters — earlier channels have higher priority.

`dependencies`
: Map of package names to version specs. Use `"*"` for any version,
  or a conda match spec like `">=0.4"`, `">=1.0,<2"`.

`exposed`
: Map of exposed names to binary names. The key is the name that
  appears on PATH; the value is the binary inside the environment's
  `bin/` (or `Scripts/` on Windows).

`pinned`
: Optional boolean. If `true`, the tool is skipped during
  `conda global update` (unless targeted explicitly with `-e`).
  Defaults to `false`.

## Filesystem layout

```
~/.conda/
├── global.toml                  ← manifest (source of truth)
└── global/
    ├── bin/                     ← exposed trampolines (on PATH)
    │   ├── ruff                   hardlink → trampoline/_cg_trampoline
    │   ├── gh                     hardlink → trampoline/_cg_trampoline
    │   └── trampoline/
    │       ├── _cg_trampoline     master binary (compiled Rust)
    │       ├── ruff.json          config for ruff trampoline
    │       └── gh.json            config for gh trampoline
    └── envs/                    ← isolated tool environments
        ├── ruff/
        │   ├── bin/ruff           real binary
        │   └── conda-meta/       conda metadata (marks valid env)
        └── gh/
            ├── bin/gh
            └── conda-meta/
```

On Windows, `bin/` uses platform-appropriate extensions (`.exe`).

### Paths

| Path | Purpose |
|------|---------|
| `~/.conda/global.toml` | Manifest (source of truth) |
| `~/.conda/global/bin/` | Trampoline directory, added to PATH |
| `~/.conda/global/bin/trampoline/` | Master binary and JSON configs |
| `~/.conda/global/envs/` | Tool environments (one prefix per tool) |

## Trampoline config files

Each exposed binary has a JSON config at
`~/.conda/global/bin/trampoline/<name>.json`:

```json
{
  "exe": "/home/user/.conda/global/envs/gh/bin/gh",
  "path_diff": "/home/user/.conda/global/envs/gh/bin",
  "env": {}
}
```

`exe`
: Absolute path to the real binary inside the tool environment.

`path_diff`
: Directory to prepend to `PATH` before launching.

`env`
: Additional environment variables to set. Empty by default.

These files are managed automatically. Editing them is only useful
for debugging.

## Environment variables

`CONDA_GLOBAL_HOME`
: Override the base directory for environments and trampolines.
  Without this variable, conda-global uses `~/.cg/` if it exists
  (legacy), otherwise `~/.conda/global/` (new default). The manifest
  always lives at `~/.conda/global.toml` regardless of this setting.
  Supports `~` expansion and relative paths.

## Migration from ~/.cg/

Previous versions of conda-global stored data in `~/.cg/`. If that
directory exists, conda-global continues to use it automatically —
no action is required. New installs use `~/.conda/global/` by default.

To migrate explicitly, run:

```bash
conda global migrate
```

This copies your manifest to the new location, reinstalls all tools
with a fresh `sync`, and removes the old directory. After migration,
update your PATH (replace `~/.cg/bin` with `~/.conda/global/bin`)
or run `conda global ensurepath`.

`EDITOR` / `VISUAL`
: Used by `conda global edit` to open the manifest. `VISUAL` takes
  precedence.
