"""Tests for manifest read/write."""

from __future__ import annotations

import pytest

from conda_global.manifest import Manifest
from conda_global.models import ToolEnv


def test_load_empty_manifest(tmp_path):
    assert Manifest(tmp_path / "global.toml").load() == {}


def test_save_and_load_roundtrip(tmp_path):
    manifest = Manifest(tmp_path / "global.toml")
    tools = {
        "gh": ToolEnv(
            name="gh",
            channels=["conda-forge"],
            dependencies={"gh": "*"},
            exposed={"gh": "gh"},
        ),
        "ruff": ToolEnv(
            name="ruff",
            channels=["conda-forge"],
            dependencies={"ruff": ">=0.4"},
            exposed={"ruff": "ruff"},
        ),
    }
    manifest.save(tools)
    loaded = manifest.load()

    assert set(loaded.keys()) == {"gh", "ruff"}
    assert loaded["gh"].channels == ["conda-forge"]
    assert loaded["gh"].dependencies == {"gh": "*"}
    assert loaded["gh"].exposed == {"gh": "gh"}
    assert loaded["ruff"].dependencies == {"ruff": ">=0.4"}


def test_add(tmp_path):
    manifest = Manifest(tmp_path / "global.toml")
    manifest.add(
        ToolEnv(
            name="bat",
            channels=["conda-forge"],
            dependencies={"bat": "*"},
            exposed={"bat": "bat"},
        )
    )
    loaded = manifest.load()
    assert "bat" in loaded
    assert loaded["bat"].exposed == {"bat": "bat"}


def test_add_update_existing(tmp_path):
    manifest = Manifest(tmp_path / "global.toml")
    manifest.add(ToolEnv(name="gh", dependencies={"gh": "*"}))
    manifest.add(ToolEnv(name="gh", dependencies={"gh": ">=2.0"}, exposed={"gh": "gh"}))

    loaded = manifest.load()
    assert loaded["gh"].dependencies == {"gh": ">=2.0"}
    assert loaded["gh"].exposed == {"gh": "gh"}


def test_remove(tmp_path):
    manifest = Manifest(tmp_path / "global.toml")
    manifest.add(ToolEnv(name="gh", dependencies={"gh": "*"}))
    manifest.remove("gh")
    assert "gh" not in manifest.load()


def test_remove_nonexistent(tmp_path):
    manifest = Manifest(tmp_path / "global.toml")
    manifest.add(ToolEnv(name="gh", dependencies={"gh": "*"}))
    manifest.remove("nonexistent")
    assert "gh" in manifest.load()


@pytest.mark.parametrize("pinned", [True, False])
def test_pinned_roundtrip(tmp_path, pinned):
    manifest = Manifest(tmp_path / "global.toml")
    manifest.add(ToolEnv(name="gh", dependencies={"gh": "*"}, pinned=pinned))
    assert manifest.load()["gh"].pinned is pinned


@pytest.mark.parametrize(
    "deps,expected",
    [
        ({"gh": "*"}, {"gh": "*"}),
        ({"ruff": ">=0.4", "black": "*"}, {"ruff": ">=0.4", "black": "*"}),
        ({"numpy": ">=1.20,<2.0"}, {"numpy": ">=1.20,<2.0"}),
    ],
)
def test_dependency_formats(tmp_path, deps, expected):
    manifest = Manifest(tmp_path / "global.toml")
    manifest.add(ToolEnv(name="test", dependencies=deps))
    assert manifest.load()["test"].dependencies == expected


def test_multiple_channels(tmp_path):
    manifest = Manifest(tmp_path / "global.toml")
    manifest.add(
        ToolEnv(
            name="cuda_tool",
            channels=["nvidia", "conda-forge"],
            dependencies={"cuda-toolkit": "*"},
        )
    )
    assert manifest.load()["cuda_tool"].channels == ["nvidia", "conda-forge"]


def test_multiple_exposed_binaries(tmp_path):
    manifest = Manifest(tmp_path / "global.toml")
    manifest.add(
        ToolEnv(
            name="bat",
            dependencies={"bat": "*"},
            exposed={"bat": "bat", "batcat": "bat"},
        )
    )
    assert manifest.load()["bat"].exposed == {"bat": "bat", "batcat": "bat"}


def test_load_malformed_toml(tmp_path):
    path = tmp_path / "global.toml"
    path.write_text("[envs\nbroken = toml", encoding="utf-8")
    manifest = Manifest(path)
    with pytest.raises(Exception):
        manifest.load()


def test_load_empty_envs_table(tmp_path):
    path = tmp_path / "global.toml"
    path.write_text("[envs]\n", encoding="utf-8")
    assert Manifest(path).load() == {}


def test_creates_parent_dirs(tmp_path):
    path = tmp_path / "nested" / "dir" / "global.toml"
    manifest = Manifest(path)
    manifest.add(ToolEnv(name="gh", dependencies={"gh": "*"}))
    assert path.exists()
    assert "gh" in manifest.load()


def test_tools_sorted_in_output(tmp_path):
    manifest = Manifest(tmp_path / "global.toml")
    manifest.save(
        {
            "zoxide": ToolEnv(name="zoxide", dependencies={"zoxide": "*"}),
            "bat": ToolEnv(name="bat", dependencies={"bat": "*"}),
            "gh": ToolEnv(name="gh", dependencies={"gh": "*"}),
        }
    )
    content = manifest.path.read_text()
    assert content.index("bat") < content.index("gh") < content.index("zoxide")


def test_load_rejects_traversal_name(tmp_path):
    path = tmp_path / "global.toml"
    path.write_text('[envs."../evil"]\ndependencies = {evil = "*"}\n')
    with pytest.raises(ValueError, match="Invalid environment name"):
        Manifest(path).load()
