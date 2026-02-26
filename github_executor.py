#!/usr/bin/env python3
"""
GitHub Executor Module
Handles GitHub operations like creating and pushing README files to repositories.
"""

from github import Github, GithubException
from typing import Optional, Dict, Any
import logging


class GitHubExecutor:
    """Handles GitHub repository operations."""

    def __init__(self, github_client: Github):
        """
        Initialize GitHub executor with authenticated client.

        Args:
            github_client: Authenticated PyGithub client instance
        """
        self.github = github_client
        self.user = None
        self._setup_logging()

    def _setup_logging(self) -> None:
        """Set up logging for the executor."""
        logging.basicConfig(
            level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
        )
        self.logger = logging.getLogger(__name__)

    def authenticate_user(self) -> bool:
        """
        Authenticate and get the current user.

        Returns:
            True if authentication successful, False otherwise
        """
        try:
            self.user = self.github.get_user()
            self.logger.info(f"Authenticated as: {self.user.login}")
            return True
        except GithubException as e:
            self.logger.error(f"Authentication failed: {e}")
            return False

    def check_readme_exists(self, repo_name: str) -> bool:
        """
        Check if README.md exists in the repository.

        Args:
            repo_name: Name of the repository to check

        Returns:
            True if README.md exists, False otherwise

        Raises:
            GithubException: If repository access fails
        """
        try:
            repo = self.user.get_repo(repo_name)

            # Try to get README.md file
            try:
                readme_file = repo.get_contents("README.md")
                self.logger.info(f"README.md already exists in {repo_name}")
                return True
            except GithubException as e:
                if e.status == 404:  # File not found
                    self.logger.info(f"README.md not found in {repo_name}")
                    return False
                else:
                    raise e

        except GithubException as e:
            self.logger.error(f"Failed to access repository {repo_name}: {e}")
            raise

    def push_readme_to_repo(
        self, repo_name: str, readme_content: str
    ) -> Dict[str, Any]:
        """
        Push README.md to a repository if it doesn't exist.

        Args:
            repo_name: Name of the repository
            readme_content: Content for the README.md file

        Returns:
            Dictionary with operation result and details
        """
        result = {
            "success": False,
            "repo_name": repo_name,
            "message": "",
            "error": None,
        }

        try:
            # Ensure user is authenticated
            if not self.user:
                if not self.authenticate_user():
                    result["error"] = "Authentication failed"
                    return result

            # Check if README already exists
            if self.check_readme_exists(repo_name):
                result["message"] = "README.md already exists - skipping"
                result["success"] = True  # Not an error, just skipping
                return result

            # Get repository
            repo = self.user.get_repo(repo_name)

            # Create README.md file
            commit_message = "Add professional README"

            try:
                # Create the file in the repository
                created_file = repo.create_file(
                    path="README.md",
                    message=commit_message,
                    content=readme_content,
                    branch=repo.default_branch,
                )

                self.logger.info(f"Successfully created README.md in {repo_name}")
                result["success"] = True
                result["message"] = f"README.md created successfully in {repo_name}"
                result["commit_sha"] = created_file["commit"].sha

            except GithubException as e:
                error_msg = f"Failed to create README.md in {repo_name}: {e}"
                self.logger.error(error_msg)
                result["error"] = error_msg
                return result

        except GithubException as e:
            error_msg = f"GitHub API error for repository {repo_name}: {e}"
            self.logger.error(error_msg)
            result["error"] = error_msg

        except Exception as e:
            error_msg = f"Unexpected error for repository {repo_name}: {e}"
            self.logger.error(error_msg)
            result["error"] = error_msg

        return result

    def batch_push_readmes(self, readme_data: list) -> Dict[str, Any]:
        """
        Push README files to multiple repositories.

        Args:
            readme_data: List of dictionaries with 'repo_name' and 'readme_content'

        Returns:
            Dictionary with batch operation results
        """
        results = {
            "total": len(readme_data),
            "successful": 0,
            "skipped": 0,
            "failed": 0,
            "details": [],
        }

        self.logger.info(
            f"Starting batch README push for {len(readme_data)} repositories"
        )

        for data in readme_data:
            repo_name = data.get("repo_name")
            readme_content = data.get("readme_content")

            if not repo_name or not readme_content:
                self.logger.warning(f"Skipping invalid data: {data}")
                results["failed"] += 1
                continue

            result = self.push_readme_to_repo(repo_name, readme_content)
            results["details"].append(result)

            if result["success"]:
                if "already exists" in result["message"]:
                    results["skipped"] += 1
                else:
                    results["successful"] += 1
            else:
                results["failed"] += 1

        # Log summary
        self.logger.info(
            f"Batch operation completed: {results['successful']} created, "
            f"{results['skipped']} skipped, {results['failed']} failed"
        )

        return results

    def get_repository_info(self, repo_name: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a repository.

        Args:
            repo_name: Name of the repository

        Returns:
            Repository information dictionary or None if error
        """
        try:
            if not self.user:
                if not self.authenticate_user():
                    return None

            repo = self.user.get_repo(repo_name)

            return {
                "name": repo.name,
                "full_name": repo.full_name,
                "description": repo.description,
                "language": repo.language,
                "stars": repo.stargazers_count,
                "forks": repo.forks_count,
                "is_private": repo.private,
                "default_branch": repo.default_branch,
                "clone_url": repo.clone_url,
                "html_url": repo.html_url,
                "size": repo.size,
                "created_at": repo.created_at,
                "updated_at": repo.updated_at,
            }

        except GithubException as e:
            self.logger.error(f"Failed to get repository info for {repo_name}: {e}")
            return None

    def print_batch_results(self, results: Dict[str, Any]) -> None:
        """Print a summary of batch operation results."""
        print(f"\n📊 Batch README Push Results")
        print("=" * 50)
        print(f"Total repositories: {results['total']}")
        print(f"✅ Successfully created: {results['successful']}")
        print(f"⏭️  Skipped (already exists): {results['skipped']}")
        print(f"❌ Failed: {results['failed']}")

        if results["failed"] > 0:
            print(f"\n❌ Failed Operations:")
            for detail in results["details"]:
                if not detail["success"] and detail.get("error"):
                    print(f"   • {detail['repo_name']}: {detail['error']}")

        print(f"\n🎉 Operation completed!")


# Convenience function for direct usage
def push_readme_to_repo(
    github_client: Github, repo_name: str, readme_content: str
) -> Dict[str, Any]:
    """
    Convenience function to push README to a repository.

    Args:
        github_client: Authenticated PyGithub client
        repo_name: Name of the repository
        readme_content: README content to push

    Returns:
        Operation result dictionary
    """
    executor = GitHubExecutor(github_client)
    return executor.push_readme_to_repo(repo_name, readme_content)


if __name__ == "__main__":
    # Example usage
    from config import Config

    try:
        config = Config()
        github = Github(config.github_token)

        executor = GitHubExecutor(github)

        # Example README content
        sample_readme = """# Test Repository

This is a sample README generated by the GitHub automation agent.

## Features

- Feature 1
- Feature 2
- Feature 3

## Installation

```bash
git clone https://github.com/username/repo.git
cd repo
```

## Usage

[Usage instructions here]

## License

MIT License
"""

        # Test the function
        result = executor.push_readme_to_repo("test-repo", sample_readme)
        print(f"Result: {result}")

    except Exception as e:
        print(f"Error: {e}")
