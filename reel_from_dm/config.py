"""Configuration helpers for the Reel-from-DM agent."""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, Optional

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover - optional dependency
    load_dotenv = None  # type: ignore


@dataclass(slots=True)
class InstagramAuth:
    """Instagram authentication options."""

    username: str
    password: Optional[str] = None
    session_file: Optional[Path] = None

    @classmethod
    def from_env(cls) -> "InstagramAuth":
        """Create credentials from environment variables.

        The following environment variables are used:
        - ``INSTAGRAM_USERNAME`` (required)
        - ``INSTAGRAM_PASSWORD`` (optional if a session file is supplied)
        - ``INSTAGRAM_SESSION_FILE`` (optional path)
        """

        username = os.getenv("INSTAGRAM_USERNAME")
        if not username:
            raise ValueError("INSTAGRAM_USERNAME is required")

        password = os.getenv("INSTAGRAM_PASSWORD") or None
        session_file_env = os.getenv("INSTAGRAM_SESSION_FILE")
        session_file = Path(session_file_env).expanduser() if session_file_env else None

        return cls(username=username, password=password, session_file=session_file)


@dataclass(slots=True)
class AgentOptions:
    """Runtime options for the compilation agent."""

    download_dir: Path = field(default_factory=lambda: Path("downloads"))
    output_path: Path = field(default_factory=lambda: Path("reel_compilation.mp4"))
    max_threads: int = 20
    max_messages_per_thread: Optional[int] = None
    include_archived: bool = False
    resume: bool = True

    @classmethod
    def from_env(cls) -> "AgentOptions":
        """Load agent options from environment variables."""

        download_dir = Path(os.getenv("DOWNLOAD_DIR", "downloads")).expanduser()
        output_path = Path(os.getenv("OUTPUT_PATH", "reel_compilation.mp4")).expanduser()
        max_threads_env = os.getenv("MAX_THREADS")
        max_threads = int(max_threads_env) if max_threads_env else 20
        max_messages_env = os.getenv("MAX_MESSAGES_PER_THREAD")
        max_messages = int(max_messages_env) if max_messages_env else None
        include_archived = os.getenv("INCLUDE_ARCHIVED", "false").lower() in {"1", "true", "yes"}
        resume = os.getenv("RESUME_DOWNLOADS", "true").lower() in {"1", "true", "yes"}

        return cls(
            download_dir=download_dir,
            output_path=output_path,
            max_threads=max_threads,
            max_messages_per_thread=max_messages,
            include_archived=include_archived,
            resume=resume,
        )


def load_env_files(paths: Iterable[str | os.PathLike[str]]) -> None:
    """Load environment variables from the provided .env files if python-dotenv is installed."""

    if load_dotenv is None:
        return

    for candidate in paths:
        path = Path(candidate)
        if path.is_file():
            load_dotenv(dotenv_path=path, override=False)


def dump_example_env(path: Path) -> None:
    """Write an example environment file that documents the configuration keys."""

    example = {
        "INSTAGRAM_USERNAME": "your_username",
        "INSTAGRAM_PASSWORD": "your_password",
        "INSTAGRAM_SESSION_FILE": "~/.instagram/session.json",
        "DOWNLOAD_DIR": "downloads",
        "OUTPUT_PATH": "reel_compilation.mp4",
        "MAX_THREADS": "20",
        "MAX_MESSAGES_PER_THREAD": "100",
        "INCLUDE_ARCHIVED": "false",
        "RESUME_DOWNLOADS": "true",
    }
    path.write_text("\n".join(f"{key}={value}" for key, value in example.items()) + "\n")


def save_session_settings(auth: InstagramAuth) -> dict:
    """Serialize the authentication settings for debugging purposes."""

    data = {
        "username": auth.username,
        "session_file": str(auth.session_file) if auth.session_file else None,
    }
    return json.loads(json.dumps(data))
