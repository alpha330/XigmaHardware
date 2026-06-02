"""
WSGI config for marketplace project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/wsgi/
"""

import os
import sys
from pathlib import Path

from django.core.wsgi import get_wsgi_application

# Add project root to path
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))

# Set default settings module
# این می‌تونه توسط environment variable override بشه
run_as = os.environ.get('RUN_AS', 'dev')

if run_as == 'prod':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.prod')
elif run_as == 'stage':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.stage')
else:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.dev')

# Initialize Sentry for WSGI (if configured)
try:
    import sentry_sdk
    from sentry_sdk.integrations.wsgi import SentryWsgiMiddleware
    
    if os.environ.get('SENTRY_DSN'):
        sentry_sdk.init(
            dsn=os.environ.get('SENTRY_DSN'),
            environment=run_as,
            traces_sample_rate=1.0 if run_as == 'dev' else 0.1,
            profiles_sample_rate=1.0 if run_as == 'dev' else 0.1,
        )
except ImportError:
    pass

# Get WSGI application
application = get_wsgi_application()

# Wrap with monitoring middleware in production
if run_as == 'prod':
    try:
        from django_prometheus.wsgi import PrometheusWSGIHandler
        application = PrometheusWSGIHandler(application)
    except ImportError:
        pass

# Add health check middleware
class HealthCheckMiddleware:
    """Simple health check middleware"""
    def __init__(self, application):
        self.application = application
    
    def __call__(self, environ, start_response):
        if environ.get('PATH_INFO') == '/health/':
            start_response('200 OK', [('Content-Type', 'application/json')])
            return [b'{"status": "healthy", "environment": "' + run_as.encode() + b'"}']
        return self.application(environ, start_response)

# Apply health check
application = HealthCheckMiddleware(application)