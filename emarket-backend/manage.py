#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""
    # تنظیم پیش‌فرض settings بر اساس environment
    # می‌تونی با متغیر محیطی RUN_AS تغییرش بدی
    run_as = os.environ.get('RUN_AS', 'dev')
    
    if run_as == 'prod':
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.prod')
    elif run_as == 'stage':
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.stage')
    else:
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.dev')
    
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    
    # این خط مخصوص debug و development هست
    if os.environ.get('RUN_MAIN') or os.environ.get('WERKZEUG_RUN_MAIN'):
        # فعال‌سازی autoreload برای development
        pass
    
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()