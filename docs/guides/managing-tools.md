# Managing tools

Day-to-day operations for keeping your global tools current and
organized.

## Update all tools

```bash
conda global update
```

This re-solves every tool environment with the latest packages from
its configured channels. Pinned tools are skipped.

To update a single tool:

```bash
conda global update -e ruff
```

## Pin and unpin

![Pin a tool, update skips it, then unpin](../../demos/pin-update.gif)

Pin a tool to prevent `conda global update` from changing it:

```bash
conda global pin -e ruff
```

Pinned tools show a `yes` in the Pinned column of
`conda global list`. To allow upgrades again:

```bash
conda global unpin -e ruff
```

## Add and remove dependencies

Add a package to an existing tool environment:

```bash
conda global add requests -e my-script
```

Remove one:

```bash
conda global remove requests -e my-script
```

Both operations re-solve the environment to ensure consistency.

## Expose and hide binaries

![Expose an alias, use it, then hide it](../../demos/expose-hide.gif)

Expose an additional binary from a tool environment:

```bash
conda global expose black=blackd -e black
```

This deploys a trampoline for `blackd` from the `black` environment,
named `black` on PATH.

To remove it:

```bash
conda global hide black -e black
```

## Inspect a tool

![View the dependency tree, add a package, see it grow](../../demos/tree.gif)

View the full dependency tree:

```bash
conda global tree -e gh
```

View all tools in table or JSON format:

```bash
conda global list
conda global list --json
```

## Edit the manifest directly

Open the manifest in your editor:

```bash
conda global edit
```

After editing, run `conda global sync` to reconcile the filesystem
with your changes.
