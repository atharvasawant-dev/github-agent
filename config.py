"""Configuration loading for the GitHub Automation Agent."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml
from dotenv import load_dotenv


VALID_INTENSITIES = {"conservative", "moderate", "active"}


@dataclass(frozen=True)
class AgentConfig:
    """Runtime configuration loaded from `.env`, environment, and YAML."""

    github_token: str
    dry_run: bool = True
    max_commits_per_day: int = 3
    activity_intensity: str = "moderate"
    profile_building_enabled: bool = True
    professional_headline: str = "Software developer focused on practical, production-minded engineering."
    profile_location: str = ""
    contact_email: str = ""
    linkedin_url: str = ""
    portfolio_url: str = ""
    featured_project_count: int = 6
    prefer_existing_repos: bool = True
    allow_create_new_repos: bool = False
    max_new_repositories: int = 3
    repository_allowlist: list[str] = field(default_factory=list)
    repository_blocklist: list[str] = field(default_factory=list)
    include_private_repos: bool = True
    require_recent_activity_days: int = 0
    schedule_interval_hours: int = 24
    log_level: str = "INFO"

    @classmethod
    def load(cls, path: str | Path = "config.yaml") -> "AgentConfig":
        """Load config from YAML and `GITHUB_TOKEN` from the environment."""

        load_dotenv()
        config_path = Path(path)
        raw: dict[str, Any] = {}
        if config_path.exists():
            with config_path.open("r", encoding="utf-8") as handle:
                raw = yaml.safe_load(handle) or {}

        token = os.getenv("GITHUB_TOKEN") or raw.get("github_token")
        if not token:
            raise ValueError(
                "GITHUB_TOKEN is missing. Add it to .env or your GitHub Actions secrets."
            )

        config = cls(
            github_token=token,
            dry_run=_as_bool(raw.get("dry_run", True)),
            max_commits_per_day=int(raw.get("max_commits_per_day", 3)),
            activity_intensity=str(raw.get("activity_intensity", "moderate")),
            profile_building_enabled=_as_bool(raw.get("profile_building_enabled", True)),
            professional_headline=str(
                raw.get(
                    "professional_headline",
                    "Software developer focused on practical, production-minded engineering.",
                )
            ),
            profile_location=str(raw.get("profile_location", "")),
            contact_email=str(raw.get("contact_email", "")),
            linkedin_url=str(raw.get("linkedin_url", "")),
            portfolio_url=str(raw.get("portfolio_url", "")),
            featured_project_count=int(raw.get("featured_project_count", 6)),
            prefer_existing_repos=_as_bool(raw.get("prefer_existing_repos", True)),
            allow_create_new_repos=_as_bool(raw.get("allow_create_new_repos", False)),
            max_new_repositories=int(raw.get("max_new_repositories", 3)),
            repository_allowlist=list(raw.get("repository_allowlist") or []),
            repository_blocklist=list(raw.get("repository_blocklist") or []),
            include_private_repos=_as_bool(raw.get("include_private_repos", True)),
            require_recent_activity_days=int(raw.get("require_recent_activity_days", 0)),
            schedule_interval_hours=int(raw.get("schedule_interval_hours", 24)),
            log_level=str(raw.get("log_level", "INFO")).upper(),
        )
        config.validate()
        return config

    def with_dry_run(self, dry_run: bool) -> "AgentConfig":
        """Return a copy with a CLI-supplied dry-run value."""

        values = self.__dict__.copy()
        values["dry_run"] = dry_run
        return AgentConfig(**values)

    def validate(self) -> None:
        """Validate configuration values with defensive defaults."""

        if self.activity_intensity not in VALID_INTENSITIES:
            raise ValueError(
                f"activity_intensity must be one of {sorted(VALID_INTENSITIES)}"
            )
        if self.max_commits_per_day < 1 or self.max_commits_per_day > 3:
            raise ValueError("max_commits_per_day must be between 1 and 3")
        if self.max_new_repositories < 0 or self.max_new_repositories > 3:
            raise ValueError("max_new_repositories must be between 0 and 3")
        if self.featured_project_count < 3 or self.featured_project_count > 10:
            raise ValueError("featured_project_count must be between 3 and 10")


def _as_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "on"}
    return bool(value)
