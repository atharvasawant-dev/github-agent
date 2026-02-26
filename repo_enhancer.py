#!/usr/bin/env python3
"""
Repository Enhancer Module
Enhances existing repositories with professional structure and CI/CD.
"""

import os
import logging
from typing import Dict, List, Any, Optional
from github import Github, GithubException
from github.ContentFile import ContentFile


class RepositoryEnhancer:
    """Enhances repositories with professional structure and workflows."""

    def __init__(self, github_client: Github):
        self.github = github_client
        self.user = None
        self._setup_logging()

    def _setup_logging(self) -> None:
        """Set up logging for the enhancer."""
        logging.basicConfig(
            level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
        )
        self.logger = logging.getLogger(__name__)

    def authenticate(self) -> bool:
        """Authenticate with GitHub."""
        try:
            self.user = self.github.get_user()
            self.logger.info(f"Authenticated as: {self.user.login}")
            return True
        except GithubException as e:
            self.logger.error(f"Authentication failed: {e}")
            return False

    def enhance_repository(self, repo_name: str) -> Dict[str, Any]:
        """
        Enhance a repository with professional structure.

        Args:
            repo_name: Name of the repository to enhance

        Returns:
            Dictionary with enhancement results
        """
        result = {
            "success": False,
            "repo_name": repo_name,
            "enhancements": [],
            "errors": [],
        }

        try:
            if not self.user:
                if not self.authenticate():
                    result["errors"].append("Authentication failed")
                    return result

            repo = self.user.get_repo(repo_name)
            self.logger.info(f"Enhancing repository: {repo_name}")

            # Add .gitignore if missing
            if self._should_add_gitignore(repo):
                self._add_gitignore(repo)
                result["enhancements"].append("Added .gitignore")

            # Add CI/CD workflow if missing
            if self._should_add_cicd(repo):
                self._add_cicd_workflow(repo)
                result["enhancements"].append("Added GitHub Actions CI/CD")

            # Add requirements.txt if Python project and missing
            if self._is_python_project(repo) and self._should_add_requirements(repo):
                self._add_requirements_txt(repo)
                result["enhancements"].append("Added requirements.txt")

            # Add setup.py if Python project and missing
            if self._is_python_project(repo) and self._should_add_setup(repo):
                self._add_setup_py(repo)
                result["enhancements"].append("Added setup.py")

            # Create basic directory structure if missing
            structure_added = self._create_directory_structure(repo)
            if structure_added:
                result["enhancements"].extend(structure_added)

            result["success"] = True
            self.logger.info(f"Successfully enhanced {repo_name}")

        except GithubException as e:
            error_msg = f"GitHub API error for {repo_name}: {e}"
            self.logger.error(error_msg)
            result["errors"].append(error_msg)
        except Exception as e:
            error_msg = f"Unexpected error for {repo_name}: {e}"
            self.logger.error(error_msg)
            result["errors"].append(error_msg)

        return result

    def _should_add_gitignore(self, repo) -> bool:
        """Check if .gitignore should be added."""
        try:
            repo.get_contents(".gitignore")
            return False
        except GithubException as e:
            if e.status == 404:
                return True
            return False

    def _add_gitignore(self, repo) -> None:
        """Add a comprehensive .gitignore file."""
        gitignore_content = """# Byte-compiled / optimized / DLL files
__pycache__/
*.py[cod]
*$py.class

# C extensions
*.so

# Distribution / packaging
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
pip-wheel-metadata/
share/python-wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# PyInstaller
*.manifest
*.spec

# Installer logs
pip-log.txt
pip-delete-this-directory.txt

# Unit test / coverage reports
htmlcov/
.tox/
.nox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
*.py,cover
.hypothesis/
.pytest_cache/

# Translations
*.mo
*.pot

# Django stuff:
*.log
local_settings.py
db.sqlite3
db.sqlite3-journal

# Flask stuff:
instance/
.webassets-cache

# Scrapy stuff:
.scrapy

# Sphinx documentation
docs/_build/

# PyBuilder
target/

# Jupyter Notebook
.ipynb_checkpoints

# IPython
profile_default/
ipython_config.py

# pyenv
.python-version

# pipenv
Pipfile.lock

# PEP 582
__pypackages__/

# Celery stuff
celerybeat-schedule
celerybeat.pid

# SageMath parsed files
*.sage.py

# Environments
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# Spyder project settings
.spyderproject
.spyproject

# Rope project settings
.ropeproject

# mkdocs documentation
/site

# mypy
.mypy_cache/
.dmypy.json
dmypy.json

# Pyre type checker
.pyre/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db
"""

        repo.create_file(
            path=".gitignore",
            message="Add comprehensive .gitignore",
            content=gitignore_content,
            branch=repo.default_branch,
        )

    def _should_add_cicd(self, repo) -> bool:
        """Check if CI/CD workflow should be added."""
        try:
            repo.get_contents(".github/workflows/ci.yml")
            return False
        except GithubException as e:
            if e.status == 404:
                return True
            return False

    def _add_cicd_workflow(self, repo) -> None:
        """Add GitHub Actions CI/CD workflow."""
        workflow_content = """name: CI/CD Pipeline

on:
  push:
    branches: [ main, master ]
  pull_request:
    branches: [ main, master ]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.8, 3.9, '3.10', '3.11']

    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        if [ -f requirements.txt ]; then pip install -r requirements.txt; fi
        if [ -f requirements-dev.txt ]; then pip install -r requirements-dev.txt; fi
    
    - name: Lint with flake8
      run: |
        pip install flake8
        flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
        flake8 . --count --exit-zero --max-complexity=10 --max-line-length=88 --statistics
    
    - name: Run tests
      run: |
        if [ -d "tests" ]; then
          python -m pytest tests/ -v
        else
          echo "No tests directory found, skipping tests"
        fi
    
    - name: Check code formatting
      run: |
        pip install black
        black --check .
"""

        # Create .github/workflows directory structure
        try:
            repo.create_file(
                path=".github/workflows/ci.yml",
                message="Add GitHub Actions CI/CD pipeline",
                content=workflow_content,
                branch=repo.default_branch,
            )
        except GithubException as e:
            # Directory might not exist, try creating it
            if e.status == 404:
                repo.create_file(
                    path=".github/workflows/.gitkeep",
                    message="Create workflows directory",
                    content="",
                    branch=repo.default_branch,
                )
                repo.create_file(
                    path=".github/workflows/ci.yml",
                    message="Add GitHub Actions CI/CD pipeline",
                    content=workflow_content,
                    branch=repo.default_branch,
                )

    def _is_python_project(self, repo) -> bool:
        """Check if repository is a Python project."""
        try:
            # Check for Python files
            contents = repo.get_contents("")
            for content in contents:
                if content.name.endswith(".py"):
                    return True
                if content.name in ["setup.py", "requirements.txt", "pyproject.toml"]:
                    return True
            return False
        except GithubException:
            return False

    def _should_add_requirements(self, repo) -> bool:
        """Check if requirements.txt should be added."""
        try:
            repo.get_contents("requirements.txt")
            return False
        except GithubException as e:
            if e.status == 404:
                return True
            return False

    def _add_requirements_txt(self, repo) -> None:
        """Add basic requirements.txt for Python projects."""
        requirements_content = """# Core dependencies
requests>=2.28.0
click>=8.0.0
pydantic>=1.10.0

# Development dependencies
pytest>=7.0.0
pytest-cov>=4.0.0
black>=22.0.0
flake8>=5.0.0
mypy>=0.991

# Optional dependencies
python-dotenv>=0.19.0
"""

        repo.create_file(
            path="requirements.txt",
            message="Add requirements.txt with common dependencies",
            content=requirements_content,
            branch=repo.default_branch,
        )

    def _should_add_setup(self, repo) -> bool:
        """Check if setup.py should be added."""
        try:
            repo.get_contents("setup.py")
            repo.get_contents("pyproject.toml")
            return False
        except GithubException as e:
            if e.status == 404:
                return True
            return False

    def _add_setup_py(self, repo) -> None:
        """Add setup.py for Python projects."""
        setup_content = """from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="{}",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="A professional Python project",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/{}/{}",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={{
        "console_scripts": [
            "{}={}.__main__:main",
        ],
    }},
)
""".format(repo.name, self.user.login, repo.name, repo.name.replace("-", "_"))

        repo.create_file(
            path="setup.py",
            message="Add setup.py for package distribution",
            content=setup_content,
            branch=repo.default_branch,
        )

    def _create_directory_structure(self, repo) -> List[str]:
        """Create basic directory structure."""
        enhancements = []

        directories = ["src", "tests", "docs", "examples"]

        for directory in directories:
            try:
                repo.get_contents(directory)
            except GithubException as e:
                if e.status == 404:
                    repo.create_file(
                        path=f"{directory}/.gitkeep",
                        message=f"Create {directory} directory",
                        content="",
                        branch=repo.default_branch,
                    )
                    enhancements.append(f"Created {directory}/ directory")

        return enhancements

    def batch_enhance_repositories(self, repo_names: List[str]) -> Dict[str, Any]:
        """Enhance multiple repositories."""
        results = {
            "total": len(repo_names),
            "successful": 0,
            "failed": 0,
            "details": [],
        }

        self.logger.info(
            f"Starting batch enhancement for {len(repo_names)} repositories"
        )

        for repo_name in repo_names:
            result = self.enhance_repository(repo_name)
            results["details"].append(result)

            if result["success"]:
                results["successful"] += 1
            else:
                results["failed"] += 1

        self.logger.info(
            f"Batch enhancement completed: {results['successful']} successful, {results['failed']} failed"
        )
        return results
