"""Lightweight repository health checks for github-agent."""

from pathlib import Path


def test_repository_has_documentation():
    """Ensure the repository keeps a visible project README."""
    root = Path(__file__).resolve().parents[1]
    readmes = ("README.md", "README.rst", "README.txt")

    assert any((root / name).exists() for name in readmes)
