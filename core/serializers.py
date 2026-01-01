"""
Django REST Framework Serializers
"""
from rest_framework import serializers
from core.models import UserConfig, GithubRepository, Report, Commit


class GithubRepositorySerializer(serializers.ModelSerializer):
    class Meta:
        model = GithubRepository
        fields = ['id', 'repo_name', 'repo_url', 'is_monitored', 'created_at']
        read_only_fields = ['id', 'created_at']


class UserConfigSerializer(serializers.ModelSerializer):
    repositories = GithubRepositorySerializer(many=True, read_only=True)

    class Meta:
        model = UserConfig
        fields = [
            'id', 'github_token', 'github_username', 'email',
            'report_time', 'timezone', 'is_active', 'repositories'
        ]
        extra_kwargs = {
            'github_token': {'write_only': True},
        }


class ReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        fields = ['id', 'report_date', 'status', 'content_html', 'content_text', 'commit_count', 'repo_count', 'sent_at']
        read_only_fields = ['id', 'content_html', 'content_text', 'commit_count', 'repo_count', 'sent_at']


class CommitSerializer(serializers.ModelSerializer):
    repository_name = serializers.CharField(source='repository.repo_name', read_only=True)

    class Meta:
        model = Commit
        fields = ['id', 'repository_name', 'author', 'message', 'commit_date', 'files_changed', 'additions', 'deletions']
        read_only_fields = ['id', 'author', 'message', 'commit_date', 'files_changed', 'additions', 'deletions']
