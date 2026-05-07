# Motivation

## The problem

Command-line tools often need their own dependencies. Installing them
into a shared environment (like `base`) leads to conflicts: upgrading
one tool can break another.

The solution is isolation — each tool in its own environment. But then
you need activation, PATH management, and a way to remember what you
installed. That overhead is why tools like pipx exist.

## Prior art

### pipx

[pipx](https://pipx.pypa.io/) pioneered the "isolated tool
environments" pattern for Python. It creates a virtualenv per tool
and places wrapper scripts on PATH. It works well, but:

- Only installs from PyPI — you can't install non-Python tools like
  `gh`, `bat`, or `fd`
- Uses Python wrapper scripts that add interpreter startup time
- No manifest file for syncing across machines

### pixi global

[pixi global](https://pixi.sh/latest/reference/cli/#global) is an
excellent implementation of this pattern for the conda ecosystem.
It installs tools from conda channels into isolated environments,
uses compiled Rust trampolines for fast execution, and provides a
manifest for reproducible setups. It is the direct inspiration for
conda-global's design.

conda-global exists for users who already rely on conda as their
package manager and want tool management integrated into the conda
CLI, using conda's solver, channel configuration, and authentication.

## How conda-global fits in

conda-global brings isolated tool management into conda itself:

| | pipx | pixi global | conda-global |
|---|---|---|---|
| Package source | PyPI | conda channels | conda channels |
| Isolation | virtualenvs | pixi envs | conda envs |
| Launcher | Python scripts | Rust trampolines | Rust trampolines |
| Startup overhead | interpreter startup | negligible | negligible |
| Manifest | none | `~/.pixi/manifests/pixi-global.toml` | `~/.conda/global.toml` |
| CLI integration | standalone | pixi CLI | `conda global` + `cg` alias |
| Non-Python tools | no | yes | yes |
| Cross-machine sync | no | yes | yes |

## Design choices

Rust trampolines over wrapper scripts
: Python wrapper scripts add interpreter startup latency. A compiled
  trampoline that calls `execvp` adds negligible overhead and replaces
  the process entirely on Unix.

Hardlinks over copies
: All trampolines are hardlinks to a single master binary. This
  keeps disk usage flat regardless of how many tools are exposed.

Manifest-first approach
: The `global.toml` manifest is the source of truth. You can edit it
  by hand, check it into version control, and run
  `conda global sync` on any machine to reproduce your setup.

conda's solver
: conda-global uses conda's own solver and channel infrastructure.
  Your `.condarc` settings, channel priorities, and authentication
  tokens all work as expected.

## Acknowledgements

conda-global stands on the shoulders of
[pixi global](https://pixi.sh/), which pioneered isolated tool
management with compiled trampolines for the conda ecosystem.
It also draws from [pipx](https://pipx.pypa.io/), which
established the pattern for Python, and
[conda-express](https://github.com/jezdez/conda-express), an
earlier experiment in this space. The trampoline design closely
follows pixi's proven approach, adapted for conda's environment
layout.
