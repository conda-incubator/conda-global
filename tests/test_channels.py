"""Tests for channel resolution."""

from __future__ import annotations

from types import SimpleNamespace

from conda_global.channels import resolve_channels


def test_resolve_channels_returns_explicit_channels():
    assert resolve_channels(["nvidia", "conda-forge"]) == ["nvidia", "conda-forge"]


def test_resolve_channels_uses_conda_context(monkeypatch):
    configured = ["https://repo.anaconda.com/pkgs/main"]
    monkeypatch.setattr(
        "conda_global.channels.context",
        SimpleNamespace(channels=configured),
    )
    assert resolve_channels() == configured
