# CLI reference

All commands are available as `conda global <cmd>`. A standalone `cg`
alias is also provided for convenience.

## install

Install a tool into an isolated environment.

```
conda global install <package> [-e <env>] [-c <channel>...] [--expose <mapping>...] [--force]
```

`package`
: The conda package to install.

`-e`, `--environment`
: Environment name. Defaults to the package name.

`-c`, `--channel`
: Channel to search. Repeatable. Defaults to conda-forge.

`--expose`
: Expose mapping as `name=binary` or just `name`. Repeatable.
  Defaults to exposing the binary matching the package name.

`--force`
: Force reinstall if the tool already exists.

```bash
# Basic install
conda global install ruff

# Custom environment name and channel
conda global install cuda-toolkit -e cuda -c nvidia -c conda-forge

# Expose specific binaries
conda global install python -e py314 --expose python3.14 --expose pip=pip3.14
```

---

## uninstall

Remove a tool, its environment, and all exposed trampolines.

```
conda global uninstall <env>
```

`env`
: Environment to remove.

`-e`, `--environment`
: Environment to remove. Supported as a compatibility alias.

```bash
conda global uninstall ruff
```

---

## add

Add a dependency to an existing tool environment.

```
conda global add <package> -e <env>
```

`package`
: Package to add.

`-e`, `--environment`
: Target environment. Required.

```bash
conda global add numpy -e py314
```

---

## remove

Remove a dependency from a tool environment.

```
conda global remove <package> -e <env>
```

`package`
: Package to remove.

`-e`, `--environment`
: Target environment. Required.

```bash
conda global remove numpy -e py314
```

---

## list

List installed tools.

```
conda global list [--json]
```

`--json`
: Output as JSON instead of a table.

```bash
$ conda global list
Tool   Dependencies   Channel       Exposed   Pinned
ruff   ruff >=0.4     conda-forge   ruff      yes
gh     gh             conda-forge   gh
```

---

## update

Update one or all tools to the latest versions.

```
conda global update [-e <env>]
```

`-e`, `--environment`
: Update only this environment. If omitted, updates all tools.
  Pinned tools are skipped unless targeted explicitly.

```bash
# Update everything
conda global update

# Update one tool
conda global update -e gh
```

---

## sync

Reconcile the filesystem with the manifest. Creates missing
environments, installs missing packages, and deploys missing
trampolines.

```
conda global sync
```

This is idempotent — running it multiple times has no effect if
everything is already in place.

---

## expose

Make a binary from a tool environment available on PATH.

```
conda global expose <mapping> -e <env>
```

`mapping`
: Format `exposed_name=binary_name` or just `binary_name`.

`-e`, `--environment`
: Source environment. Required.

```bash
# Expose binary with same name
conda global expose blackd -e black

# Expose with a different name on PATH
conda global expose fmt=black -e black
```

---

## hide

Remove an exposed binary from PATH.

```
conda global hide <name> -e <env>
```

`name`
: Exposed name to remove.

`-e`, `--environment`
: Source environment. Required.

```bash
conda global hide fmt -e black
```

---

## run

Run a tool from a temporary environment without installing it
permanently.

```
conda global run <package> [-c <channel>...] [-- <args>...]
```

`package`
: Package to run.

`-c`, `--channel`
: Channel to search. Repeatable.

`args`
: Arguments passed to the tool. Use `--` to separate from
  conda-global flags.

```bash
conda global run cowsay -- "hello from conda"
conda global run bat -c conda-forge -- README.md
```

---

## tree

Show the dependency tree for a tool environment.

```
conda global tree -e <env>
```

`-e`, `--environment`
: Environment to inspect. Required.

```bash
$ conda global tree -e gh
gh
├── gh 2.74.0  (conda-forge)
│   ├── openssl >=3.0
│   └── libcurl >=8.0
└── ...
```

---

## edit

Open the manifest in your editor. Uses `$VISUAL`, then
`$EDITOR`, falling back to `vi`.

```
conda global edit
```

If the manifest doesn't exist, it is created first.

---

## ensurepath

Add the conda-global bin directory to your shell's PATH.

```
conda global ensurepath
```

Appends an `export PATH` line to `~/.bashrc`, `~/.zshrc`, or
`~/.config/fish/config.fish` depending on your current shell.
You only need to run this once.

---

## pin

Prevent a tool from being upgraded by `conda global update`.

```
conda global pin -e <env>
```

`-e`, `--environment`
: Environment to pin. Required.

---

## unpin

Allow upgrades for a previously pinned tool.

```
conda global unpin -e <env>
```

`-e`, `--environment`
: Environment to unpin. Required.
