#!/usr/bin/env python3
"""
Repository Improver Module
Generates professional README templates for repositories lacking documentation.
"""

from typing import List, Dict, Any
from datetime import datetime


class RepositoryImprover:
    """Generates improvement suggestions and content for repositories."""

    def __init__(self):
        self.readme_templates = {
            "default": self._generate_default_template,
            "web_project": self._generate_web_template,
            "api_project": self._generate_api_template,
            "data_science": self._generate_data_science_template,
            "mobile_app": self._generate_mobile_template,
            "cli_tool": self._generate_cli_template,
        }

    def analyze_repositories_needing_readme(
        self, repositories: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Identify repositories that need README files and generate templates.

        Args:
            repositories: List of repository dictionaries from analysis

        Returns:
            List of dictionaries with repo names and generated README content
        """
        improvements = []

        for repo in repositories:
            if not repo.get("has_readme", False):
                readme_content = self._generate_readme_for_repository(repo)
                improvements.append(
                    {"repo_name": repo["name"], "readme_content": readme_content}
                )

        return improvements

    def _detect_project_type(self, repo: Dict[str, Any]) -> str:
        """Detect project type based on repository metadata."""
        name = repo.get("name", "").lower()
        language = (repo.get("language") or "").lower()
        description = (repo.get("description") or "").lower()

        # Web project indicators
        if any(
            indicator in name or indicator in description
            for indicator in [
                "web",
                "site",
                "frontend",
                "backend",
                "dashboard",
                "portal",
            ]
        ):
            return "web_project"

        # API project indicators
        if any(
            indicator in name or indicator in description
            for indicator in ["api", "rest", "graphql", "service", "server"]
        ):
            return "api_project"

        # Data science indicators
        if any(
            indicator in name or indicator in description
            for indicator in ["ml", "ai", "data", "analysis", "model", "predict"]
        ) or language in ["python", "r", "jupyter"]:
            return "data_science"

        # Mobile app indicators
        if any(
            indicator in name or indicator in description
            for indicator in [
                "app",
                "mobile",
                "ios",
                "android",
                "flutter",
                "react-native",
            ]
        ):
            return "mobile_app"

        # CLI tool indicators
        if any(
            indicator in name or indicator in description
            for indicator in ["cli", "tool", "command", "utility", "script"]
        ):
            return "cli_tool"

        return "default"

    def _generate_readme_for_repository(self, repo: Dict[str, Any]) -> str:
        """Generate appropriate README template based on repository type."""
        project_type = self._detect_project_type(repo)
        template_func = self.readme_templates.get(
            project_type, self._generate_default_template
        )
        return template_func(repo)

    def _generate_default_template(self, repo: Dict[str, Any]) -> str:
        """Generate a default README template."""
        name = repo.get("name", "Project Name")
        description = repo.get("description", "A brief description of this project.")
        language = repo.get("language", "Unknown")

        template = f"""# {name}

{description}

## Overview

This project is built with {language} and provides [brief description of functionality].

## Features

- ✨ Feature 1
- ✨ Feature 2
- ✨ Feature 3

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/{name}.git
cd {name}

# Install dependencies
[Installation instructions]
```

## Usage

```bash
# Run the project
[Usage instructions]
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contact

[Your Name] - [@yourhandle](https://twitter.com/yourhandle)

Project Link: [https://github.com/yourusername/{name}](https://github.com/yourusername/{name})

---

*This README was generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
        return template

    def _generate_web_template(self, repo: Dict[str, Any]) -> str:
        """Generate README template for web projects."""
        name = repo.get("name", "Web Project")
        description = repo.get("description", "A modern web application.")

        template = f"""# {name}

{description}

## 🌐 Live Demo

[Link to live demo] (if available)

## 📸 Screenshots

[Add screenshots of your web application]

## 🚀 Features

- 🎨 Modern UI/UX design
- 📱 Responsive layout
- ⚡ Fast performance
- 🔒 Secure authentication (if applicable)
- 🌍 Multi-language support (if applicable)

## 🛠️ Technologies Used

- **Frontend:** [React, Vue, Angular, etc.]
- **Backend:** [Node.js, Django, Flask, etc.]
- **Database:** [PostgreSQL, MongoDB, etc.]
- **Deployment:** [Vercel, Netlify, AWS, etc.]

## 📦 Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/{name}.git
cd {name}

# Install dependencies
npm install
# or
yarn install

# Set up environment variables
cp .env.example .env
# Edit .env with your configuration

# Run the development server
npm run dev
# or
yarn dev
```

## 🎯 Usage

1. Open your browser and navigate to `http://localhost:3000`
2. [Specific usage instructions]

## 🤝 Contributing

Contributions are what make the open source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

*Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
        return template

    def _generate_api_template(self, repo: Dict[str, Any]) -> str:
        """Generate README template for API projects."""
        name = repo.get("name", "API Project")
        description = repo.get("description", "A RESTful API service.")

        template = f"""# {name}

{description}

## 📡 API Documentation

### Base URL
```
[API Base URL]
```

### Authentication
```bash
# Include API key in headers
curl -H "Authorization: Bearer YOUR_API_KEY" \\
     -H "Content-Type: application/json" \\
     [endpoint]
```

## 🛠️ Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/{name}.git
cd {name}

# Install dependencies
pip install -r requirements.txt
# or
npm install

# Set up environment variables
cp .env.example .env
# Edit .env with your configuration

# Run the API server
python app.py
# or
npm start
```

## 📚 API Endpoints

### GET /api/resource
Get all resources

**Response:**
```json
{{
  "data": [],
  "status": "success"
}}
```

### POST /api/resource
Create a new resource

**Request Body:**
```json
{{
  "name": "Example",
  "value": "Data"
}}
```

## 🧪 Testing

```bash
# Run tests
python -m pytest
# or
npm test
```

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

*Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
        return template

    def _generate_data_science_template(self, repo: Dict[str, Any]) -> str:
        """Generate README template for data science projects."""
        name = repo.get("name", "Data Science Project")
        description = repo.get(
            "description", "A data science and machine learning project."
        )

        template = f"""# {name}

{description}

## 📊 Project Overview

This project focuses on [describe the data science problem and approach].

## 🗂️ Project Structure

```
{name}/
├── data/                 # Raw and processed data
├── notebooks/           # Jupyter notebooks
├── src/                 # Source code
├── models/              # Trained models
├── tests/               # Unit tests
├── requirements.txt      # Python dependencies
└── README.md           # This file
```

## 🔬 Methodology

1. **Data Collection**: [Describe data sources]
2. **Data Preprocessing**: [Describe preprocessing steps]
3. **Feature Engineering**: [Describe feature creation]
4. **Model Selection**: [Describe models tried]
5. **Training & Evaluation**: [Describe training process]
6. **Results**: [Describe key findings]

## 🛠️ Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/{name}.git
cd {name}

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\\Scripts\\activate

# Install dependencies
pip install -r requirements.txt
```

## 📈 Usage

```bash
# Run data analysis
python src/analysis.py

# Train model
python src/train.py

# Make predictions
python src/predict.py
```

## 📊 Results

[Include key metrics, charts, and findings]

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

*Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
        return template

    def _generate_mobile_template(self, repo: Dict[str, Any]) -> str:
        """Generate README template for mobile app projects."""
        name = repo.get("name", "Mobile App")
        description = repo.get("description", "A mobile application.")

        template = f"""# {name}

{description}

## 📱 App Screenshots

[Add screenshots of your mobile app]

## 🚀 Features

- 🎨 Beautiful UI/UX
- 📱 Cross-platform support
- 🔔 Push notifications
- 🌐 Offline mode
- 🔐 Secure authentication

## 🛠️ Tech Stack

- **Framework**: [React Native, Flutter, Swift, Kotlin]
- **State Management**: [Redux, MobX, Provider, etc.]
- **Backend**: [Node.js, Firebase, etc.]
- **Database**: [Firebase, SQLite, etc.]

## 📦 Installation

### Prerequisites
- [List prerequisites like Node.js, React Native CLI, etc.]

### Setup
```bash
# Clone the repository
git clone https://github.com/yourusername/{name}.git
cd {name}

# Install dependencies
npm install
# or
yarn install

# For iOS
cd ios && pod install && cd ..

# Run the app
npm run android  # For Android
npm run ios      # For iOS
```

## 🎯 Usage

1. Install the app on your device/emulator
2. [Specific usage instructions]

## 🧪 Testing

```bash
# Run tests
npm test
```

## 📱 Build & Release

```bash
# Build for production
npm run build:android
npm run build:ios
```

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

*Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
        return template

    def _generate_cli_template(self, repo: Dict[str, Any]) -> str:
        """Generate README template for CLI tools."""
        name = repo.get("name", "CLI Tool")
        description = repo.get("description", "A command-line tool.")

        template = f"""# {name}

{description}

## 🚀 Installation

### Using pip
```bash
pip install {name}
```

### From source
```bash
# Clone the repository
git clone https://github.com/yourusername/{name}.git
cd {name}

# Install in development mode
pip install -e .
```

## 📖 Usage

### Basic Commands
```bash
# Show help
{name} --help

# Main functionality
{name} [command] [options]
```

### Examples
```bash
# Example 1
{name} command --option value

# Example 2
{name} --input file.txt --output result.txt
```

## ⚙️ Configuration

Create a configuration file at `~/.{name}/config.yaml`:

```yaml
setting1: value1
setting2: value2
```

## 🛠️ Development

```bash
# Clone the repository
git clone https://github.com/yourusername/{name}.git
cd {name}

# Set up development environment
python -m venv venv
source venv/bin/activate

# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest
```

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

*Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
        return template

    def print_improvement_summary(self, improvements: List[Dict[str, Any]]) -> None:
        """Print a summary of repositories that need README files."""
        if not improvements:
            print("✅ All repositories have README files!")
            return

        print(f"\n📝 README Improvements Needed")
        print("=" * 50)
        print(f"Found {len(improvements)} repositories without README files:\n")

        for i, improvement in enumerate(improvements, 1):
            print(f"{i}. {improvement['repo_name']}")
            print(f"   README template generated ✓")
            print()

        print(
            f"💡 Tip: Use the generated README templates to improve your repository documentation!"
        )

    def export_readme_files(
        self, improvements: List[Dict[str, Any]], output_dir: str = "readme_templates"
    ) -> None:
        """Export generated README files to a directory."""
        import os

        if not improvements:
            print("No README files to export.")
            return

        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)

        for improvement in improvements:
            filename = f"{improvement['repo_name']}_README.md"
            filepath = os.path.join(output_dir, filename)

            with open(filepath, "w", encoding="utf-8") as f:
                f.write(improvement["readme_content"])

        print(f"📁 README templates exported to '{output_dir}' directory")


if __name__ == "__main__":
    # Example usage
    example_repos = [
        {
            "name": "my-web-app",
            "description": "A modern web application",
            "language": "JavaScript",
            "has_readme": False,
        },
        {
            "name": "data-analysis",
            "description": "Machine learning project",
            "language": "Python",
            "has_readme": False,
        },
    ]

    improver = RepositoryImprover()
    improvements = improver.analyze_repositories_needing_readme(example_repos)
    improver.print_improvement_summary(improvements)
