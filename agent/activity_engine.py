"""Daily activity planning for meaningful repository maintenance."""

from __future__ import annotations

import logging
from datetime import datetime, timezone

from config import AgentConfig
from agent.github_client import ChangeSet, GitHubClient
from agent.readme_improver import ReadmeImprover
from agent.repo_polisher import RepoPolisher
from agent.repo_scanner import RepositoryProfile

LOGGER = logging.getLogger(__name__)


class ActivityEngine:
    """Select repositories and build a small number of useful commits."""

    def __init__(self, config: AgentConfig, client: GitHubClient):
        self.config = config
        self.client = client
        self.readmes = ReadmeImprover(client)
        self.polisher = RepoPolisher()

    def plan(self, profiles: list[RepositoryProfile], limit: int | None = None) -> list[ChangeSet]:
        eligible = self._eligible_profiles(profiles)
        target_count = self._target_count()
        if limit is not None:
            target_count = min(target_count, max(0, limit))

        changes: list[ChangeSet] = []
        for profile in eligible:
            if len(changes) >= target_count:
                break
            change = self._change_for(profile)
            if change:
                changes.append(change)

        LOGGER.info("Planned %d change(s).", len(changes))
        return changes

    def apply(self, changes: list[ChangeSet]) -> None:
        for change in sorted(changes, key=lambda item: item.priority, reverse=True)[
            : self.config.max_commits_per_day
        ]:
            self.client.commit_files(change)

    def _eligible_profiles(self, profiles: list[RepositoryProfile]) -> list[RepositoryProfile]:
        now = datetime.now(timezone.utc)
        filtered = []
        for profile in profiles:
            if profile.name == self.client.user.login:
                continue
            if not profile.needs:
                continue
            if self.config.require_recent_activity_days:
                age = (now - profile.updated_at).days
                if age < self.config.require_recent_activity_days:
                    continue
            filtered.append(profile)
        return sorted(filtered, key=lambda item: (-item.score, item.updated_at, item.name))

    def _target_count(self) -> int:
        if self.config.activity_intensity == "conservative":
            return 1
        if self.config.activity_intensity == "active":
            return 3
        return 2

    def _change_for(self, profile: RepositoryProfile) -> ChangeSet | None:
        if "readme" in profile.needs or profile.has_readme:
            readme_change = self.readmes.build_change(profile)
            if readme_change:
                return readme_change
        return self.polisher.build_change(profile)
