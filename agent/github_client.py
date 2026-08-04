"""Small reliability wrapper around PyGithub."""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Callable

from github import Github, GithubException
from github.InputGitTreeElement import InputGitTreeElement

from config import AgentConfig

LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True)
class ChangeSet:
    """A planned repository commit."""

    repo_name: str
    files: dict[str, str]
    message: str
    summary: str
    priority: int = 50


class GitHubClient:
    """Centralized GitHub API access, retries, and dry-run writes."""

    def __init__(self, config: AgentConfig):
        self.config = config
        self.github = Github(config.github_token, per_page=100)
        self.user = self._call("authenticate", self.github.get_user)
        LOGGER.info("Authenticated as %s", self.user.login)

    def repositories(self) -> list:
        repo_type = "all" if self.config.include_private_repos else "public"
        repos = list(self._call("list repositories", self.user.get_repos, type=repo_type))
        return [repo for repo in repos if self._is_allowed(repo.name)]

    def get_repo(self, repo_name: str):
        return self._call(f"load repository {repo_name}", self.user.get_repo, repo_name)

    def try_get_repo(self, repo_name: str):
        try:
            return self.get_repo(repo_name)
        except GithubException as exc:
            if exc.status == 404:
                return None
            raise

    def get_file_text(self, repo, path: str) -> str | None:
        try:
            content = self._call(f"read {repo.name}/{path}", repo.get_contents, path)
        except GithubException as exc:
            if exc.status == 404:
                return None
            raise
        if isinstance(content, list):
            return None
        if content.encoding == "base64":
            return content.decoded_content.decode("utf-8", errors="replace")
        return None

    def file_exists(self, repo, path: str) -> bool:
        try:
            self._call(f"check {repo.name}/{path}", repo.get_contents, path)
            return True
        except GithubException as exc:
            if exc.status == 404:
                return False
            raise

    def commit_files(self, change: ChangeSet) -> bool:
        """Create one commit containing all files in the change set."""

        if self.config.dry_run:
            LOGGER.info(
                "[dry-run] %s -> %s (%s)",
                change.repo_name,
                change.message,
                ", ".join(change.files),
            )
            return True

        repo = self.get_repo(change.repo_name)
        self._respect_rate_limit()
        branch = repo.get_branch(repo.default_branch)
        base_tree = repo.get_git_tree(branch.commit.sha)
        elements = [
            InputGitTreeElement(path=path, mode="100644", type="blob", content=content)
            for path, content in sorted(change.files.items())
        ]
        tree = repo.create_git_tree(elements, base_tree)
        commit = repo.create_git_commit(change.message, tree, [branch.commit.commit])
        ref = repo.get_git_ref(f"heads/{repo.default_branch}")
        ref.edit(commit.sha)
        LOGGER.info("Committed %s to %s", change.message, repo.full_name)
        return True

    def create_repository(self, name: str, description: str, files: dict[str, str]) -> bool:
        if self.config.dry_run:
            LOGGER.info("[dry-run] create repository %s with %d files", name, len(files))
            return True

        repo = self._call(
            f"create repository {name}",
            self.user.create_repo,
            name=name,
            description=description,
            private=False,
            auto_init=False,
        )
        first_path, first_content = next(iter(files.items()))
        repo.create_file(first_path, "chore: initialize project", first_content)
        remaining = dict(list(files.items())[1:])
        if remaining:
            self.commit_files(
                ChangeSet(
                    repo_name=name,
                    files=remaining,
                    message="chore: add initial project structure",
                    summary="Add the initial project scaffold.",
                )
            )
        return True

    def ensure_repository(
        self,
        name: str,
        description: str,
        private: bool = False,
        auto_init: bool = True,
    ) -> bool:
        """Ensure a repository exists without overwriting anything."""

        if self.try_get_repo(name) is not None:
            return True
        if self.config.dry_run:
            LOGGER.info("[dry-run] create repository %s", name)
            return True

        self._call(
            f"create repository {name}",
            self.user.create_repo,
            name=name,
            description=description,
            private=private,
            auto_init=auto_init,
        )
        LOGGER.info("Created repository %s", name)
        return True

    def _call(self, label: str, func: Callable, *args, **kwargs):
        delay = 2
        for attempt in range(1, 5):
            try:
                self._respect_rate_limit()
                return func(*args, **kwargs)
            except GithubException as exc:
                if exc.status in {403, 429, 500, 502, 503, 504} and attempt < 4:
                    LOGGER.warning("%s failed (%s). Retrying in %ss.", label, exc.status, delay)
                    time.sleep(delay)
                    delay *= 2
                    continue
                raise

    def _respect_rate_limit(self) -> None:
        try:
            rate_limit = self.github.get_rate_limit()
            core_limit = self._extract_core_rate_limit(rate_limit)
        except Exception as exc:
            LOGGER.debug("Could not inspect GitHub rate limit: %s", exc)
            return

        if core_limit is None:
            LOGGER.debug("GitHub rate limit response did not include a core bucket.")
            return

        remaining = self._read_int(core_limit, "remaining")
        reset_at = self._read_reset_timestamp(core_limit)
        if remaining is None:
            LOGGER.debug("GitHub core rate limit did not include remaining count.")
            return
        if remaining > 20:
            return

        if reset_at is None:
            LOGGER.warning(
                "GitHub rate limit is low (%s remaining), but reset time is unavailable.",
                remaining,
            )
            return

        wait_seconds = max(0, int(reset_at - time.time())) + 5
        LOGGER.warning(
            "GitHub rate limit is low (%s remaining). Waiting %s seconds.",
            remaining,
            wait_seconds,
        )
        time.sleep(wait_seconds)

    def _is_allowed(self, repo_name: str) -> bool:
        if self.config.repository_allowlist and repo_name not in self.config.repository_allowlist:
            return False
        return repo_name not in set(self.config.repository_blocklist)

    def _extract_core_rate_limit(self, rate_limit: Any) -> Any | None:
        """Return the core API bucket across PyGithub versions."""

        direct = self._read_attr_or_key(rate_limit, "core")
        if direct is not None:
            return direct

        resources = self._read_attr_or_key(rate_limit, "resources")
        if resources is not None:
            core = self._read_attr_or_key(resources, "core")
            if core is not None:
                return core

        raw_data = self._read_attr_or_key(rate_limit, "raw_data")
        if isinstance(raw_data, dict):
            resources = raw_data.get("resources", raw_data)
            if isinstance(resources, dict):
                return resources.get("core")

        return None

    def _read_attr_or_key(self, value: Any, name: str) -> Any | None:
        if isinstance(value, dict):
            return value.get(name)
        return getattr(value, name, None)

    def _read_int(self, value: Any, name: str) -> int | None:
        raw = self._read_attr_or_key(value, name)
        if raw is None:
            return None
        try:
            return int(raw)
        except (TypeError, ValueError):
            return None

    def _read_reset_timestamp(self, value: Any) -> float | None:
        reset = self._read_attr_or_key(value, "reset")
        if reset is None:
            reset = self._read_attr_or_key(value, "reset_at")
        if reset is None:
            reset = self._read_attr_or_key(value, "resetAt")

        if isinstance(reset, (int, float)):
            return float(reset)
        if isinstance(reset, datetime):
            if reset.tzinfo is None:
                reset = reset.replace(tzinfo=timezone.utc)
            return reset.timestamp()
        if isinstance(reset, str):
            try:
                return float(reset)
            except ValueError:
                try:
                    parsed = datetime.fromisoformat(reset.replace("Z", "+00:00"))
                    return parsed.timestamp()
                except ValueError:
                    return None
        return None
