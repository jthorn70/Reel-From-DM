"""Command line interface for the Reel-from-DM agent."""
from __future__ import annotations

import argparse
import logging

from .config import AgentOptions, InstagramAuth, dump_example_env, load_env_files, save_session_settings
from .reel_agent import ReelCompilationAgent

LOGGER = logging.getLogger(__name__)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Download Instagram reels from DMs and build a compilation")
    parser.add_argument("--env", action="append", default=[], help="Path to .env file with credentials")
    parser.add_argument(
        "--dump-env", action="store_true", help="Write an example .env file next to OUTPUT_PATH and exit"
    )
    parser.add_argument("--verbose", "-v", action="count", default=0, help="Increase logging verbosity")
    return parser


def configure_logging(level: int) -> None:
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    level = logging.WARNING
    if args.verbose == 1:
        level = logging.INFO
    elif args.verbose >= 2:
        level = logging.DEBUG
    configure_logging(level)

    if args.env:
        load_env_files(args.env)

    if args.dump_env:
        options = AgentOptions.from_env()
        dump_path = options.output_path.with_suffix(".env.example")
        dump_example_env(dump_path)
        LOGGER.info("Wrote example environment file to %s", dump_path)
        return 0

    auth = InstagramAuth.from_env()
    options = AgentOptions.from_env()

    LOGGER.debug("Using configuration: auth=%s options=%s", save_session_settings(auth), options)

    agent = ReelCompilationAgent(auth, options)
    agent.run()
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
