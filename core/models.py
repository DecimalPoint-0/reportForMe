from django.db import models
from django.contrib.auth.models import User
from datetime import datetime, timedelta
from allauth.socialaccount.models import SocialAccount


class UserConfig(models.Model):
    """Store developer's configuration for daily reports"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='report_config')
    github_username = models.CharField(max_length=255, help_text="GitHub username")
    email = models.EmailField(help_text="Email to receive daily reports")
    report_time = models.TimeField(default="18:00", help_text="Time to send daily report (HH:MM)")
    timezone = models.CharField(max_length=50, default="UTC", help_text="User's timezone")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'user_config'

    def __str__(self):
        return f"{self.user.username} - {self.github_username}"

    @property
    def github_token(self):
        """Get GitHub access token from social account"""
        try:
            social_account = SocialAccount.objects.get(
                user=self.user,
                provider='github'
            )
            return social_account.socialaccount_ptr.extra_data.get('access_token')
        except SocialAccount.DoesNotExist:
            return None


class GithubRepository(models.Model):
    """Track monitored GitHub repositories"""
    user_config = models.ForeignKey(UserConfig, on_delete=models.CASCADE, related_name='repositories')
    repo_name = models.CharField(max_length=255, help_text="Repo name (e.g., owner/repo)")
    repo_url = models.URLField()
    is_monitored = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'github_repository'
        unique_together = ('user_config', 'repo_name')

    def __str__(self):
        return f"{self.user_config.user.username} - {self.repo_name}"


class Commit(models.Model):
    """Store fetched GitHub commits"""
    user_config = models.ForeignKey(UserConfig, on_delete=models.CASCADE, related_name='commits')
    repository = models.ForeignKey(GithubRepository, on_delete=models.CASCADE, related_name='commits')
    commit_sha = models.CharField(max_length=255, unique=True)
    author = models.CharField(max_length=255)
    message = models.TextField()
    files_changed = models.IntegerField(default=0)
    additions = models.IntegerField(default=0)
    deletions = models.IntegerField(default=0)
    commit_date = models.DateTimeField()
    fetched_at = models.DateTimeField(auto_now_add=True)
    is_processed = models.BooleanField(default=False)

    class Meta:
        db_table = 'commit'
        indexes = [
            models.Index(fields=['user_config', 'commit_date']),
            models.Index(fields=['is_processed', 'commit_date']),
        ]

    def __str__(self):
        return f"{self.author} - {self.message[:50]}"


class Report(models.Model):
    """Store generated daily reports"""
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('scheduled', 'Scheduled'),
        ('sent', 'Sent'),
        ('failed', 'Failed'),
    ]

    user_config = models.ForeignKey(UserConfig, on_delete=models.CASCADE, related_name='reports')
    report_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    content_html = models.TextField(help_text="Formatted HTML report")
    content_text = models.TextField(help_text="Plain text version of report")
    commit_count = models.IntegerField(default=0)
    repo_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    sent_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'report'
        unique_together = ('user_config', 'report_date')
        ordering = ['-report_date']

    def __str__(self):
        return f"{self.user_config.user.username} - {self.report_date} ({self.status})"


class DeliveryLog(models.Model):
    """Track report delivery attempts"""
    CHANNEL_CHOICES = [
        ('email', 'Email'),
        ('whatsapp', 'WhatsApp'),
    ]

    report = models.ForeignKey(Report, on_delete=models.CASCADE, related_name='delivery_logs')
    channel = models.CharField(max_length=20, choices=CHANNEL_CHOICES)
    recipient = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=[('success', 'Success'), ('failed', 'Failed')])
    error_message = models.TextField(blank=True, null=True)
    sent_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'delivery_log'

    def __str__(self):
        return f"{self.report.user_config.user.username} - {self.channel} - {self.status}"
