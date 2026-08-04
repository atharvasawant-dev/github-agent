"""Optional high-quality project creation."""

from __future__ import annotations

from config import AgentConfig
from agent.github_client import GitHubClient


class ProjectGenerator:
    """Create a small capped number of starter repositories when enabled."""

    def __init__(self, config: AgentConfig, client: GitHubClient):
        self.config = config
        self.client = client

    def maybe_create(self, existing_names: set[str]) -> None:
        if not self.config.allow_create_new_repos:
            return

        created = 0
        for name, description, files in self._templates():
            if created >= self.config.max_new_repositories:
                return
            if name in existing_names:
                continue
            self.client.create_repository(name, description, files)
            created += 1

    def _templates(self):
        yield (
            "python-maintenance-toolkit",
            "A small Python toolkit for repository health checks and maintenance notes.",
            {
                "README.md": "# Python Maintenance Toolkit\n\nA compact CLI-style toolkit for checking repository health and creating maintenance notes.\n",
                "requirements.txt": "pytest>=8.0.0\n",
                "maintenance.py": (
                    '"""Repository maintenance helpers."""\n\n'
                    "from pathlib import Path\n\n\n"
                    "def has_readme(path: str = '.') -> bool:\n"
                    '    """Return True when a project has a root README file."""\n'
                    "    root = Path(path)\n"
                    "    return any((root / name).exists() for name in ('README.md', 'README.rst', 'README.txt'))\n"
                ),
                "tests/test_maintenance.py": (
                    "from maintenance import has_readme\n\n\n"
                    "def test_has_readme_detects_missing_file(tmp_path):\n"
                    "    assert has_readme(tmp_path) is False\n"
                ),
            },
        )
