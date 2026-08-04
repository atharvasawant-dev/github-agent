"""Small repository hygiene improvements."""

from __future__ import annotations

from datetime import date

from agent.github_client import ChangeSet
from agent.repo_scanner import RepositoryProfile


class RepoPolisher:
    """Create safe, additive improvements without deleting user content."""

    def build_change(self, profile: RepositoryProfile) -> ChangeSet | None:
        files: dict[str, str] = {}
        messages: list[str] = []

        if "gitignore" in profile.needs:
            files[".gitignore"] = self._gitignore(profile)
            messages.append(".gitignore")
        elif "ci" in profile.needs:
            files[".github/workflows/ci.yml"] = self._ci(profile)
            messages.append("CI workflow")
        elif "dependencies" in profile.needs:
            files["requirements.txt"] = self._requirements(profile)
            messages.append("Python dependency manifest")
        elif "tests" in profile.needs:
            files["tests/test_repository_health.py"] = self._python_health_test(profile)
            messages.append("repository health test")
        elif "structure" in profile.needs:
            files.update(self._structure_files(profile))
            messages.append("project structure")
        elif "progress" in profile.needs:
            files["docs/progress.md"] = self._progress_note(profile)
            messages.append("progress notes")

        if not files:
            return None

        return ChangeSet(
            repo_name=profile.name,
            files=files,
            message=self._commit_message(files),
            summary=f"Add {', '.join(messages)}.",
        )

    def _commit_message(self, files: dict[str, str]) -> str:
        if ".github/workflows/ci.yml" in files:
            return "ci: add basic validation workflow"
        if "tests/test_repository_health.py" in files:
            return "test: add repository health checks"
        if "requirements.txt" in files:
            return "chore: add Python dependency manifest"
        if "docs/architecture.md" in files:
            return "chore: add maintainable project structure"
        if ".gitignore" in files:
            return "chore: add project gitignore"
        return "docs: add project progress notes"

    def _gitignore(self, profile: RepositoryProfile) -> str:
        common = ".env\n.env.*\n!.env.example\n.DS_Store\nThumbs.db\n.vscode/\n.idea/\n"
        if profile.language == "Python":
            return common + "\n__pycache__/\n*.py[cod]\n.venv/\nvenv/\n.pytest_cache/\n.coverage\nhtmlcov/\nbuild/\ndist/\n*.egg-info/\n"
        if profile.language in {"JavaScript", "TypeScript"}:
            return common + "\nnode_modules/\ndist/\nbuild/\ncoverage/\n.next/\n.vite/\n"
        return common + "\nlogs/\ntmp/\n"

    def _ci(self, profile: RepositoryProfile) -> str:
        if profile.language == "Python":
            return """name: CI

on:
  push:
  pull_request:

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          if [ -f requirements.txt ]; then pip install -r requirements.txt; fi
          pip install pytest
      - name: Run tests when present
        run: |
          if [ -d tests ]; then pytest; else python -m compileall .; fi
"""
        return """name: CI

on:
  push:
  pull_request:

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: "20"
      - name: Install dependencies
        run: npm install
      - name: Run available checks
        run: |
          npm test --if-present
          npm run build --if-present
"""

    def _progress_note(self, profile: RepositoryProfile) -> str:
        return (
            "# Progress Notes\n\n"
            f"## {date.today().isoformat()}\n\n"
            "- Reviewed repository structure and documentation status.\n"
            "- Identified small maintenance tasks that can be completed in focused commits.\n"
            "- Next good step: add or refresh tests around the main behavior.\n"
        )

    def _python_health_test(self, profile: RepositoryProfile) -> str:
        return f'''"""Lightweight repository health checks for {profile.name}."""

from pathlib import Path


def test_repository_has_documentation():
    """Ensure the repository keeps a visible project README."""
    root = Path(__file__).resolve().parents[1]
    readmes = ("README.md", "README.rst", "README.txt")

    assert any((root / name).exists() for name in readmes)
'''

    def _requirements(self, profile: RepositoryProfile) -> str:
        return (
            "# Runtime dependencies\n"
            "# Add project dependencies here as the codebase grows.\n\n"
            "# Development and validation\n"
            "pytest>=8.0.0\n"
        )

    def _structure_files(self, profile: RepositoryProfile) -> dict[str, str]:
        return {
            "src/.gitkeep": "",
            "tests/.gitkeep": "",
            "docs/architecture.md": (
                f"# {profile.name} Architecture\n\n"
                "## Overview\n\n"
                "This document captures the intended project structure and maintenance approach.\n\n"
                "## Layout\n\n"
                "- `src/` contains implementation code.\n"
                "- `tests/` contains automated checks and regression tests.\n"
                "- `docs/` contains design notes, architecture notes, and operational context.\n\n"
                "## Maintenance Notes\n\n"
                "Keep changes small, documented, and easy to review. Add tests when behavior changes.\n"
            ),
        }
