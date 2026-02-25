#!/usr/bin/env python3
"""
GitHub Automation Agent
A production-grade Python application for GitHub repository management.
"""

import sys
import argparse
from typing import Optional
from config import Config
from github_service import GitHubService
from repo_analyzer import RepositoryAnalyzer
from repo_improver import RepositoryImprover
from github_executor import GitHubExecutor
from repo_enhancer import RepositoryEnhancer
from project_generator import ProjectGenerator
from profile_optimizer import ProfileOptimizer
from activity_manager import ActivityManager
from scheduler import GitHubAgentScheduler


def main():
    """Main entry point for the GitHub automation agent."""
    parser = argparse.ArgumentParser(
        description="GitHub Automation Agent - Manage your GitHub repositories",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                    # List all repositories
  python main.py --repo my-repo     # Get details for specific repository
  python main.py --count            # Show only repository count
        """
    )
    
    parser.add_argument(
        '--repo', 
        type=str,
        help='Get details for a specific repository'
    )
    
    parser.add_argument(
        '--count',
        action='store_true',
        help='Show only the total count of repositories'
    )
    
    parser.add_argument(
        '--full-agent',
        action='store_true',
        help='Run the full GitHub agent pipeline'
    )
    
    parser.add_argument(
        '--schedule',
        action='store_true',
        help='Run the agent scheduler continuously'
    )
    
    parser.add_argument(
        '--interval',
        type=int,
        default=24,
        help='Scheduler interval in hours (default: 24)'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose output'
    )
    
    args = parser.parse_args()
    
    try:
        # Initialize configuration
        config = Config()
        
        # Initialize GitHub service
        github_service = GitHubService(config)
        
        # Authenticate with GitHub
        if not github_service.authenticate():
            sys.exit(1)
        
        # Initialize repository analyzer
        analyzer = RepositoryAnalyzer(github_service)
        
        # Always run full GitHub agent pipeline (CI/CD execution mode)
        scheduler = GitHubAgentScheduler()
        results = scheduler.run_full_pipeline()
        scheduler.print_pipeline_summary(results)
    
    except ValueError as e:
        print(f"Configuration error: {e}")
        sys.exit(1)
    
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)


def print_analysis_results(analyzer: RepositoryAnalyzer) -> None:
    """Print clean analysis results from repository analyzer."""
    try:
        # Get repository analysis data
        repositories = analyzer.github_service.get_user_repositories()
        
        if not repositories:
            print("No repositories found.")
            return
        
        print(f"\nRepository Analysis Results")
        print("=" * 50)
        print(f"Found {len(repositories)} repositories:\n")
        
        for i, repo in enumerate(repositories, 1):
            # Check if README exists
            readme_status = "📄" if repo.get('has_readme', False) else "❌"
            privacy = "🔒" if repo['is_private'] else "🌍"
            
            print(f"{i:2d}. {privacy} {repo['name']} {readme_status}")
            print(f"     Size: {repo.get('size', 0)} KB | Stars: {repo['stars']} | Forks: {repo['forks']}")
            print(f"     Updated: {repo['updated_at']}")
            print()
    
    except Exception as e:
        print(f"Error during analysis: {e}")


def print_readme_improvements(improvements: list) -> None:
    """Print repositories that need README files."""
    if not improvements:
        print("\n✅ All repositories have README files!")
        return
    
    print(f"\nRepositories needing README:")
    print("-" * 30)
    
    for improvement in improvements:
        print(f"📝 {improvement['repo_name']}")
    
    print(f"\n💡 Generated {len(improvements)} README templates ready for use!")


def push_readme_files(executor: GitHubExecutor, improvements: list) -> None:
    """Push README files to repositories that need them."""
    print(f"\n🚀 Pushing README files to repositories...")
    print("-" * 40)
    
    for improvement in improvements:
        repo_name = improvement['repo_name']
        readme_content = improvement['readme_content']
        
        result = executor.push_readme_to_repo(repo_name, readme_content)
        
        if result['success']:
            if "already exists" in result['message']:
                print(f"⏭️  Skipped {repo_name}: README already exists")
            else:
                print(f"✅ README pushed to: {repo_name}")
        else:
            print(f"❌ Failed {repo_name}: {result.get('error', 'Unknown error')}")


def print_repository_details(repo: dict, verbose: bool = False) -> None:
    """Print detailed information about a repository."""
    print(f"\nRepository Details: {repo['full_name']}")
    print("=" * 60)
    print(f"Name: {repo['name']}")
    print(f"Description: {repo['description'] or 'No description'}")
    print(f"Language: {repo['language'] or 'N/A'}")
    print(f"Stars: {repo['stars']}")
    print(f"Forks: {repo['forks']}")
    print(f"Private: {'Yes' if repo['is_private'] else 'No'}")
    print(f"Last Updated: {repo['updated_at']}")
    print(f"URL: {repo['url']}")
    
    if verbose:
        print(f"Clone URL: {repo['clone_url']}")
        print(f"Size: {repo['size']} KB")


if __name__ == "__main__":
    main()