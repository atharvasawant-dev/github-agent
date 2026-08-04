"""Professional GitHub profile README builder."""

from __future__ import annotations

import logging
from collections import Counter
from datetime import date

from config import AgentConfig
from agent.github_client import ChangeSet, GitHubClient
from agent.repo_scanner import RepositoryProfile

LOGGER = logging.getLogger(__name__)


class ProfileEngine:
    """Create and maintain the special `username/username` profile repository."""

    def __init__(self, config: AgentConfig, client: GitHubClient):
        self.config = config
        self.client = client

    def build_change(self, profiles: list[RepositoryProfile]) -> ChangeSet | None:
        if not self.config.profile_building_enabled:
            return None

        username = self.client.user.login
        self.client.ensure_repository(
            username,
            "Professional GitHub profile README maintained by the automation agent.",
            private=False,
            auto_init=True,
        )

        content = self._render(username, profiles)
        repo = self.client.try_get_repo(username)
        existing = self.client.get_file_text(repo, "README.md") if repo else None
        if existing and self._normalized(existing) == self._normalized(content):
            LOGGER.info("Profile README is already current.")
            return None

        return ChangeSet(
            repo_name=username,
            files={"README.md": content},
            message="docs: refresh professional GitHub profile",
            summary="Maintain the profile README with current focus, skills, featured projects, and stats.",
            priority=100,
        )

    def _render(self, username: str, profiles: list[RepositoryProfile]) -> str:
        visible = [profile for profile in profiles if not profile.private and profile.name != username]
        featured = self._featured_projects(visible)
        languages = self._languages(visible)
        skills = self._skill_badges(languages)
        project_rows = "\n".join(self._project_row(profile) for profile in featured)
        focus = self._focus_items(featured, languages)
        contact = self._contact_links()
        location = f"\n- Based in {self.config.profile_location}" if self.config.profile_location else ""

        return f"""# Hi, I'm {username}

{self.config.professional_headline}

I build practical software with an emphasis on readable code, reliable automation, clear documentation, and maintainable project structure. This profile is kept current with focused improvements across active repositories.{location}

## Current Focus

{focus}

## Skills and Tech Stack

{skills}

## Featured Projects

| Project | What it shows |
| --- | --- |
{project_rows}

## Engineering Habits

- Write small, reviewable commits with clear conventional messages.
- Keep READMEs, setup steps, and project structure aligned with the code.
- Prefer simple automation, useful tests, and reliable CI over flashy but fragile changes.
- Improve existing repositories before creating new ones.

## GitHub Activity

<p>
  <img height="165" src="https://github-readme-stats.vercel.app/api?username={username}&show_icons=true&theme=default&hide_border=true" alt="{username} GitHub stats" />
  <img height="165" src="https://github-readme-stats.vercel.app/api/top-langs/?username={username}&layout=compact&theme=default&hide_border=true" alt="{username} top languages" />
</p>

## Contact

{contact}

<!-- profile-builder:last-reviewed={date.today().isoformat()} -->
"""

    def _featured_projects(self, profiles: list[RepositoryProfile]) -> list[RepositoryProfile]:
        ranked = sorted(
            profiles,
            key=lambda item: (
                item.has_readme,
                bool(item.description),
                item.stars,
                item.forks,
                item.updated_at,
            ),
            reverse=True,
        )
        return ranked[: self.config.featured_project_count]

    def _languages(self, profiles: list[RepositoryProfile]) -> list[str]:
        counts = Counter(profile.language for profile in profiles if profile.language)
        return [language for language, _ in counts.most_common(8)]

    def _skill_badges(self, languages: list[str]) -> str:
        if not languages:
            languages = ["Python", "GitHub Actions", "Automation", "Documentation"]

        badge_map = {
            "Python": "Python-3776AB?style=for-the-badge&logo=python&logoColor=white",
            "JavaScript": "JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black",
            "TypeScript": "TypeScript-3178C6?style=for-the-badge&logo=typescript&logoColor=white",
            "HTML": "HTML5-E34F26?style=for-the-badge&logo=html5&logoColor=white",
            "CSS": "CSS3-1572B6?style=for-the-badge&logo=css3&logoColor=white",
            "Dart": "Dart-0175C2?style=for-the-badge&logo=dart&logoColor=white",
            "Java": "Java-007396?style=for-the-badge&logo=openjdk&logoColor=white",
            "C++": "C++-00599C?style=for-the-badge&logo=cplusplus&logoColor=white",
        }
        badges = []
        for language in languages:
            badge = badge_map.get(language)
            if badge:
                badges.append(f"![{language}](https://img.shields.io/badge/{badge})")
            else:
                safe = language.replace(" ", "%20")
                badges.append(f"![{language}](https://img.shields.io/badge/{safe}-555555?style=for-the-badge)")
        badges.extend(
            [
                "![Git](https://img.shields.io/badge/Git-F05032?style=for-the-badge&logo=git&logoColor=white)",
                "![GitHub Actions](https://img.shields.io/badge/GitHub%20Actions-2088FF?style=for-the-badge&logo=githubactions&logoColor=white)",
            ]
        )
        return " ".join(badges)

    def _project_row(self, profile: RepositoryProfile) -> str:
        title = profile.name.replace("-", " ").replace("_", " ").title()
        description = self._escape_table(profile.description or self._fallback_project_description(profile))
        stack = f" Built with {profile.language}." if profile.language else ""
        return f"| [{title}]({profile.html_url}) | {description}{stack} |"

    def _fallback_project_description(self, profile: RepositoryProfile) -> str:
        if profile.language == "Python":
            return "Python project with room for clear automation, tests, and documentation."
        if profile.language in {"JavaScript", "TypeScript"}:
            return "Web-oriented project focused on maintainable frontend or full-stack work."
        return "Maintained repository with ongoing structure and documentation improvements."

    def _focus_items(self, featured: list[RepositoryProfile], languages: list[str]) -> str:
        primary_stack = ", ".join(languages[:3]) if languages else "Python, automation, and documentation"
        project_names = ", ".join(profile.name for profile in featured[:3]) or "active repositories"
        return (
            f"- Strengthening project quality across {project_names}.\n"
            f"- Building practical experience in {primary_stack}.\n"
            "- Keeping repositories easy to run, understand, test, and maintain."
        )

    def _contact_links(self) -> str:
        links = ["- Open to collaboration on practical software, automation, and product-focused engineering."]
        if self.config.portfolio_url:
            links.append(f"- Portfolio: [{self.config.portfolio_url}]({self.config.portfolio_url})")
        if self.config.linkedin_url:
            links.append(f"- LinkedIn: [{self.config.linkedin_url}]({self.config.linkedin_url})")
        if self.config.contact_email:
            links.append(f"- Email: [{self.config.contact_email}](mailto:{self.config.contact_email})")
        return "\n".join(links)

    def _normalized(self, value: str) -> str:
        lines = [
            line
            for line in value.strip().splitlines()
            if not line.startswith("<!-- profile-builder:last-reviewed=")
        ]
        return "\n".join(lines).strip()

    def _escape_table(self, value: str) -> str:
        return value.replace("|", "\\|").replace("\n", " ").strip()
