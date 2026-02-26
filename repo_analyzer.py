#!/usr/bin/env python3
"""
Repository Analyzer Module
Advanced analysis and insights for GitHub repositories.
"""

from typing import Dict, List, Any, Optional
from collections import Counter
from datetime import datetime, timedelta
from github_service import GitHubService


class RepositoryAnalyzer:
    """Advanced repository analysis and insights."""

    def __init__(self, github_service: GitHubService):
        self.github_service = github_service

    def analyze_language_distribution(self) -> Dict[str, int]:
        """Analyze programming language distribution across all repositories."""
        repositories = self.github_service.get_user_repositories()
        languages = [repo["language"] for repo in repositories if repo["language"]]
        return dict(Counter(languages))

    def get_repository_statistics(self) -> Dict[str, Any]:
        """Get comprehensive statistics for all repositories."""
        repositories = self.github_service.get_user_repositories()

        if not repositories:
            return {}

        total_stars = sum(repo["stars"] for repo in repositories)
        total_forks = sum(repo["forks"] for repo in repositories)
        private_repos = sum(1 for repo in repositories if repo["is_private"])
        public_repos = len(repositories) - private_repos

        # Find most recent update
        most_recent = max(repositories, key=lambda x: x["updated_at"])

        # Calculate repository sizes
        sizes = [repo.get("size", 0) for repo in repositories]

        return {
            "total_repositories": len(repositories),
            "total_stars": total_stars,
            "total_forks": total_forks,
            "private_repositories": private_repos,
            "public_repositories": public_repos,
            "most_recently_updated": most_recent["name"],
            "last_updated": most_recent["updated_at"],
            "average_size_kb": sum(sizes) / len(sizes) if sizes else 0,
            "largest_repository": (
                max(repositories, key=lambda x: x.get("size", 0))["name"]
                if repositories
                else None
            ),
        }

    def find_starred_repositories(self) -> List[Dict[str, Any]]:
        """Find repositories with stars."""
        repositories = self.github_service.get_user_repositories()
        return [repo for repo in repositories if repo["stars"] > 0]

    def find_forked_repositories(self) -> List[Dict[str, Any]]:
        """Find repositories with forks."""
        repositories = self.github_service.get_user_repositories()
        return [repo for repo in repositories if repo["forks"] > 0]

    def get_activity_summary(self) -> Dict[str, Any]:
        """Get repository activity summary based on update times."""
        repositories = self.github_service.get_user_repositories()

        if not repositories:
            return {}

        now = datetime.now()
        recent_week = 0
        recent_month = 0
        recent_year = 0

        for repo in repositories:
            try:
                updated_at = datetime.fromisoformat(
                    repo["updated_at"].replace("Z", "+00:00")
                )
                days_diff = (now - updated_at.replace(tzinfo=None)).days

                if days_diff <= 7:
                    recent_week += 1
                if days_diff <= 30:
                    recent_month += 1
                if days_diff <= 365:
                    recent_year += 1
            except (ValueError, AttributeError):
                continue

        return {
            "updated_last_week": recent_week,
            "updated_last_month": recent_month,
            "updated_last_year": recent_year,
            "inactive_over_year": len(repositories) - recent_year,
        }

    def print_analysis_report(self) -> None:
        """Print comprehensive analysis report."""
        print("\n" + "=" * 60)
        print("REPOSITORY ANALYSIS REPORT")
        print("=" * 60)

        # Basic statistics
        stats = self.get_repository_statistics()
        if stats:
            print(f"\n📊 OVERVIEW")
            print(f"Total Repositories: {stats['total_repositories']}")
            print(
                f"Public: {stats['public_repositories']} | Private: {stats['private_repositories']}"
            )
            print(
                f"Total Stars: {stats['total_stars']} | Total Forks: {stats['total_forks']}"
            )
            print(
                f"Most Recent: {stats['most_recently_updated']} (Updated: {stats['last_updated']})"
            )

        # Language distribution
        languages = self.analyze_language_distribution()
        if languages:
            print(f"\n💻 LANGUAGE DISTRIBUTION")
            for lang, count in sorted(
                languages.items(), key=lambda x: x[1], reverse=True
            ):
                print(f"{lang}: {count} repositories")

        # Activity summary
        activity = self.get_activity_summary()
        if activity:
            print(f"\n📅 ACTIVITY SUMMARY")
            print(f"Updated in last week: {activity['updated_last_week']}")
            print(f"Updated in last month: {activity['updated_last_month']}")
            print(f"Updated in last year: {activity['updated_last_year']}")
            print(f"Inactive over 1 year: {activity['inactive_over_year']}")

        # Notable repositories
        starred = self.find_starred_repositories()
        forked = self.find_forked_repositories()

        if starred:
            print(f"\n⭐ STARRED REPOSITORIES ({len(starred)})")
            for repo in starred[:5]:  # Show top 5
                print(f"  {repo['name']}: {repo['stars']} stars")

        if forked:
            print(f"\n🔀 FORKED REPOSITORIES ({len(forked)})")
            for repo in forked[:5]:  # Show top 5
                print(f"  {repo['name']}: {repo['forks']} forks")

        print("\n" + "=" * 60)

    def export_analysis(self, filename: str = "repository_analysis.txt") -> None:
        """Export analysis report to a file."""
        import io
        import sys

        # Capture print output
        old_stdout = sys.stdout
        sys.stdout = buffer = io.StringIO()

        try:
            self.print_analysis_report()
            report = buffer.getvalue()
        finally:
            sys.stdout = old_stdout

        # Write to file
        with open(filename, "w", encoding="utf-8") as f:
            f.write(report)

        print(f"Analysis report exported to {filename}")


if __name__ == "__main__":
    # Example usage
    from config import Config
    from github_service import GitHubService

    try:
        config = Config()
        github_service = GitHubService(config)

        if github_service.authenticate():
            analyzer = RepositoryAnalyzer(github_service)
            analyzer.print_analysis_report()

    except Exception as e:
        print(f"Error: {e}")
