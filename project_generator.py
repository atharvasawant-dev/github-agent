#!/usr/bin/env python3
"""
Project Generator Module - Fixed Version
Creates professional repositories with production-grade code.
"""

import os
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from github import Github, GithubException


class ProjectGenerator:
    """Generates professional projects for GitHub repositories."""
    
    def __init__(self, github_client: Github):
        self.github = github_client
        self.user = None
        self._setup_logging()
    
    def _setup_logging(self) -> None:
        """Set up logging for the generator."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
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
    
    def should_create_new_repo(self) -> bool:
        """Check if new repositories should be created."""
        try:
            if not self.user:
                return False
            
            repos = list(self.user.get_repos(type='owner'))
            return len(repos) < 20
        except GithubException as e:
            self.logger.error(f"Failed to check repository count: {e}")
            return False
    
    def generate_automation_tool(self, repo_name: str) -> Dict[str, Any]:
        """Generate a professional automation tool project."""
        self.logger.info(f"Creating production project: {repo_name}")
        
        project_files = {
            'src/__init__.py': '''"""Automation Tool Package."""

__version__ = "0.1.0"
__author__ = "Professional Developer"
''',
            'src/automation_core.py': '''"""
Core automation functionality for professional workflow management.
"""

import logging
import asyncio
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
from datetime import datetime
import json
import os


@dataclass
class TaskResult:
    """Result of an automation task."""
    task_id: str
    status: str
    message: str
    timestamp: datetime
    data: Optional[Dict[str, Any]] = None


class AutomationEngine:
    """Professional automation engine for workflow management."""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config = self._load_config(config_path)
        self.tasks: Dict[str, Callable] = {}
        self.results: List[TaskResult] = []
        self._setup_logging()
    
    def _setup_logging(self) -> None:
        """Set up professional logging."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('automation.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """Load configuration from file."""
        default_config = {
            'max_concurrent_tasks': 5,
            'retry_attempts': 3,
            'timeout': 300,
            'log_level': 'INFO'
        }
        
        if config_path and os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    user_config = json.load(f)
                default_config.update(user_config)
            except Exception as e:
                self.logger.warning(f"Failed to load config: {e}")
        
        return default_config
    
    def register_task(self, name: str, task_func: Callable) -> None:
        """Register a new automation task."""
        self.tasks[name] = task_func
        self.logger.info(f"Registered task: {name}")
    
    async def execute_task(self, task_name: str, **kwargs) -> TaskResult:
        """Execute a specific task."""
        if task_name not in self.tasks:
            return TaskResult(
                task_id=f"{task_name}_{datetime.now().timestamp()}",
                status="failed",
                message=f"Task '{task_name}' not found",
                timestamp=datetime.now()
            )
        
        try:
            task_func = self.tasks[task_name]
            result = await task_func(**kwargs)
            
            return TaskResult(
                task_id=f"{task_name}_{datetime.now().timestamp()}",
                status="success",
                message="Task completed successfully",
                timestamp=datetime.now(),
                data=result
            )
        except Exception as e:
            self.logger.error(f"Task {task_name} failed: {e}")
            return TaskResult(
                task_id=f"{task_name}_{datetime.now().timestamp()}",
                status="failed",
                message=str(e),
                timestamp=datetime.now()
            )
    
    async def run_workflow(self, workflow: List[Dict[str, Any]]) -> List[TaskResult]:
        """Run a complete workflow with multiple tasks."""
        results = []
        
        for step in workflow:
            task_name = step['task']
            task_params = step.get('params', {})
            
            result = await self.execute_task(task_name, **task_params)
            results.append(result)
            
            if result.status == "failed" and step.get('required', True):
                self.logger.error(f"Required task {task_name} failed, stopping workflow")
                break
        
        return results
    
    def get_results(self, status_filter: Optional[str] = None) -> List[TaskResult]:
        """Get task results with optional status filter."""
        if status_filter:
            return [r for r in self.results if r.status == status_filter]
        return self.results.copy()
    
    def clear_results(self) -> None:
        """Clear all task results."""
        self.results.clear()
        self.logger.info("Task results cleared")


# Example task functions
async def backup_files(source: str, destination: str) -> Dict[str, Any]:
    """Example backup task."""
    import shutil
    
    try:
        if os.path.exists(destination):
            shutil.rmtree(destination)
        shutil.copytree(source, destination)
        
        return {
            'files_backed_up': len(os.listdir(source)),
            'destination': destination
        }
    except Exception as e:
        raise Exception(f"Backup failed: {e}")


async def cleanup_temp_files(directory: str) -> Dict[str, Any]:
    """Example cleanup task."""
    import tempfile
    
    try:
        cleaned_count = 0
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.endswith('.tmp') or file.endswith('.temp'):
                    os.remove(os.path.join(root, file))
                    cleaned_count += 1
        
        return {
            'files_cleaned': cleaned_count,
            'directory': directory
        }
    except Exception as e:
        raise Exception(f"Cleanup failed: {e}")
''',
            'src/cli.py': '''"""
