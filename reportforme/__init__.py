"""ReportForMe - Automated Daily Work Report Generator"""
from .celery import app as celery_app

__all__ = ('celery_app',)
