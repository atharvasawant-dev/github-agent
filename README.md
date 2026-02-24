# GitHub Automation Agent

A production-grade Python application for GitHub repository management and automation.

## Features

- 🔐 Secure authentication using GitHub tokens
- 📋 List all user repositories with detailed information
- 🔍 Search and get details for specific repositories
- 📊 Repository statistics (stars, forks, language, etc.)
- 🌍 Visual indicators for private/public repositories
- ⚡ Command-line interface with multiple options

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd github-agent
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up your GitHub token:
   - Create a `.env` file in the project root
   - Add your GitHub personal access token:
   ```
   GITHUB_TOKEN=your_github_token_here
   ```

## Usage

### Basic Commands

```bash
# List all repositories
python main.py

# Show only repository count
python main.py --count

# Get details for a specific repository
python main.py --repo repository-name

# Get verbose details for a specific repository
python main.py --repo repository-name --verbose
```

### Examples

```bash
# List all repositories with details
python main.py

# Get details for the "my-awesome-repo" repository
python main.py --repo my-awesome-repo

# Show total number of repositories
python main.py --count

# Get detailed information including clone URL and size
python main.py --repo my-awesome-repo --verbose
```

## Project Structure

```
github-agent/
├── main.py              # Entry point and CLI interface
├── config.py            # Configuration management
├── github_service.py    # GitHub API service class
├── requirements.txt     # Python dependencies
├── .env                 # Environment variables (not tracked)
└── README.md           # This file
```

## Configuration

The application uses environment variables for configuration:

- `GITHUB_TOKEN`: Your GitHub personal access token (required)

### Creating a GitHub Token

1. Go to GitHub Settings → Developer settings → Personal access tokens
2. Click "Generate new token"
3. Select the required scopes (at minimum: `public_repo`, `repo` for private repos)
4. Copy the token and add it to your `.env` file

## Dependencies

- **PyGithub**: GitHub API library for Python
- **python-dotenv**: Environment variable management

## Security Notes

- Never commit your `.env` file to version control
- Keep your GitHub token secure and rotate it regularly
- Use the minimum required scopes for your token

## Error Handling

The application includes comprehensive error handling for:
- Missing or invalid GitHub tokens
- Network connectivity issues
- Repository not found errors
- API rate limiting

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License.