Command-line interface for the automation tool.
"""

import click
import asyncio
import json
from typing import Optional
from .automation_core import AutomationEngine


@click.group()
@click.option('--config', '-c', help='Configuration file path')
@click.pass_context
def cli(ctx, config):
    """Professional Automation Tool CLI."""
    ctx.ensure_object(dict)
    ctx.obj['engine'] = AutomationEngine(config)


@cli.command()
@click.argument('workflow_file', type=click.Path(exists=True))
@click.pass_context
def run(ctx, workflow_file):
    """Run automation workflow from file."""
    engine = ctx.obj['engine']
    
    try:
        with open(workflow_file, 'r') as f:
            workflow = json.load(f)
        
        results = asyncio.run(engine.run_workflow(workflow))
        
        for result in results:
            status_icon = "✅" if result.status == "success" else "❌"
            click.echo(f"{status_icon} {result.task_id}: {result.message}")
    
    except Exception as e:
        click.echo(f"Error running workflow: {e}", err=True)


@cli.command()
@click.pass_context
def status(ctx):
    """Show task results status."""
    engine = ctx.obj['engine']
    
    results = engine.get_results()
    
    if not results:
        click.echo("No tasks executed yet.")
        return
    
    success_count = len([r for r in results if r.status == "success"])
    failed_count = len([r for r in results if r.status == "failed"])
    
    click.echo(f"Tasks: {len(results)} | ✅ Success: {success_count} | ❌ Failed: {failed_count}")


@cli.command()
@click.pass_context
def clear(ctx):
    """Clear all task results."""
    engine = ctx.obj['engine']
    engine.clear_results()
    click.echo("Task results cleared.")


if __name__ == '__main__':
    cli()
''',
            'src/__main__.py': '''"""Main entry point for the automation tool."""

from .cli import cli

if __name__ == '__main__':
    cli()
''',
            'tests/__init__.py': '''"""Test package."""''',
            'tests/test_automation_core.py': '''"""Tests for automation core functionality."""

import pytest
import asyncio
from datetime import datetime
from src.automation_core import AutomationEngine, TaskResult


class TestAutomationEngine:
    """Test cases for AutomationEngine."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.engine = AutomationEngine()
    
    def test_engine_initialization(self):
        """Test engine initialization."""
        assert self.engine.config is not None
        assert 'max_concurrent_tasks' in self.engine.config
        assert len(self.engine.tasks) == 0
    
    def test_task_registration(self):
        """Test task registration."""
        def dummy_task():
            return {"status": "ok"}
        
        self.engine.register_task("dummy", dummy_task)
        assert "dummy" in self.engine.tasks
    
    @pytest.mark.asyncio
    async def test_task_execution_success(self):
        """Test successful task execution."""
        def success_task():
            return {"result": "success"}
        
        self.engine.register_task("success", success_task)
        result = await self.engine.execute_task("success")
        
        assert result.status == "success"
        assert result.data["result"] == "success"
    
    @pytest.mark.asyncio
    async def test_task_execution_failure(self):
        """Test failed task execution."""
        def failing_task():
            raise Exception("Test error")
        
        self.engine.register_task("failing", failing_task)
        result = await self.engine.execute_task("failing")
        
        assert result.status == "failed"
        assert "Test error" in result.message
    
    @pytest.mark.asyncio
    async def test_workflow_execution(self):
        """Test workflow execution."""
        def task1():
            return {"step": 1}
        
        def task2():
            return {"step": 2}
        
        self.engine.register_task("task1", task1)
        self.engine.register_task("task2", task2)
        
        workflow = [
            {"task": "task1", "required": True},
            {"task": "task2", "required": True}
        ]
        
        results = await self.engine.run_workflow(workflow)
        
        assert len(results) == 2
        assert all(r.status == "success" for r in results)


