from github import GithubException
import logging
import base64


class ProjectGenerator:

    def __init__(self, github_service):
        self.github_service = github_service
        self.github = github_service.github
        self.user = self.github.get_user()

    def generate_projects_if_needed(self):

        print("Starting recruiter-grade project generation...")

        repos = self.github_service.get_user_repositories()
        repo_count = len(repos)

        print(f"Current repository count: {repo_count}")

        MAX_REPOS = 15

        if repo_count >= MAX_REPOS:
            print("Repository limit reached. Skipping generation.")
            return

        project_name = "fastapi-production-backend"

        print(f"Creating repository: {project_name}")

        try:

            repo = self.user.create_repo(
                name=project_name,
                description="Production-grade FastAPI backend with modular architecture, CI/CD, logging, and testing.",
                private=False,
            )

            readme = """# FastAPI Production Backend

Production-ready FastAPI backend template.

Features:

* Modular architecture
* Logging
* CI/CD ready
* Recruiter-grade structure

Installation:
pip install -r requirements.txt

Run:
uvicorn main:app --reload
"""

            repo.create_file("README.md", "Initial commit", readme)

            print(f"SUCCESS: Created recruiter-grade repository: {project_name}")

        except GithubException as e:

            print(f"Repository may already exist or error occurred: {e}")
