#!/usr/bin/env python3
"""Project Generator Module (Hiring-Optimized Mode).

Creates recruiter-grade, production-level repositories for Python Backend / Full Stack roles.

Rules:
- Create at most 1 repo per execution.
- Only create when total repositories < 12.
- Rotate project types: Backend API -> Automation CLI -> Full Stack -> repeat.
- Do not overwrite existing repositories.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Tuple

from github import Github, GithubException


_COMMIT_MESSAGE = "Initialize production-grade engineering project"
_STATE_FILE = Path(__file__).with_name(".project_generator_state.json")


class ProjectGenerationError(RuntimeError):
    pass


@dataclass(frozen=True)
class GenerationDecision:
    should_create: bool
    reason: str


class ProjectGenerator:
    """Hiring-optimized project generator that uses PyGithub to create and populate repositories."""

    def __init__(self, github_client: Github):
        self.github = github_client
        self.user = None
        self._setup_logging()

    def _setup_logging(self) -> None:
        logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
        self.logger = logging.getLogger(__name__)

    def authenticate(self) -> bool:
        try:
            self.user = self.github.get_user()
            self.logger.info("Authenticated as: %s", self.user.login)
            return True
        except GithubException as e:
            self.logger.error("Authentication failed: %s", e)
            return False

    def _list_repo_names(self) -> List[str]:
        if not self.user:
            raise ProjectGenerationError("Not authenticated")
        return [r.name for r in self.user.get_repos(type="owner")]

    def should_create_new_repo(self) -> GenerationDecision:
        if not self.user:
            return GenerationDecision(False, "Not authenticated")
        try:
            repos = list(self.user.get_repos(type="owner"))
            if len(repos) >= 12:
                return GenerationDecision(False, f"Repo count is {len(repos)} (>= 12)")
            return GenerationDecision(True, f"Repo count is {len(repos)} (< 12)")
        except GithubException as e:
            return GenerationDecision(False, f"Failed to list repositories: {e}")

    def generate_new_projects(self, count: int = 1) -> Dict[str, Any]:
        """Create at most 1 repository in hiring-optimized mode."""
        result: Dict[str, Any] = {
            "total_requested": count,
            "created": 0,
            "skipped": 0,
            "details": [],
        }

        if not self.user and not self.authenticate():
            result["details"].append({"success": False, "error": "Authentication failed"})
            return result

        decision = self.should_create_new_repo()
        if not decision.should_create:
            result["skipped"] = 1
            result["details"].append({"success": True, "skipped": True, "reason": decision.reason})
            return result

        created = self._create_one_project()
        result["details"].append(created)
        result["created"] = 1 if created.get("success") else 0
        return result

    def _create_one_project(self) -> Dict[str, Any]:
        if not self.user:
            raise ProjectGenerationError("Not authenticated")

        existing_names = set(self._list_repo_names())
        next_kind = self._next_project_kind(existing_names)
        repo_name, description = self._choose_repo_name_and_description(next_kind, existing_names)

        if repo_name in existing_names:
            return {"success": True, "skipped": True, "reason": f"Repo {repo_name} already exists"}

        try:
            self.user.get_repo(repo_name)
            return {"success": True, "skipped": True, "reason": f"Repo {repo_name} already exists"}
        except GithubException as e:
            if getattr(e, "status", None) != 404:
                return {"success": False, "error": f"Failed checking repo existence: {e}"}

        files = self._build_project_files(next_kind, repo_name)
        if not files:
            return {"success": False, "error": "No files generated"}

        try:
            repo = self.user.create_repo(
                name=repo_name,
                description=description,
                private=False,
                has_issues=True,
                has_projects=False,
                has_wiki=False,
                auto_init=False,
            )
            self.logger.info("Created repository: %s", repo_name)

            self._upload_files(repo, files)
            self._write_rotation_state(next_kind)

            return {
                "success": True,
                "repo_name": repo_name,
                "repo_url": repo.html_url,
                "project_type": next_kind,
            }
        except GithubException as e:
            return {"success": False, "repo_name": repo_name, "error": f"GitHub API error: {e}"}
        except Exception as e:
            return {"success": False, "repo_name": repo_name, "error": f"Unexpected error: {e}"}

    def _upload_files(self, repo: Any, files: Mapping[str, str]) -> None:
        for path, content in files.items():
            try:
                repo.create_file(path=path, message=_COMMIT_MESSAGE, content=content, branch=repo.default_branch)
            except GithubException as e:
                if getattr(e, "status", None) == 422:
                    self.logger.warning("Skipping existing path %s (422)", path)
                    continue
                self.logger.error("Failed to upload %s: %s", path, e)
                raise

    def _load_rotation_state(self) -> Dict[str, Any]:
        try:
            if not _STATE_FILE.exists():
                return {"last": None}
            return json.loads(_STATE_FILE.read_text(encoding="utf-8"))
        except Exception:
            return {"last": None}

    def _write_rotation_state(self, last_kind: str) -> None:
        payload = {"last": last_kind, "updated_at": datetime.utcnow().isoformat()}
        _STATE_FILE.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def _next_project_kind(self, existing_names: set[str]) -> str:
        """Rotation: backend_api -> automation_cli -> fullstack_app -> repeat.

        Avoid generating the same type repeatedly when possible by checking prefixes.
        """

        state = self._load_rotation_state()
        last = state.get("last")
        rotation = ["backend_api", "automation_cli", "fullstack_app"]

        if last in rotation:
            idx = (rotation.index(last) + 1) % len(rotation)
        else:
            idx = 0

        for _ in range(len(rotation)):
            kind = rotation[idx]
            prefix = self._kind_prefix(kind)
            # If we already have a repo with this prefix and there are other options, rotate away.
            if any(name.startswith(prefix) for name in existing_names) and len(existing_names) > 0:
                idx = (idx + 1) % len(rotation)
                continue
            return kind

        return rotation[idx]

    def _kind_prefix(self, kind: str) -> str:
        if kind == "backend_api":
            return "production-fastapi-"
        if kind == "automation_cli":
            return "engineering-cli-"
        if kind == "fullstack_app":
            return "fullstack-fastapi-"
        return "engineering-project-"

    def _choose_repo_name_and_description(self, kind: str, existing: set[str]) -> Tuple[str, str]:
        base = self._kind_prefix(kind)
        candidates = {
            "backend_api": ("service", "Production-grade FastAPI service with modular architecture, validation, and testing"),
            "automation_cli": (
                "log-auditor",
                "Engineering CLI tool for log auditing, anomaly spotting, and reporting with structured output",
            ),
            "fullstack_app": (
                "dashboard",
                "Full-stack FastAPI app with server-rendered UI and JSON API endpoints for a developer dashboard",
            ),
        }

        suffix, desc = candidates.get(kind, ("project", "Production-grade engineering project"))
        name = f"{base}{suffix}"
        if name not in existing:
            return name, desc
        for i in range(2, 50):
            alt = f"{name}-{i}"
            if alt not in existing:
                return alt, desc
        raise ProjectGenerationError("Unable to find available repository name")

    def _build_project_files(self, kind: str, repo_name: str) -> Dict[str, str]:
        if kind == "backend_api":
            return self._backend_api_files(repo_name)
        if kind == "automation_cli":
            return self._automation_cli_files(repo_name)
        if kind == "fullstack_app":
            return self._fullstack_files(repo_name)
        raise ProjectGenerationError(f"Unknown project kind: {kind}")

    def _common_gitignore(self) -> str:
        return (
            "__pycache__/\n*.py[cod]\n*$py.class\n\n"
            ".venv/\nvenv/\n.env\n.env.*\n\n"
            ".pytest_cache/\n.coverage\nhtmlcov/\n\n"
            "dist/\nbuild/\n*.egg-info/\n\n"
            "*.log\n\n"
            ".DS_Store\nThumbs.db\n"
        )

    def _common_ci_workflow(self) -> str:
        return (
            "name: CI\n\n"
            "on:\n  push:\n    branches: [ main, master ]\n  pull_request:\n    branches: [ main, master ]\n\n"
            "jobs:\n  test:\n    runs-on: ubuntu-latest\n    strategy:\n      matrix:\n        python-version: ['3.10', '3.11']\n\n"
            "    steps:\n      - uses: actions/checkout@v4\n"
            "      - name: Set up Python ${{ matrix.python-version }}\n        uses: actions/setup-python@v5\n        with:\n          python-version: ${{ matrix.python-version }}\n"
            "      - name: Install dependencies\n        run: |\n          python -m pip install --upgrade pip\n          pip install -r requirements.txt\n"
            "      - name: Lint\n        run: |\n          python -m pip install ruff\n          ruff check .\n"
            "      - name: Run tests\n        run: |\n          python -m pip install pytest\n          pytest -q\n"
        )

    def _backend_api_files(self, repo_name: str) -> Dict[str, str]:
        requirements = "fastapi==0.115.0\nuvicorn[standard]==0.30.6\npydantic==2.8.2\npytest==8.3.2\nhttpx==0.27.2\nruff==0.6.3\n"
        readme = f"""# Production FastAPI Service\n\nA production-grade FastAPI service designed to demonstrate backend engineering fundamentals recruiters look for: modular architecture, request validation, structured logging, error handling, and tests.\n\n## Architecture\n\n- `src/main.py`: application entry point\n- `src/routes/`: API route modules\n- `src/services/`: business logic\n- `src/models/`: Pydantic domain models\n\n## Features\n\n- Health and readiness endpoints\n- CRUD-style API for work items\n- Structured logging\n- Input validation and consistent error responses\n- Pytest test suite\n\n## Installation\n\n```bash\npython -m venv .venv\nsource .venv/bin/activate\npip install -r requirements.txt\n```\n\n## Usage\n\n```bash\nuvicorn src.main:app --reload\n# GET http://127.0.0.1:8000/health\n```\n\n## Project Structure\n\n```\n{repo_name}/\n  src/\n    main.py\n    routes/\n    services/\n    models/\n  tests/\n  .github/workflows/ci.yml\n  README.md\n  requirements.txt\n  .gitignore\n```\n"""

        return {
            "src/main.py": self._fastapi_main_py(app_title="Work Items API"),
            "src/routes/__init__.py": "",
            "src/routes/health.py": self._fastapi_health_routes(),
            "src/routes/work_items.py": self._fastapi_work_items_routes(),
            "src/services/__init__.py": "",
            "src/services/work_items_service.py": self._work_items_service_py(),
            "src/models/__init__.py": "",
            "src/models/work_item.py": self._work_item_model_py(),
            "tests/test_health.py": self._test_health_py(),
            "tests/test_work_items.py": self._test_work_items_py(),
            "README.md": readme,
            "requirements.txt": requirements,
            ".gitignore": self._common_gitignore(),
            ".github/workflows/ci.yml": self._common_ci_workflow(),
        }

    def _automation_cli_files(self, repo_name: str) -> Dict[str, str]:
        requirements = "pytest==8.3.2\nruff==0.6.3\n"
        readme = f"""# Engineering Log Auditor CLI\n\nA production-grade CLI tool for software engineers to audit log files, detect anomalies (spikes, error bursts), and generate machine-readable reports for incident reviews.\n\n## Architecture\n\n- `src/main.py`: CLI entry point\n- `src/services/`: parsing and analysis\n- `src/models/`: typed report structures\n\n## Features\n\n- Parses JSONL or plain text logs\n- Detects error-rate spikes\n- Produces summary report in JSON\n- Designed for automation and CI usage\n\n## Installation\n\n```bash\npython -m venv .venv\nsource .venv/bin/activate\npip install -r requirements.txt\n```\n\n## Usage\n\n```bash\npython -m src.main analyze --path ./app.log --window 200 --threshold 0.15\n```\n\n## Project Structure\n\n```\n{repo_name}/\n  src/\n  tests/\n  .github/workflows/ci.yml\n  README.md\n  requirements.txt\n  .gitignore\n```\n"""

        return {
            "src/main.py": self._cli_main_py(),
            "src/services/__init__.py": "",
            "src/services/log_parser.py": self._log_parser_py(),
            "src/services/analyzer.py": self._log_analyzer_py(),
            "src/models/__init__.py": "",
            "src/models/report.py": self._report_model_py(),
            "tests/test_analyzer.py": self._test_analyzer_py(),
            "README.md": readme,
            "requirements.txt": requirements,
            ".gitignore": self._common_gitignore(),
            ".github/workflows/ci.yml": self._common_ci_workflow(),
        }

    def _fullstack_files(self, repo_name: str) -> Dict[str, str]:
        requirements = (
            "fastapi==0.115.0\nuvicorn[standard]==0.30.6\n"
            "jinja2==3.1.4\npython-multipart==0.0.9\n"
            "pytest==8.3.2\nhttpx==0.27.2\nruff==0.6.3\n"
        )
        readme = f"""# Full-Stack FastAPI Developer Dashboard\n\nA hiring-optimized full-stack project: FastAPI backend + server-rendered HTML UI + JSON API endpoints. It demonstrates API design, template rendering, structured logging, and test coverage.\n\n## Architecture\n\n- `src/main.py`: app entry point\n- `src/routes/`: API + UI routes\n- `src/services/`: business logic\n- `src/models/`: typed models\n- `templates/`: Jinja2 templates\n- `static/`: minimal CSS\n\n## Installation\n\n```bash\npython -m venv .venv\nsource .venv/bin/activate\npip install -r requirements.txt\n```\n\n## Usage\n\n```bash\nuvicorn src.main:app --reload\n# Open http://127.0.0.1:8000/\n```\n\n## Project Structure\n\n```\n{repo_name}/\n  src/\n  templates/\n  static/\n  tests/\n  .github/workflows/ci.yml\n  README.md\n  requirements.txt\n  .gitignore\n```\n"""

        return {
            "src/main.py": self._fastapi_main_py(app_title="Developer Dashboard"),
            "src/routes/__init__.py": "",
            "src/routes/health.py": self._fastapi_health_routes(),
            "src/routes/dashboard.py": self._dashboard_routes_py(),
            "src/routes/api_metrics.py": self._api_metrics_routes_py(),
            "src/services/__init__.py": "",
            "src/services/metrics_service.py": self._metrics_service_py(),
            "src/models/__init__.py": "",
            "src/models/metrics.py": self._metrics_model_py(),
            "templates/index.html": self._template_index_html(),
            "static/styles.css": self._static_css(),
            "tests/test_ui.py": self._test_ui_py(),
            "README.md": readme,
            "requirements.txt": requirements,
            ".gitignore": self._common_gitignore(),
            ".github/workflows/ci.yml": self._common_ci_workflow(),
        }

    def _fastapi_main_py(self, app_title: str) -> str:
        return (
            '"""FastAPI application entry point."""\n\n'
            "import logging\n"
            "from fastapi import FastAPI\n"
            "from src.routes.health import router as health_router\n"
            "\n"
            "logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')\n"
            "logger = logging.getLogger(__name__)\n\n"
            f"app = FastAPI(title={app_title!r}, version='1.0.0')\n\n"
            "app.include_router(health_router)\n\n"
            "try:\n"
            "    from src.routes.work_items import router as work_items_router\n"
            "    app.include_router(work_items_router, prefix='/v1')\n"
            "except Exception:\n"
            "    pass\n\n"
            "try:\n"
            "    from src.routes.dashboard import router as dashboard_router\n"
            "    app.include_router(dashboard_router)\n"
            "    from src.routes.api_metrics import router as metrics_router\n"
            "    app.include_router(metrics_router, prefix='/api')\n"
            "except Exception:\n"
            "    pass\n\n"
            "@app.on_event('startup')\n"
            "def on_startup() -> None:\n"
            "    logger.info('Application startup complete')\n"
        )

    def _fastapi_health_routes(self) -> str:
        return (
            '"""Health and readiness endpoints."""\n\n'
            "from fastapi import APIRouter\n\n"
            "router = APIRouter(tags=['health'])\n\n"
            "@router.get('/health')\n"
            "def health() -> dict:\n"
            "    return {'status': 'ok'}\n\n"
            "@router.get('/ready')\n"
            "def ready() -> dict:\n"
            "    return {'ready': True}\n"
        )

    def _work_item_model_py(self) -> str:
        return (
            '"""Domain models for Work Items."""\n\n'
            "from datetime import datetime\n"
            "from pydantic import BaseModel, Field\n\n"
            "class WorkItemCreate(BaseModel):\n"
            "    title: str = Field(min_length=3, max_length=200)\n"
            "    description: str = Field(default='', max_length=2000)\n\n"
            "class WorkItem(WorkItemCreate):\n"
            "    id: int\n"
            "    created_at: datetime\n"
        )

    def _work_items_service_py(self) -> str:
        return (
            '"""Business logic for Work Items (in-memory repository)."""\n\n'
            "import logging\n"
            "from datetime import datetime\n"
            "from typing import Dict, List\n\n"
            "from src.models.work_item import WorkItem, WorkItemCreate\n\n"
            "logger = logging.getLogger(__name__)\n\n"
            "class WorkItemsService:\n"
            "    def __init__(self) -> None:\n"
            "        self._db: Dict[int, WorkItem] = {}\n"
            "        self._seq = 0\n\n"
            "    def list_items(self) -> List[WorkItem]:\n"
            "        return sorted(self._db.values(), key=lambda x: x.id)\n\n"
            "    def create_item(self, payload: WorkItemCreate) -> WorkItem:\n"
            "        self._seq += 1\n"
            "        item = WorkItem(id=self._seq, created_at=datetime.utcnow(), **payload.model_dump())\n"
            "        self._db[item.id] = item\n"
            "        logger.info('Created work_item id=%s title=%s', item.id, item.title)\n"
            "        return item\n\n"
            "    def get_item(self, item_id: int) -> WorkItem:\n"
            "        if item_id not in self._db:\n"
            "            raise KeyError('work_item_not_found')\n"
            "        return self._db[item_id]\n\n"
            "    def delete_item(self, item_id: int) -> None:\n"
            "        if item_id not in self._db:\n"
            "            raise KeyError('work_item_not_found')\n"
            "        del self._db[item_id]\n"
            "        logger.info('Deleted work_item id=%s', item_id)\n"
        )

    def _fastapi_work_items_routes(self) -> str:
        return (
            '"""Work Items REST endpoints."""\n\n'
            "import logging\n"
            "from fastapi import APIRouter, HTTPException\n\n"
            "from src.models.work_item import WorkItem, WorkItemCreate\n"
            "from src.services.work_items_service import WorkItemsService\n\n"
            "logger = logging.getLogger(__name__)\n"
            "router = APIRouter(tags=['work-items'])\n"
            "service = WorkItemsService()\n\n"
            "@router.get('/work-items', response_model=list[WorkItem])\n"
            "def list_work_items() -> list[WorkItem]:\n"
            "    return service.list_items()\n\n"
            "@router.post('/work-items', response_model=WorkItem, status_code=201)\n"
            "def create_work_item(payload: WorkItemCreate) -> WorkItem:\n"
            "    try:\n"
            "        return service.create_item(payload)\n"
            "    except Exception as e:\n"
            "        logger.exception('Failed to create work item')\n"
            "        raise HTTPException(status_code=500, detail=str(e))\n\n"
            "@router.get('/work-items/{item_id}', response_model=WorkItem)\n"
            "def get_work_item(item_id: int) -> WorkItem:\n"
            "    try:\n"
            "        return service.get_item(item_id)\n"
            "    except KeyError:\n"
            "        raise HTTPException(status_code=404, detail='Not found')\n\n"
            "@router.delete('/work-items/{item_id}', status_code=204)\n"
            "def delete_work_item(item_id: int) -> None:\n"
            "    try:\n"
            "        service.delete_item(item_id)\n"
            "        return None\n"
            "    except KeyError:\n"
            "        raise HTTPException(status_code=404, detail='Not found')\n"
        )

    def _test_health_py(self) -> str:
        return (
            "import pytest\n"
            "from fastapi.testclient import TestClient\n\n"
            "from src.main import app\n\n"
            "client = TestClient(app)\n\n"
            "def test_health_ok():\n"
            "    r = client.get('/health')\n"
            "    assert r.status_code == 200\n"
            "    assert r.json()['status'] == 'ok'\n"
        )

    def _test_work_items_py(self) -> str:
        return (
            "from fastapi.testclient import TestClient\n\n"
            "from src.main import app\n\n"
            "client = TestClient(app)\n\n"
            "def test_create_list_get_delete():\n"
            "    r = client.post('/v1/work-items', json={'title': 'Ship feature', 'description': 'Implement X'})\n"
            "    assert r.status_code == 201\n"
            "    item = r.json()\n"
            "    assert item['id'] == 1\n\n"
            "    r = client.get('/v1/work-items')\n"
            "    assert r.status_code == 200\n"
            "    assert len(r.json()) == 1\n\n"
            "    r = client.get('/v1/work-items/1')\n"
            "    assert r.status_code == 200\n\n"
            "    r = client.delete('/v1/work-items/1')\n"
            "    assert r.status_code == 204\n"
        )

    def _cli_main_py(self) -> str:
        return (
            '"""CLI entry point."""\n\n'
            "import argparse\n"
            "import json\n"
            "import logging\n"
            "from pathlib import Path\n\n"
            "from src.services.analyzer import analyze_log\n\n"
            "logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')\n"
            "logger = logging.getLogger(__name__)\n\n"
            "def _build_parser() -> argparse.ArgumentParser:\n"
            "    p = argparse.ArgumentParser(prog='log-auditor', description='Audit logs and produce anomaly reports.')\n"
            "    sub = p.add_subparsers(dest='cmd', required=True)\n"
            "    a = sub.add_parser('analyze', help='Analyze a log file')\n"
            "    a.add_argument('--path', required=True, help='Path to log file')\n"
            "    a.add_argument('--window', type=int, default=200, help='Sliding window size')\n"
            "    a.add_argument('--threshold', type=float, default=0.15, help='Error-rate threshold for spike detection')\n"
            "    a.add_argument('--out', default='-', help='Output path for JSON report, or - for stdout')\n"
            "    return p\n\n"
            "def main() -> int:\n"
            "    args = _build_parser().parse_args()\n"
            "    report = analyze_log(Path(args.path), window=args.window, threshold=args.threshold)\n"
            "    payload = report.to_dict()\n"
            "    if args.out == '-':\n"
            "        print(json.dumps(payload, indent=2))\n"
            "    else:\n"
            "        Path(args.out).write_text(json.dumps(payload, indent=2), encoding='utf-8')\n"
            "        logger.info('Report written to %s', args.out)\n"
            "    return 0\n\n"
            "if __name__ == '__main__':\n"
            "    raise SystemExit(main())\n"
        )

    def _report_model_py(self) -> str:
        return (
            '"""Typed report model."""\n\n'
            "from dataclasses import dataclass\n"
            "from datetime import datetime\n"
            "from typing import Any, Dict, List\n\n"
            "@dataclass(frozen=True)\n"
            "class Spike:\n"
            "    index: int\n"
            "    error_rate: float\n"
            "    window: int\n\n"
            "    def to_dict(self) -> Dict[str, Any]:\n"
            "        return {'index': self.index, 'error_rate': self.error_rate, 'window': self.window}\n\n"
            "@dataclass(frozen=True)\n"
            "class Report:\n"
            "    path: str\n"
            "    total_lines: int\n"
            "    error_lines: int\n"
            "    error_rate: float\n"
            "    spikes: List[Spike]\n"
            "    generated_at: str\n\n"
            "    def to_dict(self) -> Dict[str, Any]:\n"
            "        return {\n"
            "            'path': self.path,\n"
            "            'total_lines': self.total_lines,\n"
            "            'error_lines': self.error_lines,\n"
            "            'error_rate': self.error_rate,\n"
            "            'spikes': [s.to_dict() for s in self.spikes],\n"
            "            'generated_at': self.generated_at,\n"
            "        }\n"
        )

    def _log_parser_py(self) -> str:
        return (
            '"""Log parsing utilities."""\n\n'
            "import json\n"
            "from typing import Iterable, Iterator, Tuple\n\n"
            "def iter_lines(path) -> Iterator[str]:\n"
            "    with open(path, 'r', encoding='utf-8', errors='replace') as f:\n"
            "        for line in f:\n"
            "            line = line.strip()\n"
            "            if line:\n"
            "                yield line\n\n"
            "def classify_line(line: str) -> Tuple[bool, str]:\n"
            "    # JSON logs: treat level=error as error\n"
            "    if line.startswith('{') and line.endswith('}'):\n"
            "        try:\n"
            "            obj = json.loads(line)\n"
            "            level = str(obj.get('level', '')).lower()\n"
            "            msg = str(obj.get('message', line))\n"
            "            return (level in {'error', 'fatal', 'critical'}, msg)\n"
            "        except Exception:\n"
            "            pass\n"
            "    lowered = line.lower()\n"
            "    is_err = any(tok in lowered for tok in [' error ', 'exception', 'traceback', 'fatal']) or lowered.startswith('error')\n"
            "    return is_err, line\n"
        )

    def _log_analyzer_py(self) -> str:
        return (
            '"""Log analysis with spike detection."""\n\n'
            "import logging\n"
            "from datetime import datetime\n"
            "from pathlib import Path\n"
            "from typing import List\n\n"
            "from src.models.report import Report, Spike\n"
            "from src.services.log_parser import iter_lines, classify_line\n\n"
            "logger = logging.getLogger(__name__)\n\n"
            "def analyze_log(path: Path, window: int = 200, threshold: float = 0.15) -> Report:\n"
            "    if window < 20:\n"
            "        raise ValueError('window must be >= 20')\n"
            "    if threshold <= 0 or threshold >= 1:\n"
            "        raise ValueError('threshold must be between 0 and 1')\n\n"
            "    total = 0\n"
            "    error_flags: List[int] = []\n\n"
            "    for line in iter_lines(path):\n"
            "        is_err, _ = classify_line(line)\n"
            "        error_flags.append(1 if is_err else 0)\n"
            "        total += 1\n\n"
            "    err = sum(error_flags)\n"
            "    overall_rate = (err / total) if total else 0.0\n\n"
            "    spikes: List[Spike] = []\n"
            "    if total >= window:\n"
            "        current = sum(error_flags[:window])\n"
            "        for i in range(window, total + 1):\n"
            "            rate = current / window\n"
            "            if rate >= threshold:\n"
            "                spikes.append(Spike(index=i - 1, error_rate=rate, window=window))\n"
            "            if i < total:\n"
            "                current += error_flags[i] - error_flags[i - window]\n\n"
            "    logger.info('Analyzed %s lines, error_rate=%.3f spikes=%s', total, overall_rate, len(spikes))\n"
            "    return Report(\n"
            "        path=str(path),\n"
            "        total_lines=total,\n"
            "        error_lines=err,\n"
            "        error_rate=overall_rate,\n"
            "        spikes=spikes,\n"
            "        generated_at=datetime.utcnow().isoformat(),\n"
            "    )\n"
        )

    def _test_analyzer_py(self) -> str:
        return (
            "from pathlib import Path\n\n"
            "from src.services.analyzer import analyze_log\n\n"
            "def test_analyze_log_detects_spike(tmp_path: Path):\n"
            "    p = tmp_path / 'app.log'\n"
            "    lines = []\n"
            "    lines.extend(['INFO ok' for _ in range(100)])\n"
            "    lines.extend(['ERROR boom' for _ in range(60)])\n"
            "    lines.extend(['INFO ok' for _ in range(40)])\n"
            "    p.write_text('\\n'.join(lines), encoding='utf-8')\n\n"
            "    report = analyze_log(p, window=50, threshold=0.5)\n"
            "    assert report.total_lines == 200\n"
            "    assert report.error_lines == 60\n"
            "    assert len(report.spikes) > 0\n"
        )

    def _dashboard_routes_py(self) -> str:
        return (
            '"""UI routes for the dashboard."""\n\n'
            "from fastapi import APIRouter, Request\n"
            "from fastapi.responses import HTMLResponse\n"
            "from fastapi.templating import Jinja2Templates\n\n"
            "router = APIRouter(tags=['ui'])\n"
            "templates = Jinja2Templates(directory='templates')\n\n"
            "@router.get('/', response_class=HTMLResponse)\n"
            "def index(request: Request):\n"
            "    return templates.TemplateResponse('index.html', {'request': request})\n"
        )

    def _metrics_model_py(self) -> str:
        return (
            '"""Typed metrics model."""\n\n'
            "from pydantic import BaseModel\n\n"
            "class Metrics(BaseModel):\n"
            "    service: str\n"
            "    status: str\n"
            "    now_utc: str\n"
        )

    def _metrics_service_py(self) -> str:
        return (
            '"""Business logic for metrics."""\n\n'
            "from datetime import datetime\n\n"
            "from src.models.metrics import Metrics\n\n"
            "def current_metrics(service: str) -> Metrics:\n"
            "    return Metrics(service=service, status='ok', now_utc=datetime.utcnow().isoformat())\n"
        )

    def _api_metrics_routes_py(self) -> str:
        return (
            '"""JSON API endpoints."""\n\n'
            "from fastapi import APIRouter\n\n"
            "from src.models.metrics import Metrics\n"
            "from src.services.metrics_service import current_metrics\n\n"
            "router = APIRouter(tags=['api'])\n\n"
            "@router.get('/metrics', response_model=Metrics)\n"
            "def metrics() -> Metrics:\n"
            "    return current_metrics(service='developer-dashboard')\n"
        )

    def _template_index_html(self) -> str:
        return (
            "<!doctype html>\n"
            "<html lang='en'>\n"
            "  <head>\n"
            "    <meta charset='utf-8'/>\n"
            "    <meta name='viewport' content='width=device-width, initial-scale=1'/>\n"
            "    <title>Developer Dashboard</title>\n"
            "    <link rel='stylesheet' href='/static/styles.css'/>\n"
            "  </head>\n"
            "  <body>\n"
            "    <main class='container'>\n"
            "      <h1>Developer Dashboard</h1>\n"
            "      <p>Hiring-optimized full-stack FastAPI app (UI + API).</p>\n"
            "      <section class='card'>\n"
            "        <h2>Live Metrics</h2>\n"
            "        <pre id='metrics'>Loading...</pre>\n"
            "      </section>\n"
            "    </main>\n"
            "    <script>\n"
            "      fetch('/api/metrics')\n"
            "        .then(r => r.json())\n"
            "        .then(data => { document.getElementById('metrics').textContent = JSON.stringify(data, null, 2); })\n"
            "        .catch(err => { document.getElementById('metrics').textContent = String(err); });\n"
            "    </script>\n"
            "  </body>\n"
            "</html>\n"
        )

    def _static_css(self) -> str:
        return (
            "body{font-family:system-ui,-apple-system,Segoe UI,Roboto,Ubuntu,Arial,sans-serif;margin:0;background:#0b1020;color:#e7e9ee;}\n"
            ".container{max-width:900px;margin:0 auto;padding:32px;}\n"
            "h1{font-size:32px;margin:0 0 8px;}\n"
            "p{opacity:.9;}\n"
            ".card{background:#141a33;border:1px solid rgba(255,255,255,.08);border-radius:12px;padding:16px;margin-top:16px;}\n"
            "pre{background:#0f1530;border-radius:10px;padding:12px;overflow:auto;}\n"
        )

    def _test_ui_py(self) -> str:
        return (
            "from fastapi.testclient import TestClient\n\n"
            "from src.main import app\n\n"
            "client = TestClient(app)\n\n"
            "def test_index_renders():\n"
            "    r = client.get('/')\n"
            "    assert r.status_code == 200\n"
            "    assert 'Developer Dashboard' in r.text\n\n"
            "def test_metrics_api():\n"
            "    r = client.get('/api/metrics')\n"
            "    assert r.status_code == 200\n"
            "    payload = r.json()\n"
            "    assert payload['status'] == 'ok'\n"
        )
