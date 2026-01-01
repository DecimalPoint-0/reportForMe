"""
Celery tasks for scheduled report generation and delivery
"""
from celery import shared_task
from django.utils import timezone
from datetime import date, datetime
from pytz import timezone as pytz_timezone
from core.models import UserConfig, Report, Commit
from core.services.commit_aggregator import CommitAggregator
from core.services.report_generator import ReportGenerator
from core.services.email_service import EmailService
import logging

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def generate_daily_reports(self):
    """
    Generate daily reports for all active users
    Scheduled to run every day
    """
    active_users = UserConfig.objects.filter(is_active=True)
    reports_generated = 0

    for user_config in active_users:
        try:
            # Fetch commits
            aggregator = CommitAggregator()
            commit_count = aggregator.aggregate_daily_commits(user_config)

            if commit_count == 0:
                logger.info(f"No commits for {user_config.user.username} today")
                continue

            # Get today's commits
            today = date.today()
            commits = Commit.objects.filter(
                user_config=user_config,
                commit_date__date=today,
                is_processed=False
            ).values()

            if not commits.exists():
                logger.info(f"No unprocessed commits for {user_config.user.username}")
                continue

            # Generate report
            report_generator = ReportGenerator()
            report_data = report_generator.generate_report(
                list(commits),
                user_config.user.get_full_name() or user_config.user.username,
                today
            )

            # Create report
            report, created = Report.objects.get_or_create(
                user_config=user_config,
                report_date=today,
                defaults={
                    'content_html': report_data['html'],
                    'content_text': report_data['text'],
                    'commit_count': report_data['commit_count'],
                    'repo_count': report_data['repo_count'],
                    'status': 'draft'
                }
            )

            if created:
                # Mark commits as processed
                Commit.objects.filter(
                    user_config=user_config,
                    commit_date__date=today
                ).update(is_processed=True)

                logger.info(f"Generated report for {user_config.user.username}")
                reports_generated += 1

        except Exception as e:
            logger.error(f"Error generating report for {user_config.user.username}: {str(e)}")
            # Retry up to 3 times
            raise self.retry(exc=e, countdown=300)

    return {
        'status': 'success',
        'reports_generated': reports_generated,
        'timestamp': timezone.now().isoformat()
    }


@shared_task(bind=True, max_retries=3)
def send_scheduled_reports(self):
    """
    Send reports to users at their scheduled time
    Scheduled to run every hour
    """
    now = timezone.now()
    reports_sent = 0

    # Get all active users
    active_users = UserConfig.objects.filter(is_active=True)

    for user_config in active_users:
        try:
            # Check if it's time to send report
            user_tz = pytz_timezone(user_config.timezone)
            user_time = now.astimezone(user_tz)

            # Get report time
            report_time = user_config.report_time
            current_time_str = user_time.strftime('%H:%M')
            report_time_str = report_time.strftime('%H:%M')

            # Check if it's the right time (within 5 minute window)
            if current_time_str == report_time_str:
                # Get today's report
                today = date.today()
                report = Report.objects.filter(
                    user_config=user_config,
                    report_date=today,
                    status='draft'
                ).first()

                if report:
                    # Send via email
                    if EmailService.send_report(report):
                        report.status = 'sent'
                        report.sent_at = timezone.now()
                        report.save()
                        reports_sent += 1
                        logger.info(f"Sent report to {user_config.user.username}")
                    else:
                        report.status = 'failed'
                        report.save()
                        logger.error(f"Failed to send report to {user_config.user.username}")

        except Exception as e:
            logger.error(f"Error in send_scheduled_reports for {user_config.user.username}: {str(e)}")
            raise self.retry(exc=e, countdown=300)

    return {
        'status': 'success',
        'reports_sent': reports_sent,
        'timestamp': timezone.now().isoformat()
    }


@shared_task
def cleanup_old_commits():
    """
    Clean up old commits older than 30 days
    Scheduled to run daily
    """
    from datetime import timedelta
    cutoff_date = timezone.now() - timedelta(days=30)

    deleted_count, _ = Commit.objects.filter(
        fetched_at__lt=cutoff_date
    ).delete()

    logger.info(f"Cleaned up {deleted_count} old commits")

    return {
        'status': 'success',
        'deleted_commits': deleted_count
    }
