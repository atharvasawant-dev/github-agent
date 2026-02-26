#!/usr/bin/env python3
"""
Scheduler Module
Runs the full GitHub agent pipeline every 24 hours.
"""

import logging
import time
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from github import Github

from config import Config
from github_service import GitHubService
from repo_analyzer import RepositoryAnalyzer
from repo_improver import RepositoryImprover
from github_executor import GitHubExecutor
from repo_enhancer import RepositoryEnhancer
from project_generator import ProjectGenerator
from profile_optimizer import ProfileOptimizer
from activity_manager import ActivityManager


class GitHubAgentScheduler:
    """Scheduler for running the complete GitHub agent pipeline."""

    def __init__(self):
        self.config = Config()
        self.github = Github(self.config.github_token)
        self._setup_logging()

        # Initialize all components
        self.github_service = GitHubService(self.config)
        self.analyzer = RepositoryAnalyzer(self.github_service)
        self.improver = RepositoryImprover()
        self.executor = GitHubExecutor(self.github)
        self.enhancer = RepositoryEnhancer(self.github)
        self.generator = ProjectGenerator(self.github)
        self.optimizer = ProfileOptimizer(self.github)
        self.activity_manager = ActivityManager(self.github)

    def _setup_logging(self) -> None:
        """Set up logging for the scheduler."""
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            handlers=[logging.FileHandler("github_agent.log"), logging.StreamHandler()],
        )
        self.logger = logging.getLogger(__name__)

    def run_full_pipeline(self) -> Dict[str, Any]:
        """Run the complete GitHub agent pipeline."""
        pipeline_results = {
            "start_time": datetime.now(),
            "steps": {},
            "success": False,
            "errors": [],
        }

        self.logger.info("Starting full GitHub agent pipeline")

        try:
            # Step 1: Authenticate
            self.logger.info("Step 1: Authenticating with GitHub")
            if not self.github_service.authenticate():
                pipeline_results["errors"].append("Authentication failed")
                return pipeline_results

            pipeline_results["steps"]["authentication"] = {
                "success": True,
                "message": "Successfully authenticated with GitHub",
            }

            # Step 2: Analyze repositories
            self.logger.info("Step 2: Analyzing repositories")
            repositories = self.analyzer.github_service.get_user_repositories()
            pipeline_results["steps"]["analysis"] = {
                "success": True,
                "repositories_found": len(repositories),
                "message": f"Found {len(repositories)} repositories",
            }

            # Step 3: Generate README improvements
            self.logger.info("Step 3: Generating README improvements")
            improvements = self.improver.analyze_repositories_needing_readme(
                repositories
            )
            pipeline_results["steps"]["readme_generation"] = {
                "success": True,
                "improvements_generated": len(improvements),
                "message": f"Generated {len(improvements)} README improvements",
            }

            # Step 4: Push README files
            self.logger.info("Step 4: Pushing README files")
            readme_results = []
            for improvement in improvements:
                result = self.executor.push_readme_to_repo(
                    improvement["repo_name"], improvement["readme_content"]
                )
                readme_results.append(result)

            successful_readmes = len([r for r in readme_results if r["success"]])
            pipeline_results["steps"]["readme_push"] = {
                "success": True,
                "successful_pushes": successful_readmes,
                "total_attempts": len(readme_results),
                "message": f"Pushed {successful_readmes}/{len(readme_results)} README files",
            }

            # Step 5: Enhance repositories
            self.logger.info("Step 5: Enhancing repository structure")
            repo_names = [repo["name"] for repo in repositories]
            enhancement_results = self.enhancer.batch_enhance_repositories(repo_names)
            pipeline_results["steps"]["enhancement"] = {
                "success": True,
                "enhanced_repos": enhancement_results["successful"],
                "total_repos": enhancement_results["total"],
                "message": f'Enhanced {enhancement_results["successful"]}/{enhancement_results["total"]} repositories',
            }

            # Step 6: Generate new projects if needed
            self.logger.info("Step 6: Checking if new projects are needed")
            if self.generator.should_create_new_repo():
                new_projects = min(
                    3, 20 - len(repositories)
                )  # Create up to 3 new projects
                generation_results = self.generator.generate_new_projects(new_projects)
                pipeline_results["steps"]["project_generation"] = {
                    "success": True,
                    "new_projects_created": generation_results["successful"],
                    "attempts": generation_results["total"],
                    "message": f'Created {generation_results["successful"]} new projects',
                }
            else:
                pipeline_results["steps"]["project_generation"] = {
                    "success": True,
                    "message": "Sufficient repositories exist, no new projects needed",
                }

            # Step 7: Optimize profile
            self.logger.info("Step 7: Optimizing GitHub profile")
            profile_results = self.optimizer.update_profile_readme()
            pipeline_results["steps"]["profile_optimization"] = {
                "success": profile_results["success"],
                "message": profile_results.get(
                    "message", "Profile optimization completed"
                ),
            }

            # Step 8: Activity management
            self.logger.info("Step 8: Managing activity")
            activity_results = self.activity_manager.run_activity_cycle()
            pipeline_results["steps"]["activity_management"] = {
                "success": activity_results["success"],
                "activities_created": activity_results["activities_created"],
                "message": f'Created {activity_results["activities_created"]} meaningful activities',
            }

            pipeline_results["success"] = True
            pipeline_results["end_time"] = datetime.now()
            pipeline_results["duration"] = (
                pipeline_results["end_time"] - pipeline_results["start_time"]
            ).total_seconds()

            self.logger.info(
                f"Pipeline completed successfully in {pipeline_results['duration']:.2f} seconds"
            )

        except Exception as e:
            error_msg = f"Pipeline failed: {e}"
            self.logger.error(error_msg)
            pipeline_results["errors"].append(error_msg)
            pipeline_results["end_time"] = datetime.now()

        return pipeline_results

    def print_pipeline_summary(self, results: Dict[str, Any]) -> None:
        """Print a summary of the pipeline results."""
        print("\n" + "=" * 60)
        print("GITHUB AGENT PIPELINE SUMMARY")
        print("=" * 60)

        if results["success"]:
            print("✅ Pipeline completed successfully!")
        else:
            print("❌ Pipeline completed with errors!")

        print(f"⏱️  Duration: {results.get('duration', 0):.2f} seconds")
        print(f"🕐 Started: {results['start_time'].strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🕐 Ended: {results.get('end_time', 'N/A')}")

        print("\n📋 Step Results:")
        print("-" * 40)

        for step_name, step_result in results["steps"].items():
            status = "✅" if step_result["success"] else "❌"
            print(f"{status} {step_name.title()}: {step_result['message']}")

        if results["errors"]:
            print("\n❌ Errors:")
            print("-" * 40)
            for error in results["errors"]:
                print(f"• {error}")

        print("\n" + "=" * 60)

    def run_scheduler(self, interval_hours: int = 24) -> None:
        """Run the scheduler continuously."""
        self.logger.info(
            f"Starting GitHub agent scheduler (interval: {interval_hours} hours)"
        )

        while True:
            try:
                # Run the full pipeline
                results = self.run_full_pipeline()
                self.print_pipeline_summary(results)

                # Calculate next run time
                next_run = datetime.now() + timedelta(hours=interval_hours)
                self.logger.info(
                    f"Next run scheduled for: {next_run.strftime('%Y-%m-%d %H:%M:%S')}"
                )

                # Sleep until next run
                sleep_seconds = interval_hours * 3600
                self.logger.info(f"Sleeping for {interval_hours} hours...")
                time.sleep(sleep_seconds)

            except KeyboardInterrupt:
                self.logger.info("Scheduler stopped by user")
                break
            except Exception as e:
                self.logger.error(f"Scheduler error: {e}")
                # Wait 1 hour before retrying
                time.sleep(3600)


def run_full_github_agent():
    """Convenience function to run the full GitHub agent once."""
    scheduler = GitHubAgentScheduler()
    results = scheduler.run_full_pipeline()
    scheduler.print_pipeline_summary(results)
    return results


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--schedule":
        # Run in scheduler mode
        interval = 24  # Default 24 hours
        if len(sys.argv) > 2:
            interval = int(sys.argv[2])

        scheduler = GitHubAgentScheduler()
        scheduler.run_scheduler(interval)
    else:
        # Run once
        run_full_github_agent()
