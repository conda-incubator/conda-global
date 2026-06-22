# conda-trampoline

Small **Rust** trampoline binary plus a **stdlib-only Python** helper used by
[conda-global](https://github.com/conda-incubator/conda-global) to run globally
installed CLI tools **without** activating a conda environment every time.

## What it does

- **`_cg_trampoline`** (installed on `PATH` as `bin/_cg_trampoline` or
  `Scripts/_cg_trampoline.exe`) reads a JSON config, adjusts `PATH` and optional
  environment variables, then `exec`s the real executable.
- Each exposed tool is typically a **hardlink** (or copy) to that single
  binary. The trampoline picks the config file from its **own filename**:
  config lives next to the links under a `trampoline/` directory (see
  conda-global’s layout under `~/.conda/global/bin`).

Config shape (simplified):

```json
{
  "exe": "/path/to/real/binary",
  "path_diff": "relative/path/prefix/for/PATH",
  "env": {}
}
```

## Python package

The `conda_trampoline` module has **no third-party dependencies**. It exposes
`TrampolineManager` to copy the master binary into place, create per-tool
configs, and manage hardlinks — used by `conda-global`, not usually by
end users directly.

```python
from pathlib import Path
from conda_trampoline import TrampolineManager

tm = TrampolineManager(Path("~/.conda/global/bin").expanduser())
# deploy/remove are normally driven by conda global …
```

## Install

Most people install **conda-global**, which pulls in **conda-trampoline** as a
dependency. You can also install this package alone from PyPI if you are
building tooling on top of the same trampoline layout.

- Repository: <https://github.com/conda-incubator/conda-global>
- Docs: <https://conda-incubator.github.io/conda-global/>

## License

BSD-3-Clause (same as conda-global).

Design is inspired by pixi’s trampoline idea; this is a clean-room
implementation with no shared code.
