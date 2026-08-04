"""Repository analysis and need detection."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
import logging

from github import GithubException

from agent.github_client import GitHubClient

LOGGER = logging.getLogger(__name__)
README_NAMES = {"README.md", "README.rst", "README.txt", "readme.md"}


@dataclass(frozen=True)
class RepositoryProfile:
    name: str
    full_name: str
    description: str
    language: str | None
    html_url: str
    homepage: str
    stars: int
    forks: int
    default_branch: str
    private: bool
    archived: bool
    fork: bool
    updated_at: datetime
    has_readme: bool
    root_files: set[str] = field(default_factory=set)
    needs: list[str] = field(default_factory=list)

    @property
    def score(self) -> int:
        score = 0
        if "readme" in self.needs:
            score += 5
        if "gitignore" in self.needs:
            score += 3
        if "ci" in self.needs:
            score += 2
        if "dependencies" in self.needs:
            score += 2
        if "tests" in self.needs:
            score += 2
        if "structure" in self.needs:
            score += 2
        if "progress" in self.needs:
            score += 1
        if self.description:
            score += 1
        return score


class RepoScanner:
    """Inspect repositories and return facts the activity engine can trust."""

    def __init__(self, client: GitHubClient):
        self.client = client

    def scan(self) -> list[RepositoryProfile]:
        profiles: list[RepositoryProfile] = []
        for repo in self.client.repositories():
            if repo.archived or repo.fork:
                LOGGER.debug("Skipping %s because it is archived or forked.", repo.name)
                continue
            try:
                profiles.append(self._profile(repo))
            except GithubException as exc:
                LOGGER.warning("Skipping %s after scan error: %s", repo.name, exc)
        return profiles

    def _profile(self, repo) -> RepositoryProfile:
        root_files = self._root_files(repo)
        has_readme = any(name in root_files for name in README_NAMES)
        needs: list[str] = []

        if not has_readme:
            needs.append("readme")
        if ".gitignore" not in root_files:
            needs.append("gitignore")
        if ".github" not in root_files and repo.language in {"Python", "JavaScript", "TypeScript"}:
            needs.append("ci")
        if repo.language == "Python" and "requirements.txt" not in root_files and "pyproject.toml" not in root_files:
            needs.append("dependencies")
        if repo.language == "Python" and "tests" not in root_files:
            needs.append("tests")
        if self._needs_structure(repo.language, root_files):
            needs.append("structure")
        if "CHANGELOG.md" not in root_files and "docs" not in root_files:
            needs.append("progress")

        return RepositoryProfile(
            name=repo.name,
            full_name=repo.full_name,
            description=repo.description or "",
            language=repo.language,
            html_url=repo.html_url,
            homepage=repo.homepage or "",
            stars=repo.stargazers_count,
            forks=repo.forks_count,
            default_branch=repo.default_branch,
            private=repo.private,
            archived=repo.archived,
            fork=repo.fork,
            updated_at=repo.updated_at.replace(tzinfo=timezone.utc),
            has_readme=has_readme,
            root_files=root_files,
            needs=needs,
        )

    def _root_files(self, repo) -> set[str]:
        try:
            contents = self.client._call(f"list root for {repo.name}", repo.get_contents, "")
        except GithubException as exc:
            if exc.status == 409:
                return set()
            raise
        return {item.name for item in contents}

    def _needs_structure(self, language: str | None, root_files: set[str]) -> bool:
        if language == "Python":
            return "src" not in root_files and not any(name.endswith(".py") for name in root_files)
        if language in {"JavaScript", "TypeScript"}:
            return "src" not in root_files and "package.json" in root_files
        return False
