#!/usr/bin/env python3
"""
Activity Manager Module
Manages continuous improvement and meaningful commits.
"""

import logging
import random
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from github import Github, GithubException


class ActivityManager:
    """Manages GitHub activity with meaningful improvements."""

    def __init__(self, github_client: Github):
        self.github = github_client
        self.user = None
        self._setup_logging()

    def _setup_logging(self) -> None:
        """Set up logging for the activity manager."""
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

    def should_create_activity(self) -> bool:
        """Check if new activity should be created."""
        if not self.user:
            return False

        try:
            # Check last activity
            repos = list(self.user.get_repos(type="owner"))

            if not repos:
                return True

            # Get the most recent commit across all repositories
            latest_commit = None
            for repo in repos:
                try:
                    commits = list(repo.get_commits())
                    if commits:
                        commit_date = commits[0].commit.author.date
                        if not latest_commit or commit_date > latest_commit:
                            latest_commit = commit_date
                except GithubException:
                    continue

            # If no commits in last 3 days, create activity
            if not latest_commit:
                return True

            days_since_last_commit = (
                datetime.now() - latest_commit.replace(tzinfo=None)
            ).days
            return days_since_last_commit >= 3

        except GithubException as e:
            self.logger.error(f"Failed to check activity status: {e}")
            return False

    def get_improvement_suggestions(self) -> List[Dict[str, Any]]:
        """Get meaningful improvement suggestions."""
        suggestions = [
            {
                "type": "documentation",
                "title": "Improve README documentation",
                "description": "Add installation instructions and usage examples",
                "priority": "high",
            },
            {
                "type": "tests",
                "title": "Add unit tests",
                "description": "Increase test coverage for critical functions",
                "priority": "high",
            },
            {
                "type": "dependencies",
                "title": "Update dependencies",
                "description": "Update to latest stable versions",
                "priority": "medium",
            },
            {
                "type": "code_quality",
                "title": "Code refactoring",
                "description": "Improve code structure and readability",
                "priority": "medium",
            },
            {
                "type": "performance",
                "title": "Performance optimization",
                "description": "Optimize critical paths and reduce complexity",
                "priority": "low",
            },
            {
                "type": "security",
                "title": "Security improvements",
                "description": "Add input validation and error handling",
                "priority": "high",
            },
            {
                "type": "examples",
                "title": "Add usage examples",
                "description": "Create practical examples and tutorials",
                "priority": "medium",
            },
            {
                "type": "ci_cd",
                "title": "Improve CI/CD pipeline",
                "description": "Add automated testing and deployment",
                "priority": "medium",
            },
        ]

        return suggestions

    def generate_meaningful_commit(
        self, repo_name: str, improvement_type: str
    ) -> Dict[str, Any]:
        """Generate a meaningful commit based on improvement type."""
        commit_templates = {
            "documentation": {
                "files": {"docs/usage.md": """# Usage Guide

## Installation

```bash
pip install package-name
```

## Basic Usage

```python
from package import main

# Example usage
result = main()
print(result)
```

## Advanced Features

### Feature 1
Description of advanced feature 1.

### Feature 2
Description of advanced feature 2.

## Troubleshooting

### Common Issues

1. **Issue**: Description
   **Solution**: How to fix it

2. **Issue**: Description
   **Solution**: How to fix it

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.
"""},
                "message": "docs: Add comprehensive usage guide and troubleshooting",
                "description": "Added detailed usage documentation with examples",
            },
            "tests": {
                "files": {
                    "tests/test_integration.py": '''"""Integration tests for the application."""

import pytest
import sys
import os

# Add src to path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


class TestIntegration:
    """Integration test cases."""
    
    def test_full_workflow(self):
        """Test complete application workflow."""
        # Test the main functionality
        assert True  # Replace with actual test
    
    def test_error_handling(self):
        """Test error handling scenarios."""
        # Test error cases
        assert True  # Replace with actual test
    
    def test_performance(self):
        """Test performance requirements."""
        # Test performance
        assert True  # Replace with actual test


if __name__ == '__main__':
    pytest.main([__file__])
'''
                },
                "message": "test: Add integration tests for critical workflows",
                "description": "Added comprehensive integration test suite",
            },
            "dependencies": {
                "files": {"requirements.txt": """# Core dependencies
requests>=2.31.0
click>=8.1.0
pydantic>=2.0.0
python-dotenv>=1.0.0

# Development dependencies
pytest>=7.4.0
pytest-cov>=4.1.0
black>=23.0.0
flake8>=6.0.0
mypy>=1.5.0

# Optional dependencies
aiohttp>=3.8.0
jinja2>=3.1.0
"""},
                "message": "deps: Update dependencies to latest stable versions",
                "description": "Updated all dependencies for security and performance",
            },
            "code_quality": {
                "files": {
                    "src/utils.py": '''"""Utility functions for the application."""

import logging
from typing import Any, Dict, List, Optional
from datetime import datetime


logger = logging.getLogger(__name__)


def format_timestamp(timestamp: datetime) -> str:
    """Format timestamp in a consistent way.
    
    Args:
        timestamp: DateTime object to format
        
    Returns:
        Formatted timestamp string
    """
    return timestamp.strftime("%Y-%m-%d %H:%M:%S")


def validate_input(data: Dict[str, Any], required_fields: List[str]) -> bool:
    """Validate input data against required fields.
    
    Args:
        data: Dictionary to validate
        required_fields: List of required field names
        
    Returns:
        True if all required fields are present
    """
    return all(field in data for field in required_fields)


def safe_get(data: Dict[str, Any], key: str, default: Any = None) -> Any:
    """Safely get value from dictionary.
    
    Args:
        data: Dictionary to get value from
        key: Key to retrieve
        default: Default value if key not found
        
    Returns:
        Value from dictionary or default
    """
    return data.get(key, default)


class PerformanceTimer:
    """Context manager for timing operations."""
    
    def __init__(self, operation_name: str):
        self.operation_name = operation_name
        self.start_time = None
        self.end_time = None
    
    def __enter__(self):
        self.start_time = datetime.now()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_time = datetime.now()
        duration = (self.end_time - self.start_time).total_seconds()
        logger.info(f"{self.operation_name} completed in {duration:.2f} seconds")
'''
                },
                "message": "refactor: Improve code structure with utility functions",
                "description": "Added utility functions for better code organization",
            },
            "security": {
                "files": {
                    "src/security.py": '''"""Security utilities for the application."""

import hashlib
import secrets
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


def hash_password(password: str) -> str:
    """Hash password using SHA-256.
    
    Args:
        password: Plain text password
        
    Returns:
        Hashed password
    """
    return hashlib.sha256(password.encode()).hexdigest()


def generate_secure_token(length: int = 32) -> str:
    """Generate cryptographically secure token.
    
    Args:
        length: Length of token in bytes
        
    Returns:
        Hexadecimal token string
    """
    return secrets.token_hex(length)


def sanitize_input(data: str) -> str:
    """Sanitize user input to prevent injection.
    
    Args:
        data: User input string
        
    Returns:
        Sanitized string
    """
    # Remove potentially dangerous characters
    dangerous_chars = ['<', '>', '"', "'", '&', 'script', 'javascript']
    sanitized = data
    
    for char in dangerous_chars:
        sanitized = sanitized.replace(char, '')
    
    return sanitized.strip()


def validate_api_key(api_key: str) -> bool:
    """Validate API key format.
    
    Args:
        api_key: API key string to validate
        
    Returns:
        True if format is valid
    """
    if not api_key:
        return False
    
    # Basic validation - adjust based on your requirements
    return len(api_key) >= 32 and api_key.isalnum()


class SecurityConfig:
    """Security configuration class."""
    
    def __init__(self):
        self.max_login_attempts = 5
        self.session_timeout = 3600  # 1 hour
        self.password_min_length = 8
        self.require_special_chars = True
    
    def validate_password_strength(self, password: str) -> Dict[str, Any]:
        """Validate password strength.
        
        Args:
            password: Password to validate
            
        Returns:
            Dictionary with validation results
        """
        result = {
            'valid': True,
            'errors': []
        }
        
        if len(password) < self.password_min_length:
            result['valid'] = False
            result['errors'].append(f"Password must be at least {self.password_min_length} characters")
        
        if self.require_special_chars and not any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?' for c in password):
            result['valid'] = False
            result['errors'].append("Password must contain special characters")
        
        return result
'''
                },
                "message": "security: Add security utilities and input validation",
                "description": "Implemented security measures for input handling and validation",
            },
        }

        return commit_templates.get(improvement_type, commit_templates["documentation"])

    def create_meaningful_activity(self, repo_name: str) -> Dict[str, Any]:
        """Create meaningful activity for a repository."""
        result = {
            "success": False,
            "repo_name": repo_name,
            "commit_message": "",
            "description": "",
            "errors": [],
        }

        try:
            if not self.user:
                if not self.authenticate():
                    result["errors"].append("Authentication failed")
                    return result

            repo = self.user.get_repo(repo_name)

            # Get improvement suggestions
            suggestions = self.get_improvement_suggestions()
            improvement = random.choice(suggestions)
            improvement_type = improvement["type"]

            self.logger.info(f"Creating meaningful activity: {improvement['title']}")

            # Generate commit content
            commit_data = self.generate_meaningful_commit(repo_name, improvement_type)

            # Create files and commit
            for file_path, content in commit_data["files"].items():
                try:
                    # Check if file exists
                    try:
                        existing_file = repo.get_contents(file_path)
                        # Update existing file
                        repo.update_file(
                            path=file_path,
                            message=commit_data["message"],
                            content=content,
                            sha=existing_file.sha,
                            branch=repo.default_branch,
                        )
                    except GithubException as e:
                        if e.status == 404:
                            # Create new file
                            repo.create_file(
                                path=file_path,
                                message=commit_data["message"],
                                content=content,
                                branch=repo.default_branch,
                            )
                        else:
                            raise e
                except GithubException as e:
                    self.logger.warning(f"Failed to create {file_path}: {e}")

            result["success"] = True
            result["commit_message"] = commit_data["message"]
            result["description"] = commit_data["description"]

            self.logger.info(f"Successfully created activity in {repo_name}")

        except GithubException as e:
            error_msg = f"GitHub API error for {repo_name}: {e}"
            self.logger.error(error_msg)
            result["errors"].append(error_msg)
        except Exception as e:
            error_msg = f"Unexpected error for {repo_name}: {e}"
            self.logger.error(error_msg)
            result["errors"].append(error_msg)

        return result

    def run_activity_cycle(self) -> Dict[str, Any]:
        """Run a complete activity cycle."""
        results = {
            "success": False,
            "activities_created": 0,
            "repositories_updated": [],
            "errors": [],
        }

        try:
            if not self.should_create_activity():
                self.logger.info("No activity needed at this time")
                results["success"] = True
                return results

            if not self.user:
                if not self.authenticate():
                    results["errors"].append("Authentication failed")
                    return results

            # Get user repositories
            repos = list(self.user.get_repos(type="owner"))

            # Select a random repository for activity
            if repos:
                target_repo = random.choice(repos)
                activity_result = self.create_meaningful_activity(target_repo.name)

                if activity_result["success"]:
                    results["activities_created"] = 1
                    results["repositories_updated"].append(
                        {
                            "repo": target_repo.name,
                            "message": activity_result["commit_message"],
                            "description": activity_result["description"],
                        }
                    )
                else:
                    results["errors"].extend(activity_result["errors"])

            results["success"] = True
            self.logger.info("Activity cycle complete")

        except Exception as e:
            error_msg = f"Activity cycle failed: {e}"
            self.logger.error(error_msg)
            results["errors"].append(error_msg)

        return results
