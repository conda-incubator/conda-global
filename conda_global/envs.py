"""Create and remove isolated tool environments."""

from __future__ import annotations

from typing import TYPE_CHECKING

from conda.base.context import context
from conda.core.envs_manager import unregister_env
from conda.exceptions import UnsatisfiableError
from conda.gateways.disk.delete import rm_rf
from conda.models.channel import Channel
from conda.models.match_spec import MatchSpec

from .exceptions import SolveError
from .paths import global_envs_dir as _default_envs_dir

if TYPE_CHECKING:
    from pathlib import Path


class EnvironmentManager:
    """Manages isolated conda environments for global tools.

    Usage::

        envs = EnvironmentManager()                    # ~/.conda/global/
        envs = EnvironmentManager(tmp / "global")      # test path

        prefix = envs.create("gh", ["gh"], ["conda-forge"])
        envs.exists("gh")
        envs.remove("gh")
    """

    def __init__(self, envs_dir: Path | None = None) -> None:
        self.envs_dir = envs_dir or _default_envs_dir()

    def create(
        self,
        name: str,
        packages: list[str],
        channels: list[str] | None = None,
    ) -> Path:
        """Create an isolated conda environment for a tool.

        Uses conda's solver backend (respects solver plugins like
        conda-rattler-solver) and installation APIs. Returns the
        prefix path.

        Raises *SolveError* if dependency resolution fails.
        """
        prefix = self.envs_dir / name
        prefix.mkdir(parents=True, exist_ok=True)

        channels = list(context.channels) if channels is None else list(channels)
        channel_objs = [Channel(c) for c in channels]
        specs = [MatchSpec(p) for p in packages]

        solver_backend = context.plugin_manager.get_cached_solver_backend()
        if solver_backend is None:
            raise SolveError(name, "no solver backend found")

        solver = solver_backend(
            str(prefix),
            channel_objs,
            context.subdirs,
            specs_to_add=specs,
        )

        try:
            transaction = solver.solve_for_transaction()
        except (UnsatisfiableError, SystemExit) as exc:
            raise SolveError(name, str(exc)) from exc

        transaction.download_and_extract()
        transaction.execute()

        return prefix

    def remove(self, name: str) -> None:
        """Remove a tool environment entirely."""
        prefix = self.envs_dir / name
        if prefix.exists():
            unregister_env(str(prefix))
            rm_rf(prefix)

    def exists(self, name: str) -> bool:
        """Check if a tool environment exists."""
        prefix = self.envs_dir / name
        return prefix.exists() and (prefix / "conda-meta").exists()
