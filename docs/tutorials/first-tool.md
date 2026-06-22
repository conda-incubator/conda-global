# Your first tool

This tutorial walks through a complete lifecycle: installing a tool,
customizing its environment, exposing additional binaries, adding
dependencies, and cleaning up.

## Install with a custom environment name

By default, `conda global install` names the environment after the
package. You can override this with `-e`:

```bash
$ conda global install gh -e github-cli
  Installing tool github-cli...
  Installed tool github-cli
  Commands now available:
    gh    → ~/.cg/bin/gh
```

The environment lives in the data directory under `envs/github-cli/`.

## Use a specific channel

Install a tool from a non-default channel:

```bash
$ conda global install cuda-toolkit -c nvidia -c conda-forge
  Installing tool cuda-toolkit...
  Installed tool cuda-toolkit
```

Channels are recorded in the manifest and used for future updates.

## Expose additional binaries

Some packages ship multiple executables. By default, conda-global
exposes the one matching the package name. Use `--expose` to control
this:

```bash
$ conda global install python -e py314 --expose python3.14 --expose pip=pip3.14
  Installing tool py314...
  Installed tool py314
  Commands now available:
    python3.14    → ~/.cg/bin/python3.14
    pip           → ~/.cg/bin/pip
```

The `pip=pip3.14` syntax means: expose the binary `pip3.14` from
the environment as `pip` on PATH.

## Add a dependency

Need an extra package in a tool's environment? Use
`conda global add`:

```bash
$ conda global add numpy -e py314
  Adding package numpy to py314...
  Added package numpy to py314
```

The environment is re-solved with the new dependency.

## Remove a dependency

```bash
$ conda global remove numpy -e py314
  Removing package numpy from py314...
  Removed package numpy from py314
```

## Pin a tool

Prevent a tool from being upgraded during `conda global update`:

```bash
$ conda global pin -e github-cli
  Pinned tool github-cli

$ conda global update
  Skipped tool github-cli (pinned)
```

Unpin it when you're ready:

```bash
$ conda global unpin -e github-cli
```

## View the dependency tree

```bash
$ conda global tree -e github-cli
github-cli
├── gh 2.74.0  (conda-forge)
│   ├── openssl >=3.0
│   ├── libcurl >=8.0
│   └── ...
└── openssl 3.2.0  (conda-forge)
```

## Uninstall

Remove the tool, its environment, and all trampolines:

```bash
$ conda global uninstall github-cli
  Uninstalling tool github-cli...
  Uninstalled tool github-cli
```

## What's in the manifest?

After these steps, `conda global edit` opens the manifest:

```toml
[envs.py314]
channels = ["conda-forge"]
dependencies = { python = "*" }
exposed = { "python3.14" = "python3.14", pip = "pip3.14" }
```

The manifest is the source of truth. You can edit it by hand and run
`conda global sync` to reconcile.

## Next steps

- {doc}`coming-from/pipx` — Map your pipx habits to conda-global
- {doc}`../guides/managing-tools` — Day-to-day tool management
- {doc}`../guides/sharing-manifests` — Share your setup across machines
