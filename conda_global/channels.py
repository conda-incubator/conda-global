"""Channel helpers."""

from __future__ import annotations

from conda.base.context import context, reset_context


def resolve_channels(channels: list[str] | None = None) -> list[str]:
    """Return explicit channels or conda's configured channel list."""
    if channels:
        return list(channels)
    if not context.channels:
        reset_context()
    return list(context.channels)
