from django.contrib import admin
from core.models import UserConfig, GithubRepository, Commit, Report, DeliveryLog


@admin.register(UserConfig)
class UserConfigAdmin(admin.ModelAdmin):
    list_display = ['user', 'github_username', 'email', 'report_time', 'is_active', 'created_at']
    list_filter = ['is_active', 'timezone', 'created_at']
    search_fields = ['user__username', 'github_username', 'email']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(GithubRepository)
class GithubRepositoryAdmin(admin.ModelAdmin):
    list_display = ['repo_name', 'user_config', 'is_monitored', 'created_at']
    list_filter = ['is_monitored', 'created_at']
    search_fields = ['repo_name', 'user_config__user__username']
    readonly_fields = ['created_at']


@admin.register(Commit)
class CommitAdmin(admin.ModelAdmin):
    list_display = ['author', 'repository', 'message', 'commit_date', 'files_changed', 'is_processed']
    list_filter = ['is_processed', 'commit_date', 'repository']
    search_fields = ['author', 'message', 'commit_sha']
    readonly_fields = ['commit_sha', 'fetched_at']
    ordering = ['-commit_date']


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ['user_config', 'report_date', 'status', 'commit_count', 'sent_at']
    list_filter = ['status', 'report_date', 'created_at']
    search_fields = ['user_config__user__username', 'report_date']
    readonly_fields = ['created_at', 'content_html', 'content_text']
    ordering = ['-report_date']


@admin.register(DeliveryLog)
class DeliveryLogAdmin(admin.ModelAdmin):
    list_display = ['report', 'channel', 'recipient', 'status', 'sent_at']
    list_filter = ['status', 'channel', 'sent_at']
    search_fields = ['recipient', 'report__user_config__user__username']
    readonly_fields = ['sent_at']
    ordering = ['-sent_at']
