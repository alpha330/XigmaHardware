"""
Marketplace Backend Configuration
"""

# این فایل می‌تونه خالی باشه یا شامل import های Celery
from .celery import app as celery_app

__all__ = ('celery_app',)