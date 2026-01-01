"""
Commit Aggregation Service
Handles fetching and storing commits from GitHub
"""
from datetime import datetime, date
from django.utils import timezone
from core.models import UserConfig, GithubRepository, Commit
from core.services.github_service import GitHubService
import logging

logger = logging.getLogger(__name__)


class CommitAggregator:
    """Service to aggregate and store commits"""

    def aggregate_daily_commits(self, user_config: UserConfig, target_date: date = None) -> int:
        """
        Fetch and store daily commits for a user
        
        Args:
            user_config: User configuration
            target_date: Date to fetch commits for (default: today)
            
        Returns:
            Number of commits fetched and stored
        """
        if target_date is None:
            target_date = date.today()

        # Validate GitHub token
        gh_service = GitHubService(user_config.github_token)
        if not gh_service.verify_token():
            logger.error(f"Invalid GitHub token for {user_config.user.username}")
            return 0

        total_commits = 0

        # Fetch commits from each monitored repository
        for repo in user_config.repositories.filter(is_monitored=True):
            commits = gh_service.get_daily_commits(repo.repo_name, since=timezone.make_aware(
                timezone.datetime.combine(target_date, timezone.datetime.min.time())
            ))

            # Store commits in database
            stored = self._store_commits(user_config, repo, commits)
            total_commits += stored
            logger.info(f"Stored {stored} commits from {repo.repo_name}")

        return total_commits

    def _store_commits(self, user_config: UserConfig, repository: GithubRepository, commits: list) -> int:
        """
        Store fetched commits in the database
        
        Args:
            user_config: User configuration
            repository: Repository model instance
            commits: List of normalized commits
            
        Returns:
            Number of commits stored
        """
        stored_count = 0

        for commit_data in commits:
            try:
                # Check if commit already exists
                if Commit.objects.filter(commit_sha=commit_data['sha']).exists():
                    continue

                # Parse commit date
                commit_date = datetime.fromisoformat(commit_data['date'].replace('Z', '+00:00'))

                # Create commit record
                commit = Commit.objects.create(
                    user_config=user_config,
                    repository=repository,
                    commit_sha=commit_data['sha'],
                    author=commit_data['author'],
                    message=commit_data['message'],
                    files_changed=commit_data['files_changed'],
                    additions=commit_data['additions'],
                    deletions=commit_data['deletions'],
                    commit_date=commit_date,
                )

                stored_count += 1
                logger.debug(f"Stored commit {commit.commit_sha[:8]}")

            except Exception as e:
                logger.error(f"Error storing commit: {str(e)}")
                continue

        return stored_count

    def sync_user_repositories(self, user_config: UserConfig) -> int:
        """
        Sync all repositories for a user from GitHub
        
        Args:
            user_config: User configuration
            
        Returns:
            Number of repositories synced
        """
        gh_service = GitHubService(user_config.github_token)
        repos = gh_service.get_user_repos(user_config.github_username)

        synced = 0
        for repo_name in repos:
            try:
                owner, name = repo_name.split('/')
                repo_url = f"https://github.com/{repo_name}"

                repo, created = GithubRepository.objects.get_or_create(
                    user_config=user_config,
                    repo_name=repo_name,
                    defaults={'repo_url': repo_url, 'is_monitored': True}
                )

                if created:
                    synced += 1
                    logger.info(f"Added repository {repo_name}")

            except Exception as e:
                logger.error(f"Error syncing repo {repo_name}: {str(e)}")
                continue

        return synced
