"""
Django REST Framework Views and API Endpoints
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from datetime import date
from core.models import UserConfig, Report, GithubRepository, Commit
from core.serializers import UserConfigSerializer, ReportSerializer, CommitSerializer, GithubRepositorySerializer
from core.services.github_service import GitHubService
from core.services.commit_aggregator import CommitAggregator
from core.services.email_service import EmailService
import logging

logger = logging.getLogger(__name__)


class UserConfigViewSet(viewsets.ModelViewSet):
    """
    API endpoints for managing user configurations
    """
    serializer_class = UserConfigSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Only return config for the current user"""
        return UserConfig.objects.filter(user=self.request.user)

    @action(detail=True, methods=['post'])
    def verify_token(self, request, pk=None):
        """Verify if GitHub token is valid"""
        user_config = self.get_object()
        if user_config.github_token is None:
            return Response({
                'token_valid': False,
                'message': 'No GitHub token found'
            })

        gh_service = GitHubService(user_config.github_token)
        is_valid = gh_service.verify_token()

        return Response({
            'token_valid': is_valid,
            'message': 'GitHub token is valid' if is_valid else 'GitHub token is invalid'
        })

    @action(detail=True, methods=['post'])
    def sync_repositories(self, request, pk=None):
        """Sync all GitHub repositories for user"""
        user_config = self.get_object()
        aggregator = CommitAggregator()

        try:
            synced_count = aggregator.sync_user_repositories(user_config)
            return Response({
                'status': 'success',
                'repositories_synced': synced_count
            })
        except Exception as e:
            logger.error(f"Error syncing repositories: {str(e)}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['post'])
    def fetch_daily_commits(self, request, pk=None):
        """Manually fetch commits for today"""
        user_config = self.get_object()
        aggregator = CommitAggregator()

        try:
            commit_count = aggregator.aggregate_daily_commits(user_config)
            return Response({
                'status': 'success',
                'commits_fetched': commit_count
            })
        except Exception as e:
            logger.error(f"Error fetching commits: {str(e)}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['post'])
    def send_test_email(self, request, pk=None):
        """Send test email to verify configuration"""
        user_config = self.get_object()

        try:
            success = EmailService.send_test_email(user_config.email)
            return Response({
                'status': 'success' if success else 'failed',
                'message': 'Test email sent' if success else 'Failed to send test email'
            })
        except Exception as e:
            logger.error(f"Error sending test email: {str(e)}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class ReportViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoints for viewing reports
    """
    serializer_class = ReportSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Only return reports for the current user"""
        return Report.objects.filter(
            user_config__user=self.request.user
        ).order_by('-report_date')

    @action(detail=False, methods=['get'])
    def today(self, request):
        """Get today's report"""
        today = date.today()
        report = self.get_queryset().filter(report_date=today).first()

        if report:
            serializer = self.get_serializer(report)
            return Response(serializer.data)
        else:
            return Response(
                {'message': 'No report for today'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=False, methods=['get'])
    def recent(self, request):
        """Get recent reports (last 7 days)"""
        reports = self.get_queryset()[:7]
        serializer = self.get_serializer(reports, many=True)
        return Response(serializer.data)


class CommitViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoints for viewing commits
    """
    serializer_class = CommitSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Only return commits for the current user"""
        return Commit.objects.filter(
            user_config__user=self.request.user
        ).order_by('-commit_date')

    @action(detail=False, methods=['get'])
    def today(self, request):
        """Get today's commits"""
        today = date.today()
        commits = self.get_queryset().filter(commit_date__date=today)
        serializer = self.get_serializer(commits, many=True)
        return Response(serializer.data)


class GithubRepositoryViewSet(viewsets.ModelViewSet):
    """
    API endpoints for managing GitHub repositories
    """
    serializer_class = GithubRepositorySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Only return repositories for the current user"""
        return GithubRepository.objects.filter(
            user_config__user=self.request.user
        )

    @action(detail=True, methods=['post'])
    def toggle_monitoring(self, request, pk=None):
        """Toggle monitoring status for a repository"""
        repo = self.get_object()
        repo.is_monitored = not repo.is_monitored
        repo.save()

        return Response({
            'repo_name': repo.repo_name,
            'is_monitored': repo.is_monitored
        })
