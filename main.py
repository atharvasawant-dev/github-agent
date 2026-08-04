"""Command line entry point for the GitHub Automation Agent."""

from __future__ import annotations

import argparse
import logging
import sys


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="A safe autonomous agent for steady GitHub repository maintenance."
    )
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--dry-run", action="store_true", help="Show planned changes only.")
    mode.add_argument("--run-once", action="store_true", help="Run one daily cycle.")
    mode.add_argument("--schedule", action="store_true", help="Run continuously.")
    mode.add_argument("--status", action="store_true", help="Show account and repo status.")
    parser.add_argument(
        "--config",
        default="config.yaml",
        help="Path to YAML config file. Defaults to config.yaml.",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable debug-level logging for troubleshooting.",
    )
    return parser


def configure_logging(level: str) -> None:
    logging.basicConfig(
        level=getattr(logging, level, logging.INFO),
        format="%(asctime)s %(levelname)s %(name)s - %(message)s",
    )


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    try:
        from config import AgentConfig
        from agent.github_client import GitHubClient
        from agent.scheduler import AgentScheduler

        config = AgentConfig.load(args.config)
        if args.dry_run:
            config = config.with_dry_run(True)
        elif args.run_once:
            config = config.with_dry_run(False)

        configure_logging("DEBUG" if args.verbose else config.log_level)

        client = GitHubClient(config)
        scheduler = AgentScheduler(config, client)

        if args.status:
            scheduler.print_status()
        elif args.schedule:
            scheduler.run_forever()
        else:
            # Default to dry-run so first execution is safe.
            if not args.run_once and not config.dry_run:
                config = config.with_dry_run(True)
                client = GitHubClient(config)
                scheduler = AgentScheduler(config, client)
            scheduler.run_once()
        return 0
    except KeyboardInterrupt:
        logging.getLogger(__name__).info("Stopped by user.")
        return 130
    except Exception as exc:
        logging.getLogger(__name__).error("Agent failed: %s", exc)
        return 1


if __name__ == "__main__":
    sys.exit(main())
