"""High level orchestration for downloading reels and building a compilation."""
from __future__ import annotations

import logging
from pathlib import Path

from .config import AgentOptions, InstagramAuth
from .instagram import InstagramDMClient
from .video import VideoConcatenationError, concatenate_videos

LOGGER = logging.getLogger(__name__)


class ReelCompilationAgent:
    """Coordinate the download of reels from Instagram DMs and build a compilation."""

    def __init__(self, auth: InstagramAuth, options: AgentOptions) -> None:
        self.auth = auth
        self.options = options
        self.client = InstagramDMClient(auth, options)

    def run(self) -> Path:
        """Execute the full pipeline and return the path to the compilation video."""

        LOGGER.info("Starting Reel compilation agent")
        self.client.login()

        download_root = self.options.download_dir
        download_root.mkdir(parents=True, exist_ok=True)

        videos = self.client.download_reels(download_root)
        if not videos:
            raise RuntimeError("No reels were found in the processed DM threads")

        output_path = self.options.output_path
        output_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            concatenate_videos(videos, output_path, reencode=False)
        except VideoConcatenationError:
            LOGGER.warning("Concatenation failed with direct copy; retrying with re-encode")
            concatenate_videos(videos, output_path, reencode=True)

        LOGGER.info("Completed Reel compilation at %s", output_path)
        return output_path


__all__ = ["ReelCompilationAgent"]
