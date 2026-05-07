# Sharing manifests

The `global.toml` manifest is a plain text file that describes all
your globally installed tools. You can share it across machines to
replicate your setup.

## Export your current setup

The manifest path varies by platform (see {doc}`../configuration`).
Copy it to a new machine or keep it in a dotfiles repository:

```bash
cp "$(conda global info --manifest)" ~/dotfiles/conda-global.toml
```

On the target machine, place the file in the data directory and run
`conda global sync`.

## Sync on the new machine

![Edit the manifest and sync to reconcile](../../demos/sync.gif)

After placing the manifest, run:

```bash
conda global sync
```

This creates any missing environments, installs the specified
packages, and deploys trampolines for all exposed binaries.

## Example manifest

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

[envs.bat]
channels = ["conda-forge"]
dependencies = { bat = "*" }
exposed = { bat = "bat", batcat = "bat" }
```

## Version control tips

- Commit `global.toml` to your dotfiles repo
- Use `conda global pin` for tools where version stability matters
- Use version specs (`>=0.4`) instead of `*` for critical tools
- Run `conda global sync` as part of your machine bootstrap script

:::{tip}
`conda global sync` is idempotent. Running it on a machine that already has
all tools installed is a no-op — it only creates missing environments
and deploys missing trampolines.
:::
