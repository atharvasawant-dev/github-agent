"""Daily orchestration for the GitHub Automation Agent."""

from __future__ import annotations

import logging
import time

import schedule

from config import AgentConfig
from agent.activity_engine import ActivityEngine
from agent.github_client import GitHubClient
from agent.profile_engine import ProfileEngine
from agent.project_generator import ProjectGenerator
from agent.repo_scanner import RepoScanner

LOGGER = logging.getLogger(__name__)


class AgentScheduler:
    """Coordinate scanning, planning, and applying daily activity."""

    def __init__(self, config: AgentConfig, client: GitHubClient):
        self.config = config
        self.client = client
        self.scanner = RepoScanner(client)
        self.engine = ActivityEngine(config, client)
        self.generator = ProjectGenerator(config, client)
        self.profile_engine = ProfileEngine(config, client)

    def run_once(self) -> None:
        mode = "dry-run" if self.config.dry_run else "live"
        LOGGER.info("Starting one %s agent cycle.", mode)
        profiles = self.scanner.scan()
        LOGGER.info("Scanned %d eligible repositories.", len(profiles))

        if not self.config.prefer_existing_repos and self.config.allow_create_new_repos:
            self.generator.maybe_create({profile.name for profile in profiles})

        changes = []
        profile_change = self.profile_engine.build_change(profiles)
        if profile_change:
            changes.append(profile_change)

        remaining_budget = self.config.max_commits_per_day - len(changes)
        changes.extend(self.engine.plan(profiles, limit=remaining_budget))
        if not changes:
            LOGGER.info("No useful changes found for this cycle.")
            return

        changes = sorted(changes, key=lambda item: item.priority, reverse=True)
        for change in changes:
            LOGGER.info("Plan: %s -> %s (%s)", change.repo_name, change.message, change.summary)
        self.engine.apply(changes)
        LOGGER.info("Agent cycle complete.")

    def run_forever(self) -> None:
        schedule.every(self.config.schedule_interval_hours).hours.do(self.run_once)
        self.run_once()
        while True:
            schedule.run_pending()
            time.sleep(60)

    def print_status(self) -> None:
        profiles = self.scanner.scan()
        needs_readme = sum(1 for profile in profiles if "readme" in profile.needs)
        needs_polish = sum(1 for profile in profiles if profile.needs)
        public_repos = sum(1 for profile in profiles if not profile.private)
        LOGGER.info("Repositories scanned: %d", len(profiles))
        LOGGER.info("Public repositories available for profile features: %d", public_repos)
        LOGGER.info("Repositories missing README: %d", needs_readme)
        LOGGER.info("Repositories with useful maintenance work: %d", needs_polish)
        LOGGER.info("Profile builder enabled: %s", self.config.profile_building_enabled)
        LOGGER.info("Dry-run default: %s", self.config.dry_run)