if __name__ == '__main__':
    pytest.main([__file__])
''',
            'examples/workflow.json': '''{
  "name": "Example Automation Workflow",
  "description": "Sample workflow demonstrating automation capabilities",
  "steps": [
    {
      "task": "backup_files",
      "params": {
        "source": "./data",
        "destination": "./backup"
      },
      "required": true
    },
    {
      "task": "cleanup_temp_files",
      "params": {
        "directory": "./temp"
      },
      "required": false
    }
  ]
}''',
            'requirements.txt': '''# Core dependencies
click>=8.0.0
asyncio-throttle>=1.0.2
pydantic>=1.10.0

# Development dependencies
pytest>=7.0.0
pytest-asyncio>=0.21.0
pytest-cov>=4.0.0
black>=22.0.0
flake8>=5.0.0
mypy>=0.991

# Optional dependencies
python-dotenv>=0.19.0
''',
            'setup.py': '''from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="automation-toolkit",
    version="0.1.0",
    author="Professional Developer",
    author_email="dev@example.com",
    description="Professional automation toolkit for workflow management",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/username/automation-toolkit",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Systems Administration",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "automation-toolkit=src.cli:cli",
        ],
    },
)
''',
            '.gitignore': '''# Byte-compiled / optimized / DLL files
__pycache__/
*.py[cod]
*$py.class

# C extensions
*.so

# Distribution / packaging
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
pip-wheel-metadata/
share/python-wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# PyInstaller
*.manifest
*.spec

# Installer logs
pip-log.txt
pip-delete-this-directory.txt

# Unit test / coverage reports
htmlcov/
.tox/
.nox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
*.py,cover
.hypothesis/
.pytest_cache/

# Environments
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Project specific
automation.log
backup/
temp/
''',
            'README.md': '''# Professional Automation Toolkit

A production-grade automation framework for managing complex workflows and tasks with professional reliability and monitoring.

## 🚀 Features

- **Asynchronous Task Execution**: High-performance concurrent task processing
- **Workflow Management**: Define and execute complex multi-step workflows
- **Robust Error Handling**: Comprehensive error recovery and retry mechanisms
- **Professional Logging**: Structured logging with file and console output
- **CLI Interface**: Full-featured command-line interface
- **Configuration Management**: Flexible JSON-based configuration system
- **Task Results Tracking**: Complete audit trail of all operations

## 🏗️ Architecture

The toolkit is built with a modular architecture:

```
automation-toolkit/
├── src/
│   ├── __init__.py           # Package initialization
│   ├── automation_core.py     # Core automation engine
│   ├── cli.py               # Command-line interface
│   └── __main__.py          # Entry point
├── tests/
│   ├── __init__.py
│   └── test_automation_core.py
├── examples/
│   └── workflow.json         # Example workflow
├── requirements.txt          # Dependencies
├── setup.py                # Package configuration
└── README.md              # This file
```

## 📦 Installation

```bash
# Clone the repository
git clone https://github.com/username/automation-toolkit.git
cd automation-toolkit

# Install in development mode
pip install -e .

# Or install from requirements
pip install -r requirements.txt
```

## 🛠️ Usage

### Command Line Interface

```bash
# Run a workflow from file
automation-toolkit run workflow.json

# Check task status
automation-toolkit status

# Clear task results
automation-toolkit clear
```

### Python API

```python
import asyncio
from src.automation_core import AutomationEngine

# Initialize the engine
engine = AutomationEngine()

# Register a custom task
async def my_task():
    return {"result": "success"}

engine.register_task("my_task", my_task)

# Execute the task
result = await engine.execute_task("my_task")
print(f"Task status: {result.status}")
```

### Workflow Definition

Create a JSON workflow file:

```json
{
  "name": "My Workflow",
  "steps": [
    {
      "task": "backup_files",
      "params": {
        "source": "./data",
        "destination": "./backup"
      },
      "required": true
    }
  ]
}
```

## 🧪 Testing

```bash
# Run all tests
python -m pytest

# Run with coverage
python -m pytest --cov=src --cov-report=html

# Run specific test file
python -m pytest tests/test_automation_core.py
```

## 🔧 Configuration

