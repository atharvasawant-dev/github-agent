from github import Github, GithubException
from typing import List, Dict, Any
from config import Config


class GitHubService:
    """Service class for GitHub API operations."""

    def __init__(self, config: Config):
        self.config = config
        self.github = Github(config.github_token)
        self.user = None

    def authenticate(self) -> bool:
        """Authenticate with GitHub and verify connection."""
        try:
            self.user = self.github.get_user()
            print(f"Successfully authenticated as: {self.user.login}")
            return True
        except GithubException as e:
            print(f"Authentication failed: {e}")
            return False

    def get_user_repositories(self) -> List[Dict[str, Any]]:
        """Get all repositories for the authenticated user."""
        if not self.user:
            raise RuntimeError("Not authenticated. Call authenticate() first.")

        repositories = []
        try:
            repos = self.user.get_repos(type="owner")
            for repo in repos:
                repo_info = {
                    "name": repo.name,
                    "full_name": repo.full_name,
                    "description": repo.description,
                    "language": repo.language,
                    "stars": repo.stargazers_count,
                    "forks": repo.forks_count,
                    "is_private": repo.private,
                    "updated_at": repo.updated_at,
                    "url": repo.html_url,
                }
                repositories.append(repo_info)
        except GithubException as e:
            print(f"Error fetching repositories: {e}")
            return []

        return repositories

    def print_repository_names(self) -> None:
        """Print names of all user repositories."""
        repositories = self.get_user_repositories()

        if not repositories:
            print("No repositories found.")
            return

        print(f"\nFound {len(repositories)} repositories:")
        print("-" * 50)

        for i, repo in enumerate(repositories, 1):
            privacy = "🔒" if repo["is_private"] else "🌍"
            stars = "⭐" if repo["stars"] > 0 else ""
            print(f"{i:2d}. {privacy} {repo['name']} {stars}")
            if repo["description"]:
                print(f"     {repo['description']}")
            print(
                f"     Language: {repo['language'] or 'N/A'} | Stars: {repo['stars']} | Forks: {repo['forks']}"
            )
            print()

    def get_repository_by_name(self, repo_name: str) -> Dict[str, Any]:
        """Get specific repository by name."""
        if not self.user:
            raise RuntimeError("Not authenticated. Call authenticate() first.")

        try:
            repo = self.user.get_repo(repo_name)
            return {
                "name": repo.name,
                "full_name": repo.full_name,
                "description": repo.description,
                "language": repo.language,
                "stars": repo.stargazers_count,
                "forks": repo.forks_count,
                "is_private": repo.private,
                "updated_at": repo.updated_at,
                "url": repo.html_url,
                "clone_url": repo.clone_url,
                "size": repo.size,
            }
        except GithubException as e:
            print(f"Error fetching repository '{repo_name}': {e}")
            return {}
