# AGENTS.md — conda-global coding guidelines

## Project structure

- The package provides one conda subcommand from a single plugin:
  `conda global` (global tool installation and management).

- A standalone shorthand `cg` is registered as a `[project.scripts]`
  entry point, mirroring `cw`/`ct` from conda-workspaces.

- CLI modules are organized under `conda_global/cli/`. Each
  subcommand lives in its own module (e.g., `install.py`, `list.py`).
  `cli/main.py` contains parser configuration and dispatch;
  `cli/__init__.py` is a thin re-export shim.

- The Rust trampoline binary and its Python management API
  (`conda_trampoline`) live in `packages/conda-trampoline/`. It is published
  as a separate PyPI/conda package (`conda-trampoline`) via maturin
  with platform-specific wheels. The Python module has no dependencies
  beyond the standard library. The main Python package (`conda-global`)
  depends on it and is built with hatchling. A single multi-output
  conda recipe in `recipe/` produces both packages.

- Tests mirror the source structure. Tests for
  `conda_global/cli/install.py` live in `tests/cli/test_install.py`.

## Imports

- Use relative imports for all intra-package references
  (`from .models import ToolEnv`,
  `from ..exceptions import CondaGlobalError`).
  Absolute `conda_global.*` imports should only appear in tests and
  entry points.

- Inline (lazy) imports are reserved for performance-critical paths
  or optional dependencies. Acceptable cases: `plugin.py` hooks
  (loaded on every `conda` invocation), `__main__.py` entry point,
  `cli/main.py` subcommand dispatch (only the chosen handler is
  loaded). Everywhere else, imports belong at the top of the module.

## Dependencies

- Minimize the dependency graph. Prefer stdlib or already-required
  packages over adding new ones.

- Pin minimum versions in `pyproject.toml` dependencies (e.g.,
  `"tomlkit >=0.13"`), not exact versions.

## Typing and linting

- All code must be typed using modern annotations (`str | None` not
  `Optional[str]`, `list[str]` not `List[str]`). `ClassVar` from
  `typing` is the correct annotation for class-level attributes.

- Use `ruff` for linting and formatting. Configured in
  `pyproject.toml`.

- Use `from __future__ import annotations` in all modules.

## Testing

- Tests are plain `pytest` functions — no `unittest.TestCase` or other
  class-based test grouping.

- Use `pytest` native fixtures (`tmp_path`, `monkeypatch`, `capsys`)
  instead of `unittest.mock`. Prefer `monkeypatch.setattr` with simple
  fakes or recording closures over `MagicMock` / `patch`.

- Use `pytest.mark.parametrize` extensively. When multiple test cases
  exercise the same logic with different inputs, consolidate them into
  a single parameterized test.

- Shared fixtures belong in `conftest.py` at the appropriate level.

## Code structure

- Avoid private module-level helper functions (`_foo()`). If a helper
  is called once, inline it at the call site. If it is genuinely
  reused or tested independently, make it a public function with a
  clear name and docstring. The underscore-prefix convention creates
  untestable, hard-to-patch indirection without real encapsulation.

## Conda integration

- Use `-e`/`--environment` for environment targeting, consistent with
  conda-workspaces and pixi global.

- Use conda's own APIs where available (e.g., `conda.base.constants`,
  `conda.base.context.context`) rather than reimplementing platform
  detection or config parsing.

- The plugin registers via `pluggy` hooks (`conda_subcommands`) and
  the `[project.entry-points.conda]` entry point.

## CLI conventions

- All commands use `-e`/`--environment` for env targeting (always a
  flag, never positional). The positional argument is always the
  "thing" being acted on (package, binary name, mapping).

- Verb pairs: `install`/`uninstall`, `add`/`remove`, `expose`/`hide`,
  `pin`/`unpin`.

- `remove` modifies an env (removes a dep). `uninstall` removes the
  entire env.

## CLI output

- All output uses Rich, following conda-workspaces patterns.

- Every `execute_*` handler accepts `console: Console | None = None`.

- Shared status helpers live in `cli/status.py` (verb-based,
  colorblind-safe status lines).

- Tables use `Table(show_edge=False, pad_edge=False)`.

- Errors use `[bold red]Error:[/bold red]` with
  `rich.markup.escape` on user text.

## Lockfile maintenance

- After any change to `pyproject.toml` that affects pixi metadata
  (dependencies, features, tasks, or workspace settings), always run
  `pixi lock` and commit the updated `pixi.lock` alongside the
  `pyproject.toml` change. CI will fail if the lockfile is out of date.

- After any change to `packages/conda-trampoline/Cargo.toml`, run
  `cargo generate-lockfile --manifest-path packages/conda-trampoline/Cargo.toml`
  (or `cargo build`) and commit the updated `Cargo.lock`.

## Documentation

- Docs use Sphinx with `conda-sphinx-theme`, `myst-parser`, and
  `sphinx-design`.

- Follow the Diataxis framework: tutorials, how-to guides, reference,
  and explanation sections.
