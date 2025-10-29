"""Video utilities for concatenating downloaded reels."""
from __future__ import annotations

import logging
import subprocess
import tempfile
from pathlib import Path
from typing import Iterable

LOGGER = logging.getLogger(__name__)


class VideoConcatenationError(RuntimeError):
    """Raised when FFmpeg fails to concatenate the downloaded reels."""


def ensure_ffmpeg_available() -> None:
    """Ensure that ffmpeg is installed and accessible."""

    try:
        subprocess.run(["ffmpeg", "-version"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except (OSError, subprocess.CalledProcessError) as exc:  # pragma: no cover - env specific
        raise VideoConcatenationError("ffmpeg is required to concatenate videos") from exc


def concatenate_videos(video_paths: Iterable[Path], output_path: Path, reencode: bool = False) -> Path:
    """Concatenate a sequence of videos into a single output file."""

    paths = [Path(path) for path in video_paths if Path(path).is_file()]
    if not paths:
        raise ValueError("No video files were provided for concatenation")

    ensure_ffmpeg_available()

    with tempfile.TemporaryDirectory() as temp_dir:
        list_file = Path(temp_dir) / "inputs.txt"
        with list_file.open("w", encoding="utf8") as handle:
            for path in paths:
                handle.write(f"file '{path.resolve()}'\n")

        cmd = [
            "ffmpeg",
            "-y",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            str(list_file),
        ]
        if reencode:
            cmd.extend(["-c:v", "libx264", "-c:a", "aac", "-movflags", "+faststart"])
        else:
            cmd.extend(["-c", "copy"])
        cmd.append(str(output_path))

        LOGGER.info("Running ffmpeg to concatenate %s videos", len(paths))
        process = subprocess.run(cmd, capture_output=True, text=True)
        if process.returncode != 0:
            LOGGER.error("ffmpeg failed: %s", process.stderr)
            raise VideoConcatenationError(process.stderr)

    LOGGER.info("Created compilation video at %s", output_path)
    return output_path


__all__ = ["concatenate_videos", "VideoConcatenationError", "ensure_ffmpeg_available"]
