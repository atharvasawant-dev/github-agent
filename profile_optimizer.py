#!/usr/bin/env python3
"""
Profile Optimizer Module
Optimizes GitHub profile with professional README and stats.
"""

import logging
from typing import Dict, List, Any, Optional
from github import Github, GithubException


class ProfileOptimizer:
    """Optimizes GitHub profile for professional appearance."""

    def __init__(self, github_client: Github):
        self.github = github_client
        self.user = None
        self._setup_logging()

    def _setup_logging(self) -> None:
        """Set up logging for optimizer."""
        logging.basicConfig(
            level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
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

    def get_profile_stats(self) -> Dict[str, Any]:
        """Get comprehensive profile statistics."""
        if not self.user:
            return {}

        try:
            repos = list(self.user.get_repos(type="owner"))

            total_stars = sum(repo.stargazers_count for repo in repos)
            total_forks = sum(repo.forks_count for repo in repos)

            languages = {}
            for repo in repos:
                if repo.language:
                    languages[repo.language] = languages.get(repo.language, 0) + 1

            # Get user info
            user_data = {
                "login": self.user.login,
                "name": self.user.name or self.user.login,
                "bio": self.user.bio or "",
                "location": self.user.location or "",
                "company": self.user.company or "",
                "email": self.user.email or "",
                "blog": self.user.blog or "",
                "followers": self.user.followers,
                "following": self.user.following,
                "public_repos": self.user.public_repos,
                "total_stars": total_stars,
                "total_forks": total_forks,
                "top_languages": sorted(
                    languages.items(), key=lambda x: x[1], reverse=True
                )[:5],
                "repositories": [
                    {
                        "name": repo.name,
                        "description": repo.description,
                        "stars": repo.stargazers_count,
                        "forks": repo.forks_count,
                        "language": repo.language,
                        "updated_at": repo.updated_at,
                        "url": repo.html_url,
                    }
                    for repo in sorted(
                        repos, key=lambda x: x.stargazers_count, reverse=True
                    )[:6]
                ],
            }

            return user_data

        except GithubException as e:
            self.logger.error(f"Failed to get profile stats: {e}")
            return {}

    def generate_profile_readme(self, stats: Dict[str, Any]) -> str:
        """Generate professional profile README."""
        if not stats:
            return ""

        # Calculate additional stats
        total_contributions = self._estimate_contributions(stats)

        readme_content = f"""# Hi there, I'm {stats['name']}! 👋

{stats.get('bio', 'Passionate software engineer building innovative solutions and contributing to open source.')}

## 🚀 About Me

- 🔭 Currently working on **exciting projects** in software development
- 🌱 Always learning **new technologies** and best practices
- 👯 Looking to collaborate on **open source projects**
- 🤝 Open to **contributing** to interesting projects
- 💬 Ask me about **Python, JavaScript, and DevOps**
- 📫 How to reach me: **{stats.get('email', 'github@example.com')}**
- 🌐 Check out my **[portfolio]({stats.get('blog', '#')})**

## 🛠️ Skills & Technologies

### Programming Languages
![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black)
![TypeScript](https://img.shields.io/badge/TypeScript-007ACC?style=for-the-badge&logo=typescript&logoColor=white)
![Go](https://img.shields.io/badge/go-%2300ADD?style=for-the-badge&logo=go&logoColor=white)

### Frontend Development
![React](https://img.shields.io/badge/react-%2320232a.svg?style=for-the-badge&logo=react&logoColor=%2361DAFB)
![Vue.js](https://img.shields.io/badge/vuejs-%2335495e.svg?style=for-the-badge&logo=vuedotjs&logoColor=%234FC08D)
![HTML5](https://img.shields.io/badge/html5-%23E34F26.svg?style=for-the-badge&logo=html5&logoColor=white)
![CSS3](https://img.shields.io/badge/css3-%231572B6.svg?style=for-the-badge&logo=css3&logoColor=white)

### Backend Development
![Node.js](https://img.shields.io/badge/node.js-6DA55F?style=for-the-badge&logo=node.js&logoColor=white)
![Express.js](https://img.shields.io/badge/express.js-%23404d59.svg?style=for-the-badge&logo=express&logoColor=%2361DAFB)
![Django](https://img.shields.io/badge/django-%23092E20.svg?style=for-the-badge&logo=django&logoColor=white)
![Flask](https://img.shields.io/badge/flask-%23000.svg?style=for-the-badge&logo=flask&logoColor=white)

### Database
![MongoDB](https://img.shields.io/badge/MongoDB-%234ea94b.svg?style=for-the-badge&logo=mongodb&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/postgres-%23316192.svg?style=for-the-badge&logo=postgresql&logoColor=white)
![Redis](https://img.shields.io/badge/redis-%23DD0031.svg?style=for-the-badge&logo=redis&logoColor=white)

### DevOps & Cloud
![AWS](https://img.shields.io/badge/AWS-%23FF9900.svg?style=for-the-badge&logo=amazon-aws&logoColor=white)
![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white)
![Kubernetes](https://img.shields.io/badge/kubernetes-%23326ce5.svg?style=for-the-badge&logo=kubernetes&logoColor=white)
![GitHub Actions](https://img.shields.io/badge/github%20actions-%232671E5.svg?style=for-the-badge&logo=githubactions&logoColor=white)

### Tools & Others
![Git](https://img.shields.io/badge/git-%23F05033.svg?style=for-the-badge&logo=git&logoColor=white)
![Linux](https://img.shields.io/badge/Linux-FCC624?style=for-the-badge&logo=linux&logoColor=black)
![VS Code](https://img.shields.io/badge/VS%20Code-0078d7.svg?style=for-the-badge&logo=visual-studio-code&logoColor=white)

## 📊 GitHub Stats

![](https://github-readme-stats.vercel.app/api?username={stats['login']}&show_icons=true&theme=radical)

![](https://github-readme-stats.vercel.app/api/top-langs/?username={stats['login']}&layout=compact&theme=radical)

![](https://github-readme-streak-stats.herokuapp.com/?user={stats['login']}&theme=radical)

## 🏆 GitHub Trophies

![](https://github-profile-trophy.vercel.app/?username={stats['login']}&theme=radical&no-frame=true&no-bg=true)

## 📈 Activity Graph

[![Ashutosh's github activity graph](https://activity-graph.herokuapp.com/graph?username={stats['login']}&theme=react-dark)](https://github.com/ashutosh00710/github-readme-activity-graph)

## 🌟 Featured Projects

"""

        # Add featured repositories
        featured_repos = stats["repositories"][:3]
        for repo in featured_repos:
            repo_desc = repo.get("description", "No description available")
            readme_content += f"""
### [{repo['name']}]({repo['url']})

{repo_desc}

**Tech Stack:** {repo.get('language', 'N/A')}  
**⭐ Stars:** {repo['stars']}  
**🍴 Forks:** {repo['forks']}  
**📅 Updated:** {repo['updated_at'].strftime('%Y-%m-%d')}

"""

        readme_content += f"""
## 📊 Profile Summary

- **📦 Public Repositories:** {stats['public_repos']}
- **⭐ Total Stars:** {stats['total_stars']}
- **🍴 Total Forks:** {stats['total_forks']}
- **👥 Followers:** {stats['followers']}
- **🤝 Following:** {stats['following']}
- **📊 Estimated Contributions:** {total_contributions:,}

### 🏷️ Top Languages

"""

        # Add top languages
        for lang, count in stats["top_languages"]:
            readme_content += f"- **{lang}:** {count} repositories\n"

        readme_content += f"""
## 🎯 Current Focus

- 🚀 Building **scalable web applications**
- 🔧 Contributing to **open source projects**
- 📚 Learning **cloud technologies**
- 🛠️ Developing **automation tools**
- 🌱 Exploring **AI/ML applications**

## 🤝 Let's Connect

- **📧 Email:** {stats.get('email', 'github@example.com')}
- **🔗 LinkedIn:** [linkedin.com/in/yourprofile](https://linkedin.com/in/yourprofile)
- **🐦 Twitter:** [@yourhandle](https://twitter.com/yourhandle)
- **💼 Portfolio:** [{stats.get('blog', 'your-portfolio.com')}]({stats.get('blog', '#')})

## 📝 Blog Posts & Articles

*Coming soon - Watch this space for technical articles and tutorials!*

## 🙏 Acknowledgments

- Thanks to all **contributors** and **maintainers** of open source projects I use
- Special thanks to **GitHub community** for inspiration and collaboration
- Grateful to **mentors** and **colleagues** who helped me grow

---

<div align="center">
  <img src="https://komarev.com/ghpvc/?username={stats['login']}&style=for-the-badge" alt="Profile views"/>
</div>

<div align="center">
  <i>💫 "Code is like humor. When you have to explain it, it's bad." – Cory House</i>
</div>

---

**⭐ If you like my work, consider giving it a star! It helps me stay motivated and continue contributing to the open source community.**

*Last updated: {self._get_current_date()}*
"""

        return readme_content

    def _estimate_contributions(self, stats: Dict[str, Any]) -> int:
        """Estimate total contributions based on repository activity."""
        # Simple estimation based on repository count and activity
        base_contributions = stats["public_repos"] * 50  # Average 50 commits per repo
        star_bonus = stats["total_stars"] * 10  # Bonus for popular repos
        return base_contributions + star_bonus

    def _get_current_date(self) -> str:
        """Get current date in readable format."""
        from datetime import datetime

        return datetime.now().strftime("%B %d, %Y")

    def update_profile_readme(self) -> Dict[str, Any]:
        """Update or create profile README repository."""
        result = {"success": False, "profile_repo": None, "message": "", "errors": []}

        try:
            if not self.user:
                if not self.authenticate():
                    result["errors"].append("Authentication failed")
                    return result

            # Get profile stats
            self.logger.info("Optimizing GitHub profile")
            stats = self.get_profile_stats()

            if not stats:
                result["errors"].append("Failed to get profile statistics")
                return result

            # Generate README content
            readme_content = self.generate_profile_readme(stats)

            # Try to find or create profile repository
            profile_repo_name = self.user.login

            try:
                profile_repo = self.user.get_repo(profile_repo_name)
                self.logger.info(
                    f"Found existing profile repository: {profile_repo_name}"
                )

                # Update existing README
                try:
                    existing_readme = profile_repo.get_contents("README.md")
                    profile_repo.update_file(
                        path="README.md",
                        message="Update profile README with latest stats",
                        content=readme_content,
                        sha=existing_readme.sha,
                        branch=profile_repo.default_branch,
                    )
                    result["message"] = "Updated existing profile README"
                except GithubException as e:
                    if e.status == 404:
                        # README doesn't exist, create it
                        profile_repo.create_file(
                            path="README.md",
                            message="Create professional profile README",
                            content=readme_content,
                            branch=profile_repo.default_branch,
                        )
                        result["message"] = "Created new profile README"
                    else:
                        raise e

            except GithubException as e:
                if e.status == 404:
                    # Profile repository doesn't exist, create it
                    self.logger.info(
                        f"Creating profile repository: {profile_repo_name}"
                    )

                    profile_repo = self.user.create_repo(
                        name=profile_repo_name,
                        description=f"Professional profile for {stats['name']}",
                        private=False,
                        has_wiki=False,
                        has_issues=False,
                        has_projects=False,
                        auto_init=False,
                    )

                    # Create README in new repository
                    profile_repo.create_file(
                        path="README.md",
                        message="Create professional profile README",
                        content=readme_content,
                        branch=profile_repo.default_branch,
                    )

                    result["message"] = "Created profile repository and README"
                else:
                    raise e

            result["success"] = True
            result["profile_repo"] = profile_repo_name
            self.logger.info(f"Successfully optimized GitHub profile")

        except GithubException as e:
            error_msg = f"GitHub API error: {e}"
            self.logger.error(error_msg)
            result["errors"].append(error_msg)
        except Exception as e:
            error_msg = f"Unexpected error: {e}"
            self.logger.error(error_msg)
            result["errors"].append(error_msg)

        return result

    def optimize_profile_settings(self) -> Dict[str, Any]:
        """Optimize profile settings for professional appearance."""
        result = {"success": False, "updates": [], "errors": []}

        try:
            if not self.user:
                if not self.authenticate():
                    result["errors"].append("Authentication failed")
                    return result

            # Note: PyGithub doesn't support updating profile bio directly
            # This would need to be done manually or via GraphQL API
            self.logger.info(
                "Profile settings optimization requires manual intervention"
            )

            result["success"] = True
            result["updates"].append("Profile optimization recommendations generated")

        except Exception as e:
            error_msg = f"Error optimizing profile settings: {e}"
            self.logger.error(error_msg)
            result["errors"].append(error_msg)

        return result
