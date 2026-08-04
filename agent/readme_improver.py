"""README creation and light-touch improvement."""

from __future__ import annotations

from datetime import date

from agent.github_client import ChangeSet, GitHubClient
from agent.repo_scanner import RepositoryProfile


class ReadmeImprover:
    """Generate practical README content based on observed repository metadata."""

    def __init__(self, client: GitHubClient):
        self.client = client

    def build_change(self, profile: RepositoryProfile) -> ChangeSet | None:
        repo = self.client.try_get_repo(profile.name)
        if repo is None:
            return None
        existing = self.client.get_file_text(repo, "README.md")
        if existing and self._looks_complete(existing):
            return None

        content = self._improve_existing(profile, existing) if existing else self._new_readme(profile)
        return ChangeSet(
            repo_name=profile.name,
            files={"README.md": content},
            message="docs: improve project README",
            summary="Create or improve README with overview, setup, usage, and maintenance notes.",
        )

    def _looks_complete(self, content: str) -> bool:
        lowered = content.lower()
        sections = ["installation", "setup", "usage", "features", "architecture", "project structure"]
        return len(content) > 1000 and sum(section in lowered for section in sections) >= 4

    def _improve_existing(self, profile: RepositoryProfile, existing: str) -> str:
        additions: list[str] = []
        lowered = existing.lower()
        if "## overview" not in lowered:
            additions.append(f"## Overview\n\n{self._overview(profile)}\n")
        if "## setup" not in lowered and "## installation" not in lowered:
            additions.append(f"## Setup\n\n{self._setup(profile)}\n")
        if "## tech stack" not in lowered and "## technologies" not in lowered:
            additions.append(f"## Tech Stack\n\n{self._tech_stack(profile)}\n")
        if "## usage" not in lowered:
            additions.append(f"## Usage\n\n{self._usage(profile)}\n")
        if "## architecture" not in lowered:
            additions.append(f"## Architecture\n\n{self._architecture(profile)}\n")
        if "## validation" not in lowered and "## testing" not in lowered:
            additions.append(f"## Validation\n\n{self._validation(profile)}\n")
        if "## maintenance" not in lowered:
            additions.append(self._maintenance_note())

        if not additions:
            additions.append(self._maintenance_note())
        return existing.rstrip() + "\n\n" + "\n".join(additions).rstrip() + "\n"

    def _new_readme(self, profile: RepositoryProfile) -> str:
        title = profile.name.replace("-", " ").replace("_", " ").title()
        return (
            f"# {title}\n\n"
            f"{self._overview(profile)}\n\n"
            "## Features\n\n"
            f"{self._features(profile)}\n\n"
            "## Tech Stack\n\n"
            f"{self._tech_stack(profile)}\n\n"
            "## Setup\n\n"
            f"{self._setup(profile)}\n\n"
            "## Usage\n\n"
            f"{self._usage(profile)}\n\n"
            "## Architecture\n\n"
            f"{self._architecture(profile)}\n\n"
            "## Project Structure\n\n"
            f"{self._structure(profile)}\n\n"
            "## Validation\n\n"
            f"{self._validation(profile)}\n\n"
            "## Maintenance\n\n"
            "This repository is maintained with small, reviewable updates. Changes should keep setup steps current, avoid committing generated artifacts, and include tests or notes when behavior changes.\n"
        )

    def _overview(self, profile: RepositoryProfile) -> str:
        description = profile.description.strip()
        if description:
            return description
        language = profile.language or "the primary project language"
        return f"{profile.name} is a {language} repository focused on practical, maintainable project work."

    def _features(self, profile: RepositoryProfile) -> str:
        language = profile.language or "project"
        return (
            f"- Clear {language} project layout and ownership boundaries\n"
            "- Documented local setup path for repeatable development\n"
            "- Small commits that are easy to review and maintain\n"
            "- Space for tests, examples, CI, and architecture notes as the project grows"
        )

    def _tech_stack(self, profile: RepositoryProfile) -> str:
        stack = []
        if profile.language:
            stack.append(f"- Primary language: {profile.language}")
        if "requirements.txt" in profile.root_files or "pyproject.toml" in profile.root_files:
            stack.append("- Python dependency management")
        if "package.json" in profile.root_files:
            stack.append("- Node.js package scripts and dependency management")
        if ".github" in profile.root_files:
            stack.append("- GitHub Actions for automation")
        return "\n".join(stack) if stack else "- Stack details should be documented as implementation files are added."

    def _setup(self, profile: RepositoryProfile) -> str:
        if profile.language == "Python" or "requirements.txt" in profile.root_files:
            return (
                "```bash\n"
                "python -m venv .venv\n"
                ".venv\\Scripts\\activate  # Windows\n"
                "pip install -r requirements.txt\n"
                "```\n"
            )
        if profile.language in {"JavaScript", "TypeScript"} or "package.json" in profile.root_files:
            return "```bash\nnpm install\n```\n"
        return "Clone the repository, inspect the project files, and install the dependencies required by the detected stack.\n"

    def _usage(self, profile: RepositoryProfile) -> str:
        if profile.language == "Python":
            return "Run the main Python entry point or module for this repository after installing dependencies.\n"
        if profile.language in {"JavaScript", "TypeScript"}:
            return "Use the scripts in `package.json` for development, testing, and builds.\n"
        return "Use the repository-specific entry point documented in the source files.\n"

    def _architecture(self, profile: RepositoryProfile) -> str:
        if profile.language == "Python":
            return (
                "The project should keep source code, tests, and documentation separated. "
                "Prefer small modules with explicit responsibilities and avoid mixing runtime code with generated artifacts."
            )
        if profile.language in {"JavaScript", "TypeScript"}:
            return (
                "The project should keep application code in `src/`, shared utilities in clearly named modules, "
                "and validation/build scripts in `package.json`."
            )
        return (
            "The repository should keep implementation files, documentation, examples, and validation scripts in predictable locations."
        )

    def _structure(self, profile: RepositoryProfile) -> str:
        visible = sorted(name for name in profile.root_files if not name.startswith(".git"))[:8]
        if not visible:
            return "The repository is ready for source files, tests, and supporting documentation."
        return "Current top-level files and folders include: " + ", ".join(f"`{name}`" for name in visible) + "."

    def _validation(self, profile: RepositoryProfile) -> str:
        if profile.language == "Python":
            return "Run `python -m compileall .` for a syntax pass. When tests are present, run `pytest` before committing changes."
        if profile.language in {"JavaScript", "TypeScript"}:
            return "Run available `npm test` and `npm run build` scripts before committing changes."
        return "Run the repository-specific validation steps before merging changes."

    def _maintenance_note(self) -> str:
        return (
            "## Maintenance\n\n"
            f"Last documentation review: {date.today().isoformat()}. Keep this README aligned with the current setup, usage, and repository structure.\n"
        )
