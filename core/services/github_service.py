"""
GitHub API Integration Service
Handles fetching commits from GitHub repositories
"""
import requests
from datetime import datetime, timedelta
from typing import List, Dict
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class GitHubService:
    """Service to interact with GitHub API"""

    def __init__(self, github_token: str):
        self.github_token = github_token
        self.base_url = settings.GITHUB_API_BASE
        self.headers = {
            'Authorization': f'token {github_token}',
            'Accept': 'application/vnd.github.v3+json'
        }

    def get_daily_commits(self, repo: str, since: datetime = None) -> List[Dict]:
        """
        Fetch commits from a repository for today (or specified date)
        
        Args:
            repo: Repository in format 'owner/repo'
            since: Datetime to fetch commits from (default: today at 00:00)
            
        Returns:
            List of commit dictionaries with relevant metadata
        """
        if since is None:
            since = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        
        until = since + timedelta(days=1)
        
        url = f"{self.base_url}/repos/{repo}/commits"
        params = {
            'since': since.isoformat(),
            'until': until.isoformat(),
            'per_page': 100,
        }
        
        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            response.raise_for_status()
            commits = response.json()
            
            # Filter and normalize commits
            normalized_commits = []
            for commit in commits:
                normalized = self._normalize_commit(commit, repo)
                if normalized:  # Only include non-noise commits
                    normalized_commits.append(normalized)
            
            logger.info(f"Fetched {len(normalized_commits)} commits from {repo}")
            return normalized_commits
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching commits from {repo}: {str(e)}")
            return []

    def _normalize_commit(self, github_commit: Dict, repo: str) -> Dict | None:
        """
        Normalize GitHub commit data and filter noise
        
        Args:
            github_commit: Raw commit from GitHub API
            repo: Repository name
            
        Returns:
            Normalized commit dict or None if it's a noise commit
        """
        try:
            message = github_commit['commit']['message']
            
            # Filter noise commits
            if self._is_noise_commit(message):
                return None
            
            return {
                'sha': github_commit['sha'],
                'author': github_commit['commit']['author']['name'],
                'email': github_commit['commit']['author']['email'],
                'message': message.split('\n')[0],  # First line only
                'full_message': message,
                'date': github_commit['commit']['author']['date'],
                'url': github_commit['html_url'],
                'repository': repo,
                'files_changed': len(github_commit.get('files', [])),
                'additions': sum(f.get('additions', 0) for f in github_commit.get('files', [])),
                'deletions': sum(f.get('deletions', 0) for f in github_commit.get('files', [])),
            }
        except (KeyError, IndexError) as e:
            logger.warning(f"Error normalizing commit: {str(e)}")
            return None

    def _is_noise_commit(self, message: str) -> bool:
        """
        Check if a commit message is noise (should be filtered)
        
        Args:
            message: Commit message
            
        Returns:
            True if commit is noise, False otherwise
        """
        message_lower = message.lower()
        noise_patterns = settings.GITHUB_COMMIT_FILTER_WORDS
        
        return any(pattern.lower() in message_lower for pattern in noise_patterns)

    def get_user_repos(self, username: str) -> List[str]:
        """
        Get all repositories for a GitHub user
        
        Args:
            username: GitHub username
            
        Returns:
            List of repository names (owner/repo format)
        """
        url = f"{self.base_url}/users/{username}/repos"
        params = {'per_page': 100, 'type': 'owner,collaborator'}
        
        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            response.raise_for_status()
            repos = response.json()
            
            return [f"{repo['owner']['login']}/{repo['name']}" for repo in repos]
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching repos for {username}: {str(e)}")
            return []

    def verify_token(self) -> bool:
        """
        Verify if GitHub token is valid
        
        Returns:
            True if token is valid, False otherwise
        """
        url = f"{self.base_url}/user"
        
        try:
            response = requests.get(url, headers=self.headers, timeout=5)
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False
