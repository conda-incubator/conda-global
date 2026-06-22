# Features

An overview of what conda-global provides and how the pieces fit
together.

## Isolated environments

Every tool gets its own conda environment under the `envs/` directory.
Dependencies are fully isolated — installing `ruff` cannot break `gh`,
even if they depend on different versions of the same library.

Environments are standard conda prefixes. You can inspect them with
conda commands:

```bash
conda list -p ~/.conda/global/envs/ruff
```

## Rust trampolines

When you install a tool, conda-global deploys a small native binary
(the trampoline, provided by the `conda-trampoline` package) in the
`bin/` directory. This binary:

1. Reads a JSON config from `bin/trampoline/<name>.json`
2. Sets `PATH` and any custom environment variables
3. Replaces itself with the real binary via `execvp` (Unix) or
   spawns it as a child process (Windows)

The trampoline adds negligible overhead — there is no Python
interpreter startup, no shell activation, no conda environment
solving at runtime.

All trampolines are hardlinks to a single master binary at
`bin/trampoline/_cg_trampoline`. This means 100 exposed
tools use the same disk space as one (plus 100 small JSON configs).

### Trampoline config

Each exposed binary has a JSON config:

```json
{
  "exe": "/home/user/.conda/global/envs/ruff/bin/ruff",
  "path_diff": "/home/user/.conda/global/envs/ruff/bin",
  "env": {}
}
```

`exe`
: Absolute path to the real binary.

`path_diff`
: Directory to prepend to `PATH` before launching.

`env`
: Additional environment variables to set.

## Binary exposure

![Expose and hide binaries](../demos/expose-hide.gif)

By default, `conda global install <pkg>` exposes executables that conda
package metadata marks as package-owned. You can control this with
`--expose`:

```bash
# Expose a specific binary
conda global install python --expose python3.14

# Rename on PATH
conda global install python --expose pip=pip3.14

# Expose multiple binaries
conda global install python --expose python3.14 --expose pip=pip3.14
```

After installation, use `conda global expose` and `conda global hide`
to add or remove exposed binaries without reinstalling.

## Manifest

The manifest (`~/.conda/global.toml`) records all tools, their
channels, dependencies, exposed binaries, and pin status. It is
the source of truth for `conda global sync`.

```toml
[envs.ruff]
channels = ["conda-forge"]
dependencies = { ruff = ">=0.4" }
exposed = { ruff = "ruff" }
pinned = true
```

See {doc}`configuration` for the full manifest reference.

## Pinning

![Pin, update, and unpin](../demos/pin-update.gif)

Pin a tool to freeze it at its current version during
`conda global update`:

```bash
conda global pin -e ruff
```

Pinned tools show `pinned = true` in the manifest and are skipped
by `conda global update` (unless targeted directly with `-e`).

## Cross-platform support

conda-global works on Linux, macOS, and Windows:

- Unix: trampolines use `execvp` to replace the process entirely
- Windows: trampolines spawn a child process and forward the exit
  code, with `ctrlc` signal forwarding
- Binary extensions are `.exe` on Windows, none on Unix
- `Scripts/` is used instead of `bin/` on Windows prefixes

## conda plugin

conda-global registers as a conda plugin. All commands are available
as `conda global <cmd>`. A standalone `cg` alias is also provided
for convenience:

```bash
conda global install ruff
conda global list
```
