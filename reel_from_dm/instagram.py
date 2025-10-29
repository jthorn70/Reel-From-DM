"""Instagram client helpers built on top of :mod:`instagrapi`."""
from __future__ import annotations

import logging
import time
from pathlib import Path
from typing import Iterator, Optional

from instagrapi import Client
from instagrapi.exceptions import ClientError

from .config import AgentOptions, InstagramAuth

LOGGER = logging.getLogger(__name__)


class InstagramDMClient:
    """Wrapper around :class:`instagrapi.Client` with DM helper methods."""

    def __init__(self, auth: InstagramAuth, options: AgentOptions, login_retries: int = 3) -> None:
        self.auth = auth
        self.options = options
        self.login_retries = login_retries
        self.client = Client()

    # ------------------------------------------------------------------
    # Authentication helpers
    # ------------------------------------------------------------------
    def login(self) -> None:
        """Login to Instagram, optionally using a cached session."""

        if self.auth.session_file and Path(self.auth.session_file).is_file():
            LOGGER.info("Loading Instagram session from %s", self.auth.session_file)
            try:
                self.client.load_settings(str(self.auth.session_file))
                self.client.get_timeline_feed()
                LOGGER.info("Session file valid – skipping password login")
                return
            except ClientError:
                LOGGER.warning("Stored session is invalid; attempting password login")

        if not self.auth.password:
            raise ValueError("Password is required when no valid session file is available")

        for attempt in range(1, self.login_retries + 1):
            try:
                LOGGER.info("Logging into Instagram (attempt %s/%s)", attempt, self.login_retries)
                self.client.login(self.auth.username, self.auth.password)
                if self.auth.session_file:
                    Path(self.auth.session_file).parent.mkdir(parents=True, exist_ok=True)
                    self.client.dump_settings(str(self.auth.session_file))
                return
            except ClientError as exc:
                LOGGER.error("Instagram login failed: %s", exc)
                if attempt == self.login_retries:
                    raise
                time.sleep(attempt * 2)

    # ------------------------------------------------------------------
    # Fetch helpers
    # ------------------------------------------------------------------
    def iter_threads(self) -> Iterator:
        """Yield direct threads, including archived ones if configured."""

        LOGGER.info("Fetching direct threads (include archived=%s)", self.options.include_archived)
        amount = self.options.max_threads
        threads = self.client.direct_threads(amount=amount)
        for thread in threads:
            yield thread

        if self.options.include_archived:
            LOGGER.info("Fetching archived threads")
            for thread in self.client.direct_threads(selected_filter="archived", amount=amount):
                yield thread

    def iter_messages(self, thread, limit: Optional[int] = None) -> Iterator:
        """Iterate over messages in a thread respecting a limit."""

        messages = thread.messages
        count = 0
        for message in messages:
            yield message
            count += 1
            if limit and count >= limit:
                break

    # ------------------------------------------------------------------
    # Reel helpers
    # ------------------------------------------------------------------
    def extract_reel_pk_from_message(self, message) -> Optional[str]:
        """Return a clip primary key or URL from a DM message."""

        item_type = getattr(message, "item_type", None)
        if item_type == "clip":
            clip = getattr(message, "clip", None)
            return getattr(clip, "pk", None)
        if item_type == "media_share":
            media_share = getattr(message, "media_share", None)
            if getattr(media_share, "product_type", "") == "clips":
                return getattr(media_share, "pk", None)
        if item_type == "link":
            link = getattr(message, "link", None)
            url = getattr(link, "link_context", {}).get("link_url") if link else None
            if url and "instagram.com/reel/" in url:
                return url
        return None

    def download_reel(self, identifier: str, destination: Path) -> Optional[Path]:
        """Download a reel either by PK or URL."""

        destination.parent.mkdir(parents=True, exist_ok=True)
        try:
            if identifier.startswith("http"):
                LOGGER.info("Downloading reel from URL %s", identifier)
                path = self.client.clip_download_by_url(identifier, str(destination))
            else:
                LOGGER.info("Downloading reel with PK %s", identifier)
                path = self.client.clip_download(identifier, str(destination))
        except ClientError as exc:
            LOGGER.error("Failed to download reel %s: %s", identifier, exc)
            return None

        return Path(path)

    def download_reels_from_thread(self, thread, destination_dir: Path) -> list[Path]:
        """Download all reel messages from a thread to the destination directory."""

        downloaded: list[Path] = []
        for message in self.iter_messages(thread, limit=self.options.max_messages_per_thread):
            identifier = self.extract_reel_pk_from_message(message)
            if not identifier:
                continue

            filename = f"{getattr(message, 'item_id', int(time.time()))}.mp4"
            target = destination_dir / filename
            if self.options.resume and target.exists():
                LOGGER.info("Skipping existing download %s", target)
                downloaded.append(target)
                continue

            result = self.download_reel(identifier, target)
            if result:
                downloaded.append(result)
        return downloaded

    def download_reels(self, destination_dir: Path) -> list[Path]:
        """Download reels from all fetched threads."""

        all_downloads: list[Path] = []
        for thread in self.iter_threads():
            thread_dir = destination_dir / thread.id
            LOGGER.info("Processing thread %s", thread.thread_title)
            downloads = self.download_reels_from_thread(thread, thread_dir)
            all_downloads.extend(downloads)
        return all_downloads


__all__ = ["InstagramDMClient"]
