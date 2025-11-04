"""Utility to load environment variables from a .env file."""

from typing import Optional
from pathlib import Path
from os import environ


def load_env(env_path: Optional[str] = None) -> None:
    """Load environment variables from a .env file into ``os.environ``.

    This is a minimal parser that reads lines in the form ``KEY=VALUE`` and sets
    environment variables using :pyfunc:`os.environ.setdefault` so existing
    environment values are preserved.

    Args:
        env_path: Optional path to a .env file. If ``None``, the function will look
            for a ``.env`` file in the project root (two levels up from this file).

    Returns:
        None
    """
    if env_path is None:
        env_path = Path(__file__).resolve().parents[1] / ".env"  # project root
    env_file = Path(env_path)
    if not env_file.exists():
        return
    with env_file.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                continue
            key, val = line.split("=", 1)
            key = key.strip()
            val = val.strip().strip("'\"")
            environ.setdefault(key, val)
