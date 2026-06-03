import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('marketplace')
app.conf.broker_connection_retry_on_startup = True
# ✅ این خطوط رو اضافه کن:
app.config_from_object('django.conf:settings', namespace='CELERY')

# ✅ تنظیمات صریح broker و result backend
app.conf.broker_url = os.environ.get('CELERY_BROKER_URL', 'redis://redis:6379/1')
app.conf.result_backend = 'django-db'
app.conf.task_serializer = 'json'
app.conf.result_serializer = 'json'
app.conf.accept_content = ['json']
app.conf.timezone = 'Asia/Tehran'
app.conf.enable_utc = False

# ✅ مسیر task ها
app.autodiscover_tasks(['apps.accounts'])

# ✅ اضافه کن: task رو حتماً acknowledge کنه
app.conf.task_acks_late = True
app.conf.task_reject_on_worker_lost = True

# beat schedule
app.conf.beat_schedule = {
    'clean-expired-otps': {
        'task': 'accounts.clean_expired_otps',
        'schedule': crontab(minute=0, hour='*/1'),
    },
    'clean-expired-otps': {
        'task': 'accounts.clean_expired_otps',
        'schedule': crontab(minute=0, hour='*/1'),  # هر یک ساعت
    },
    'deactivate-inactive-users': {
        'task': 'accounts.deactivate_inactive_users',
        'schedule': crontab(hour=2, minute=0),  # هر روز ساعت 2 صبح
    },
    'unlock-locked-accounts': {
        'task': 'accounts.unlock_locked_accounts',
        'schedule': crontab(minute='*/30'),  # هر 30 دقیقه
    },
    'clean-old-devices': {
        'task': 'accounts.clean_old_devices',
        'schedule': crontab(day_of_week=0, hour=3, minute=0),  # هر یکشنبه ساعت 3 صبح
    },
    'check-system-health': {
        'task': 'accounts.check_system_health',
        'schedule': crontab(minute='*/5'),  # هر 5 دقیقه
    },
    'send-admin-daily-report': {
        'task': 'accounts.send_admin_daily_report',
        'schedule': crontab(hour=8, minute=0),  # هر روز ساعت 8 صبح
    },
    'generate-user-report-daily': {
        'task': 'accounts.generate_user_report',
        'schedule': crontab(hour=0, minute=5),  # هر روز ساعت 00:05
        'kwargs': {'report_type': 'daily'},
    },
    'generate-user-report-weekly': {
        'task': 'accounts.generate_user_report',
        'schedule': crontab(day_of_week=0, hour=1, minute=0),  # هر یکشنبه
        'kwargs': {'report_type': 'weekly'},
    },
}