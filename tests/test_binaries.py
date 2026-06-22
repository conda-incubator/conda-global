"""Tests for binary discovery."""

from __future__ import annotations

import stat
import sys

import pytest
from conda.common.path import BIN_DIRECTORY

from conda_global.binaries import discover_binaries, discover_package_binaries, find_binary


@pytest.fixture
def unix_prefix(tmp_path, monkeypatch):
    """Create a fake prefix with its platform binary directory."""
    monkeypatch.setattr("conda_global.binaries.on_win", False)
    bin_dir = tmp_path / BIN_DIRECTORY
    bin_dir.mkdir()
    return tmp_path


def _make_executable(path):
    """Make a file executable."""
    path.write_bytes(b"#!/bin/sh\n")
    path.chmod(path.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)


def test_discover_binaries_empty_prefix(unix_prefix):
    result = discover_binaries(unix_prefix)
    assert result == []


@pytest.mark.skipif(sys.platform == "win32", reason="chmod +x is a no-op on Windows")
def test_discover_binaries_unix(unix_prefix):
    bin_dir = unix_prefix / BIN_DIRECTORY
    _make_executable(bin_dir / "gh")
    _make_executable(bin_dir / "ruff")
    (bin_dir / "not_executable").write_text("data")
    (bin_dir / "nested").mkdir()

    result = discover_binaries(unix_prefix)
    assert "gh" in result
    assert "ruff" in result
    assert "not_executable" not in result


def test_discover_binaries_no_bin_dir(tmp_path, monkeypatch):
    monkeypatch.setattr("conda_global.binaries.on_win", False)
    result = discover_binaries(tmp_path)
    assert result == []


def test_discover_binaries_windows_extensions(tmp_path, monkeypatch):
    monkeypatch.setattr("conda_global.binaries.on_win", True)
    bin_dir = tmp_path / BIN_DIRECTORY
    bin_dir.mkdir()
    for name in ("gh.exe", "ruff.bat", "pixi.cmd", "python"):
        (bin_dir / name).write_bytes(b"data")

    assert discover_binaries(tmp_path) == ["gh", "pixi", "ruff"]


@pytest.mark.skipif(sys.platform == "win32", reason="chmod +x is a no-op on Windows")
def test_discover_package_binaries_uses_package_files(unix_prefix, monkeypatch):
    class FakeRecord:
        files = [
            f"{BIN_DIRECTORY}/http",
            f"{BIN_DIRECTORY}/httpie",
            f"{BIN_DIRECTORY}/https",
            f"{BIN_DIRECTORY}/missing",
            f"{BIN_DIRECTORY}/not-executable",
            "lib/python.py",
        ]

    class FakePrefixData:
        def __init__(self, prefix):
            self.prefix = prefix

        def get(self, package, default=None):
            return FakeRecord()

    bin_dir = unix_prefix / BIN_DIRECTORY
    for name in ("http", "httpie", "https"):
        _make_executable(bin_dir / name)
    (bin_dir / "not-executable").write_text("data")
    _make_executable(bin_dir / "dependency-tool")
    monkeypatch.setattr("conda_global.binaries.PrefixData", FakePrefixData)

    assert discover_package_binaries(unix_prefix, "httpie") == [
        "http",
        "httpie",
        "https",
    ]


def test_discover_package_binaries_windows_extensions(tmp_path, monkeypatch):
    monkeypatch.setattr("conda_global.binaries.on_win", True)

    class FakeRecord:
        files = [
            f"{BIN_DIRECTORY}/http.exe",
            f"{BIN_DIRECTORY}/httpie.bat",
            f"{BIN_DIRECTORY}/https.cmd",
            f"{BIN_DIRECTORY}/python",
        ]

    class FakePrefixData:
        def __init__(self, prefix):
            self.prefix = prefix

        def get(self, package, default=None):
            return FakeRecord()

    bin_dir = tmp_path / BIN_DIRECTORY
    bin_dir.mkdir()
    for name in ("http.exe", "httpie.bat", "https.cmd", "python"):
        (bin_dir / name).write_bytes(b"data")
    monkeypatch.setattr("conda_global.binaries.PrefixData", FakePrefixData)

    assert discover_package_binaries(tmp_path, "httpie") == [
        "http",
        "httpie",
        "https",
    ]


def test_find_binary_no_bin_dir(tmp_path, monkeypatch):
    monkeypatch.setattr("conda_global.binaries.on_win", False)
    assert find_binary(tmp_path, "gh") is None


def test_find_binary_windows_extension(tmp_path, monkeypatch):
    monkeypatch.setattr("conda_global.binaries.on_win", True)
    bin_dir = tmp_path / BIN_DIRECTORY
    bin_dir.mkdir()
    binary = bin_dir / "gh.exe"
    binary.write_bytes(b"data")

    assert find_binary(tmp_path, "gh") == binary


@pytest.mark.parametrize(
    "name,create,expected_found",
    [
        pytest.param("gh", True, True, id="found"),
        pytest.param("nonexistent", False, False, id="not-found"),
    ],
)
def test_find_binary(unix_prefix, name, create, expected_found):
    if create:
        _make_executable(unix_prefix / BIN_DIRECTORY / name)
    result = find_binary(unix_prefix, name)
    if expected_found:
        assert result is not None
        assert result.name == name
    else:
        assert result is None
