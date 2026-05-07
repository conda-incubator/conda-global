"""Read and write the global manifest (~/.conda/global.toml)."""

from __future__ import annotations

from typing import TYPE_CHECKING

import tomlkit

from .models import ToolEnv, validate_name
from .paths import manifest_path as _default_manifest_path

if TYPE_CHECKING:
    from pathlib import Path


class Manifest:
    """Manages the global tool manifest file.

    Usage::

        manifest = Manifest()                        # ~/.conda/global.toml
        manifest = Manifest(tmp / "manifest.toml")  # test path

        tools = manifest.load()
        manifest.add(tool)
        manifest.remove("gh")
    """

    def __init__(self, path: Path | None = None) -> None:
        self.path = path or _default_manifest_path()

    def load(self) -> dict[str, ToolEnv]:
        """Load tool environments from the manifest.

        Returns an empty dict if the file does not exist.
        """
        if not self.path.exists():
            return {}

        text = self.path.read_text(encoding="utf-8")
        doc = tomlkit.parse(text)
        envs_table = doc.get("envs", {})

        result: dict[str, ToolEnv] = {}
        for name, data in envs_table.items():
            validate_name(name, kind="environment")
            for exposed_name in data.get("exposed", {}):
                validate_name(exposed_name, kind="exposed binary")
            result[name] = ToolEnv(
                name=name,
                channels=list(data.get("channels", ["conda-forge"])),
                dependencies=dict(data.get("dependencies", {})),
                exposed=dict(data.get("exposed", {})),
                pinned=bool(data.get("pinned", False)),
            )
        return result

    def save(self, tools: dict[str, ToolEnv]) -> None:
        """Write tool environments to the manifest.

        Creates the parent directory if needed.
        """
        self.path.parent.mkdir(parents=True, exist_ok=True)

        doc = tomlkit.document()
        envs_table = tomlkit.table(is_super_table=True)

        for name in sorted(tools):
            tool = tools[name]
            entry = tomlkit.table()
            entry.add("channels", tool.channels)
            entry.add("dependencies", tool.dependencies)
            if tool.exposed:
                entry.add("exposed", tool.exposed)
            if tool.pinned:
                entry.add("pinned", True)
            envs_table.add(name, entry)

        doc.add("envs", envs_table)
        self.path.write_text(tomlkit.dumps(doc), encoding="utf-8")

    def add(self, tool: ToolEnv) -> None:
        """Add or update a tool in the manifest."""
        tools = self.load()
        tools[tool.name] = tool
        self.save(tools)

    def remove(self, name: str) -> None:
        """Remove a tool from the manifest."""
        tools = self.load()
        tools.pop(name, None)
        self.save(tools)
