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

### Windows setup with Visual Studio Code

Follow the checklist below when running the project from the VS Code **PowerShell** terminal on Windows:

1. **Install prerequisites.**
   - Install [Python 3.11+](https://www.python.org/downloads/windows/) and ensure the *Add python.exe to PATH* checkbox is selected during setup.
   - Install [ffmpeg](https://ffmpeg.org/download.html) (required for concatenation). An easy option is `winget install --id=Gyan.FFmpeg` or `choco install ffmpeg` if you already use Chocolatey.
2. **Open the project in VS Code and launch a terminal.**
   - Use <kbd>Ctrl</kbd>+<kbd>Shift</kbd>+<kbd>`</kbd> to open a new integrated terminal (PowerShell by default).
   - Ensure the terminal is rooted at the repository folder (the one containing `README.md`):
     ```powershell
     Set-Location C:\path\to\Reel-From-DM
     ```
   - Confirm Python is available: `python --version` should print the interpreter version.
3. **Create and activate a virtual environment.**
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```
   If PowerShell blocks script execution, enable it for the current session first:
   ```powershell
   Set-ExecutionPolicy -Scope Process RemoteSigned
   ```
4. **Install the project (adds it to the environment path) and dependencies.**
   ```powershell
   pip install --upgrade pip
   pip install -r requirements.txt
   pip install -e .
   ```
5. **Configure credentials and paths.** Either export them inline for the session or create a `.env` file:
   ```powershell
   $env:INSTAGRAM_USERNAME = "your_username"
   $env:INSTAGRAM_PASSWORD = "your_password"
   $env:DOWNLOAD_DIR = "C:\\path\\to\\downloads"   # optional override
   $env:OUTPUT_PATH = "C:\\path\\to\\reel_compilation.mp4"  # optional override
   ```
   You can generate a `.env` template with:
   ```powershell
   python -m reel_from_dm.cli --dump-env > .env
   ```
6. **Run the agent.**
   ```powershell
   python -m reel_from_dm.cli -v --env .env
   ```
   The CLI logs progress to the terminal and produces the concatenated video at `OUTPUT_PATH` when it finishes.

> 💡 Tip: To rerun the workflow later, reopen VS Code, run `.\.venv\Scripts\Activate.ps1`, and repeat steps 5–6.

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
