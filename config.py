import os
from dotenv import load_dotenv
from typing import Optional


class Config:
    """Configuration management for GitHub automation agent."""

    def __init__(self):
        load_dotenv()
        self.github_token = self._get_github_token()

    def _get_github_token(self) -> str:
        """Get GitHub token from environment variables."""
        token = os.getenv("GITHUB_TOKEN")
        if not token:
            raise ValueError(
                "GITHUB_TOKEN not found in environment variables. Please set it in .env file."
            )
        return token

    @property
    def github_auth(self) -> tuple[str, str]:
        """Return GitHub authentication tuple for PyGithub."""
        return self.github_token, ""
