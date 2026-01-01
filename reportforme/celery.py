"""
Celery configuration for ReportForMe
"""
import os
from celery import Celery
from celery.schedules import crontab

# Set the default Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'reportforme.settings')

app = Celery('reportforme')

# Load config from Django settings, all config keys should have a `CELERY_` prefix
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks from all registered Django apps
app.autodiscover_tasks()

# Celery Beat Schedule
app.conf.beat_schedule = {
    # Generate daily reports at 11:45 PM (to collect commits from entire day)
    'generate-daily-reports': {
        'task': 'core.tasks.generate_daily_reports',
        'schedule': crontab(hour=23, minute=45),  # 11:45 PM daily
        'options': {'queue': 'default'}
    },
    # Send scheduled reports every hour
    'send-scheduled-reports': {
        'task': 'core.tasks.send_scheduled_reports',
        'schedule': crontab(minute=0),  # Every hour
        'options': {'queue': 'default'}
    },
    # Cleanup old commits daily at 2 AM
    'cleanup-old-commits': {
        'task': 'core.tasks.cleanup_old_commits',
        'schedule': crontab(hour=2, minute=0),  # 2:00 AM daily
        'options': {'queue': 'default'}
    },
}


@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
