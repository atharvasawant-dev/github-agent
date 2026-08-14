# Professional GitHub Profile Builder

A production-minded autonomous agent that maintains a serious GitHub profile and steadily improves existing repositories with small, meaningful commits. It is designed to run unattended every day through GitHub Actions after one-time setup.

The agent behaves like a careful junior-to-mid level developer: it prefers improving real repositories, keeps documentation and structure current, limits daily commit volume, avoids deletion, and logs every action clearly.

## Core Capabilities

- Creates and maintains the special profile repository named `username/username`.
- Generates a professional profile README with introduction, skills, featured projects, current focus, GitHub stats, and contact links.
- Scans owned repositories and detects missing README files, `.gitignore`, CI, tests, dependency manifests, structure, and progress notes.
- Improves repositories with high-quality READMEs, safe structure files, CI workflows, dependency manifests, and lightweight tests.
- Produces natural daily activity with conventional commit messages.
- Supports full dry-run mode before making any account changes.
- Handles GitHub API retries and rate-limit shape changes defensively.

## Project Layout

```text
github-agent/
|-- main.py
|-- config.py
|-- config.yaml
|-- .env.example
|-- requirements.txt
|-- README.md
|-- agent/
|   |-- __init__.py
|   |-- github_client.py
|   |-- repo_scanner.py
|   |-- profile_engine.py
|   |-- readme_improver.py
|   |-- repo_polisher.py
|   |-- activity_engine.py
|   |-- project_generator.py
|   `-- scheduler.py
|-- templates/
`-- .github/workflows/daily-agent.yml
```

## Configuration

Edit `config.yaml`:

```yaml
dry_run: true
max_commits_per_day: 3
activity_intensity: moderate

profile_building_enabled: true
professional_headline: "Software developer focused on practical, production-minded engineering."
profile_location: ""
contact_email: ""
linkedin_url: ""
portfolio_url: ""
featured_project_count: 6

prefer_existing_repos: true
allow_create_new_repos: false
max_new_repositories: 3
include_private_repos: true
repository_allowlist: []
repository_blocklist: []
```

Recommended production settings:

- Keep `profile_building_enabled: true`.
- Keep `max_commits_per_day` between `2` and `3`.
- Use `activity_intensity: moderate` for natural activity.
- Keep `allow_create_new_repos: false` unless you explicitly want the agent to create starter projects.
- Use `repository_blocklist` for repositories the agent should never touch.

## Local Setup

1. Create a classic GitHub Personal Access Token with `repo` and `workflow` scopes.
2. Copy `.env.example` to `.env`.
3. Add your token:

```bash
GITHUB_TOKEN=ghp_your_token_here
```

4. Install dependencies:

```bash
pip install -r requirements.txt
```

5. Run a safe planning pass:

```bash
python main.py --dry-run
```

6. When the plan looks correct, run one live cycle:

```bash
python main.py --run-once
```

## CLI

```bash
python main.py --dry-run
python main.py --run-once
python main.py --schedule
python main.py --status
```

Running `python main.py` defaults to dry-run behavior.

## Daily Automation With GitHub Actions

The workflow at `.github/workflows/daily-agent.yml` runs once per day and waits a random amount of time within the first hour. It then runs:

```bash
python main.py --run-once
```

The workflow uses the secret `GH_AGENT_TOKEN`.

## First-Time Production Setup

1. Commit and push this project to GitHub:

```bash
git add .
git commit -m "feat: build autonomous GitHub profile agent"
git push origin main
```

2. Open the repository on GitHub.
3. Go to `Settings` -> `Secrets and variables` -> `Actions`.
4. Click `New repository secret`.
5. Name the secret:

```text
GH_AGENT_TOKEN
```

6. Paste a classic Personal Access Token with `repo` and `workflow` scopes.
7. Go to the `Actions` tab.
8. Open the `Daily GitHub Agent` workflow.
9. If GitHub prompts you to enable workflows, enable them.
10. Click `Run workflow` once to verify the setup.
11. Check the workflow logs. You should see authentication, repository scanning, planned changes, and completed commits.

After that, the workflow will run automatically every day from the schedule in `.github/workflows/daily-agent.yml`.

## Safety Model

- Dry-run mode shows planned actions without writing.
- Live daily runs are capped by `max_commits_per_day`.
- Archived repositories and forks are skipped.
- The agent never deletes files.
- Repository creation is off by default.
- Rate-limit checks are defensive across PyGithub versions.
- All write operations flow through one GitHub client wrapper.

## What the Agent Commits

Typical commit messages:

- `docs: refresh professional GitHub profile`
- `docs: improve project README`
- `chore: add project gitignore`
- `ci: add basic validation workflow`
- `test: add repository health checks`
- `chore: add maintainable project structure`

The goal is consistent, believable maintenance rather than noisy activity.

## Overview

Autonomous GitHub profile manager agent

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
pip install -r requirements.txt
```


## Tech Stack

- Primary language: Python
- Python dependency management
- GitHub Actions for automation

## Usage

Run the main Python entry point or module for this repository after installing dependencies.


## Architecture

The project should keep source code, tests, and documentation separated. Prefer small modules with explicit responsibilities and avoid mixing runtime code with generated artifacts.

## Validation

Run `python -m compileall .` for a syntax pass. When tests are present, run `pytest` before committing changes.

## Maintenance

Last documentation review: 2026-08-14. Keep this README aligned with the current setup, usage, and repository structure.
