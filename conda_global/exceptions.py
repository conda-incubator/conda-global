"""Exceptions for conda-global."""

from __future__ import annotations

from conda.exceptions import CondaError


class CondaGlobalError(CondaError):
    """Base exception for conda-global operations."""


class ToolNotFoundError(CondaGlobalError):
    """Raised when a tool environment does not exist."""

    def __init__(self, name: str, available: list[str] | None = None) -> None:
        self.error_message = f"tool environment '{name}' not found"
        self.hints: list[str] = []
        if available:
            self.hints.append(f"available tools: {', '.join(sorted(available))}")
        super().__init__(self.error_message)


class ToolExistsError(CondaGlobalError):
    """Raised when trying to install a tool that already exists."""

    def __init__(self, name: str) -> None:
        self.error_message = f"tool environment '{name}' already exists"
        self.hints = [
            "use 'conda global update' to update or 'conda global install --force' to reinstall"
        ]
        super().__init__(self.error_message)


class BinaryNotFoundError(CondaGlobalError):
    """Raised when an expected binary is not found in a tool environment."""

    def __init__(self, binary: str, env_name: str) -> None:
        self.error_message = f"binary '{binary}' not found in tool environment '{env_name}'"
        self.hints: list[str] = []
        super().__init__(self.error_message)


class EnvironmentArgumentError(CondaGlobalError):
    """Raised when an environment target is missing or ambiguous."""

    def __init__(self, message: str) -> None:
        self.error_message = message
        self.hints = ["use 'conda global uninstall <env>' or 'conda global uninstall -e <env>'"]
        super().__init__(self.error_message)


class SolveError(CondaGlobalError):
    """Raised when dependency resolution fails for a tool environment."""

    def __init__(self, name: str, detail: str) -> None:
        self.error_message = f"failed to solve environment for '{name}': {detail}"
        self.hints: list[str] = []
        super().__init__(self.error_message)


class ManifestError(CondaGlobalError):
    """Raised when the manifest file cannot be read or written."""

    def __init__(self, message: str) -> None:
        self.error_message = message
        self.hints: list[str] = []
        super().__init__(self.error_message)
