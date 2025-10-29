# Reel From DM

A small utility that logs into Instagram, scans your direct messages for reels, downloads them, and produces a single compilation video. The project is built on top of [instagrapi](https://github.com/subzeroid/instagrapi) and requires a valid Instagram account.

> ⚠️ **Disclaimer:** Automating Instagram interaction may violate Instagram's terms of service. Use the tool responsibly and only with accounts that you control.

## Features

- Reuses cached sessions to minimise login prompts and checkpoints.
- Filters DM messages for shared reels and downloads the source videos.
- Supports resuming downloads if the script is re-run.
- Concatenates the collected reels into a single MP4 file using ffmpeg.

## Installation

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Configuration

The agent reads its configuration from environment variables. The most important ones are:

- `INSTAGRAM_USERNAME` – Instagram username (required)
- `INSTAGRAM_PASSWORD` – Instagram password (required unless a valid session file exists)
- `INSTAGRAM_SESSION_FILE` – Path to cache the session settings (optional)
- `DOWNLOAD_DIR` – Directory where downloaded reels are stored (`downloads` by default)
- `OUTPUT_PATH` – Location of the concatenated video (`reel_compilation.mp4` by default)
- `MAX_THREADS` – Maximum number of DM threads to inspect (default `20`)
- `MAX_MESSAGES_PER_THREAD` – Limit on messages per thread (optional)
- `INCLUDE_ARCHIVED` – Set to `true` to process archived threads
- `RESUME_DOWNLOADS` – If `true`, skip reels that are already present on disk

You can create an example `.env` file to document the configuration keys:

```bash
python -m reel_from_dm.cli --dump-env
```

## Usage

Once the environment variables are configured, run the agent via the CLI:

```bash
python -m reel_from_dm.cli -v --env .env
```

The script will login to Instagram, download the reels to `DOWNLOAD_DIR`, and produce `OUTPUT_PATH`. If ffmpeg cannot concatenate the reels via stream-copy, the tool automatically retries with re-encoding.

## Development Notes

- The CLI logs progress to stdout. Increase verbosity with `-vv` for debug logging.
- ffmpeg must be installed and available on your system `PATH`.
- Install [python-dotenv](https://github.com/theskumar/python-dotenv) if you want to load configuration from `.env` files.