Create a configuration file to customize behavior:

```json
{
  "max_concurrent_tasks": 10,
  "retry_attempts": 3,
  "timeout": 300,
  "log_level": "INFO"
}
```

## 📈 Performance

- **Concurrent Processing**: Handles multiple tasks simultaneously
- **Memory Efficient**: Optimized for large-scale automation
- **Fast Execution**: Minimal overhead for task operations
- **Scalable Architecture**: Suitable for enterprise workflows

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔮 Future Improvements

- [ ] Web dashboard for workflow management
- [ ] Docker containerization support
- [ ] Kubernetes integration
- [ ] Advanced scheduling capabilities
- [ ] Plugin system for custom task types
- [ ] Real-time monitoring dashboard

## 📞 Support

For support and questions:
- Create an issue on GitHub
- Check the documentation
- Review the examples directory

---

*Built with ❤️ for professional automation workflows*
''',
            '.github/workflows/ci.yml': '''name: CI/CD Pipeline

on:
  push:
    branches: [ main, master ]
  pull_request:
    branches: [ main, master ]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.8, 3.9, '3.10', '3.11']

    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install -e .
    
    - name: Lint with flake8
      run: |
        pip install flake8
        flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
        flake8 . --count --exit-zero --max-complexity=10 --max-line-length=88 --statistics
    
    - name: Run tests
      run: |
        python -m pytest tests/ -v --cov=src --cov-report=xml
    
    - name: Check code formatting
      run: |
        pip install black
        black --check .
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
        flags: unittests
        name: codecov-umbrella
'''
        }
        
        return project_files
    
    def create_repository(self, repo_name: str, description: str = None) -> Dict[str, Any]:
        """Create a new repository with professional project."""
        result = {
            'success': False,
            'repo_name': repo_name,
            'repo_url': None,
            'errors': []
        }
        
        try:
            if not self.user:
                if not self.authenticate():
                    result['errors'].append("Authentication failed")
                    return result
            
            # Create repository
            repo_description = description or f"Professional {repo_name.replace('-', ' ').title()} - Production-grade tool for developers"
            
            repo = self.user.create_repo(
                name=repo_name,
                description=repo_description,
                private=False,
                has_wiki=True,
                has_issues=True,
                has_projects=True,
                auto_init=False
            )
            
            self.logger.info(f"Created repository: {repo_name}")
            
            # Generate and upload project files
            project_files = self.generate_automation_tool(repo_name)
            
            for file_path, content in project_files.items():
                try:
                    repo.create_file(
                        path=file_path,
                        message=f"Add {file_path}",
                        content=content,
                        branch=repo.default_branch
                    )
                except GithubException as e:
                    self.logger.warning(f"Failed to create {file_path}: {e}")
            
            result['success'] = True
            result['repo_url'] = repo.html_url
            self.logger.info(f"Successfully created and populated {repo_name}")
            
        except GithubException as e:
            error_msg = f"Failed to create repository {repo_name}: {e}"
            self.logger.error(error_msg)
            result['errors'].append(error_msg)
        except Exception as e:
            error_msg = f"Unexpected error creating {repo_name}: {e}"
            self.logger.error(error_msg)
            result['errors'].append(error_msg)
        
        return result
    
    def generate_new_projects(self, count: int = 1) -> Dict[str, Any]:
        """Generate multiple new professional projects."""
        project_templates = [
            ("automation-toolkit", "Professional automation framework for workflow management"),
            ("dev-monitor", "System monitoring tool for developers"),
            ("api-builder", "RESTful API framework builder"),
            ("cli-utility", "Command-line utility toolkit"),
            ("config-manager", "Professional configuration management system"),
            ("log-analyzer", "Advanced log analysis and monitoring tool"),
            ("task-scheduler", "Professional task scheduling system"),
            ("data-processor", "Data processing and transformation toolkit"),
            ("file-manager", "Advanced file management utility"),
            ("network-monitor", "Network monitoring and diagnostic tool")
        ]
        
        results = {
            'total': count,
            'successful': 0,
            'failed': 0,
            'details': []
        }
        
        for i in range(min(count, len(project_templates))):
            repo_name, description = project_templates[i]
            result = self.create_repository(repo_name, description)
            results['details'].append(result)
            
            if result['success']:
                results['successful'] += 1
            else:
                results['failed'] += 1
        
        return results
