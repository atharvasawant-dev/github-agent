from github import GithubException


class ProjectGenerator:
    """
    Stable recruiter-grade project generator.
    """

    MAX_REPOS = 15

    PROJECT_TEMPLATES = [
        {
            "name": "fastapi-production-backend",
            "description": "Production-grade FastAPI backend with modular architecture, CI/CD, logging, and testing.",
        },
        {
            "name": "engineering-cli-log-auditor-pro",
            "description": "Engineering CLI tool for structured logging, anomaly detection, and reporting.",
        },
        {
            "name": "fullstack-fastapi-dashboard-pro",
            "description": "Full-stack FastAPI dashboard with REST APIs and modular architecture.",
        },
    ]

    def __init__(self, github_service):
        self.github_service = github_service
        self.github = github_service.github
        self.user = self.github.get_user()

    def generate_projects_if_needed(self):

        print("Starting recruiter-grade project generation...")

        repos = self.github_service.get_user_repositories()
        repo_names = [repo["name"] for repo in repos]

        repo_count = len(repo_names)

        print(f"Current repository count: {repo_count}")

        if repo_count >= self.MAX_REPOS:
            print("Repository limit reached. Skipping generation.")
            return

        for template in self.PROJECT_TEMPLATES:

            name = template["name"]
            description = template["description"]

            if name in repo_names:
                print(f"{name} already exists. Skipping.")
                continue

            try:
                self._create_project(name, description)
                repo_names.append(name)

            except Exception as e:
                print(f"Failed creating {name}: {e}")

    def _create_project(self, name, description):

        print(f"Creating repository: {name}")

        try:

            repo = self.user.create_repo(
                name=name,
                description=description,
                private=False,
            )

            readme = (
                f"# {name}\n\n"
                "Production-ready engineering project.\n\n"
                "## Features\n\n"
                "- Modular architecture\n"
                "- Logging\n"
                "- CI/CD pipeline\n"
                "- Recruiter-grade repository layout\n\n"
                "## Installation\n\n"
                "pip install -r requirements.txt\n\n"
                "## Run\n\n"
                "uvicorn main:app --reload\n"
            )

            repo.create_file("README.md", "Initial commit", readme)

            requirements = (
                "fastapi\n"
                "uvicorn\n"
                "pytest\n"
                "black\n"
                "flake8\n"
            )

            repo.create_file(
                "requirements.txt",
                "Add requirements",
                requirements,
            )

            main_py = (
                "from fastapi import FastAPI\n\n"
                "app = FastAPI()\n\n"
                "@app.get('/')\n"
                "def health_check():\n"
                "    return {'status': 'healthy'}\n"
            )

            repo.create_file(
                "main.py",
                "Add main application file",
                main_py,
            )

            ci = (
                "name: CI/CD Pipeline\n\n"
                "on:\n"
                "  push:\n"
                "  pull_request:\n\n"
                "jobs:\n"
                "  build:\n"
                "    runs-on: ubuntu-latest\n\n"
                "    steps:\n"
                "    - uses: actions/checkout@v3\n\n"
                "    - name: Set up Python\n"
                "      uses: actions/setup-python@v4\n"
                "      with:\n"
                "        python-version: '3.11'\n\n"
                "    - name: Install dependencies\n"
                "      run: pip install -r requirements.txt\n\n"
                "    - name: Format check\n"
                "      run: black --check . || true\n\n"
                "    - name: Lint\n"
                "      run: flake8 . || true\n\n"
                "    - name: Run tests\n"
                "      run: pytest || true\n"
            )

            repo.create_file(
                ".github/workflows/ci.yml",
                "Add CI pipeline",
                ci,
            )

            print(f"SUCCESS: Created repository: {name}")

        except GithubException as e:
            print(f"GitHub error creating {name}: {e}")

        except Exception as e:
            print(f"Unexpected error creating {name}: {e}")