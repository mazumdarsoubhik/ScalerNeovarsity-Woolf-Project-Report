from __future__ import annotations

from pathlib import Path


def _prompts_root() -> Path:
    """Return the root folder where meal parsing prompt versions are stored."""
    return Path(__file__).resolve().parent


def _read_prompt_file(version: str, filename: str) -> str:
    """Read one versioned prompt file from disk."""
    prompt_path = _prompts_root() / version / filename
    return prompt_path.read_text(encoding="utf-8").strip()


def get_system_prompt(version: str) -> str:
    """Load the system prompt for a version; fall back to v1 when missing."""
    try:
        return _read_prompt_file(version, "system.txt")
    except FileNotFoundError:
        return _read_prompt_file("v1", "system.txt")


def get_user_prompt_template(version: str) -> str:
    """Load the user prompt template for a version; fall back to v1 when missing."""
    try:
        return _read_prompt_file(version, "user_template.txt")
    except FileNotFoundError:
        return _read_prompt_file("v1", "user_template.txt")
