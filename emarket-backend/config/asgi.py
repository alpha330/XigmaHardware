"""
ASGI config for marketplace project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/asgi/
"""

import os
import sys
from pathlib import Path

from django.core.asgi import get_asgi_application

# Add project root to path
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))

# Set default settings module
run_as = os.environ.get('RUN_AS', 'dev')

if run_as == 'prod':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.prod')
elif run_as == 'stage':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.stage')
else:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.dev')

# Initialize Django ASGI application early
django_asgi_app = get_asgi_application()

# Initialize Sentry for ASGI (if configured)
try:
    import sentry_sdk
    from sentry_sdk.integrations.asgi import SentryAsgiMiddleware
    
    if os.environ.get('SENTRY_DSN'):
        sentry_sdk.init(
            dsn=os.environ.get('SENTRY_DSN'),
            environment=run_as,
            traces_sample_rate=1.0 if run_as == 'dev' else 0.1,
            profiles_sample_rate=1.0 if run_as == 'dev' else 0.1,
        )
except ImportError:
    pass

# Try to setup Channels (WebSocket support)
try:
    from channels.routing import ProtocolTypeRouter, URLRouter
    from channels.auth import AuthMiddlewareStack
    from channels.security.websocket import AllowedHostsOriginValidator
    
    # Import your WebSocket routing
    # از اپ‌های مختلف می‌تونی import کنی
    from django.urls import path
    
    # اینجا routing های WebSocket رو اضافه کن
    # مثال:
    # from apps.market.routing import websocket_urlpatterns as market_ws
    # from apps.notification.routing import websocket_urlpatterns as notification_ws
    
    websocket_urlpatterns = [
        # مسیرهای WebSocket اینجا اضافه بشن
        # path('ws/market/', include(market_ws)),
        # path('ws/notifications/', include(notification_ws)),
    ]
    
    # Build WebSocket application
    websocket_application = AllowedHostsOriginValidator(
        AuthMiddlewareStack(
            URLRouter(websocket_urlpatterns)
        )
    )
    
    # Combine HTTP and WebSocket
    application = ProtocolTypeRouter({
        "http": django_asgi_app,
        "websocket": websocket_application,
    })
    
    use_channels = True
    
except ImportError:
    # Channels not installed, use Django ASGI only
    application = django_asgi_app
    use_channels = False

# Wrap with Sentry
try:
    if os.environ.get('SENTRY_DSN'):
        application = SentryAsgiMiddleware(application)
except NameError:
    pass

# Add health check middleware for ASGI
class ASGIHealthCheckMiddleware:
    """ASGI Health check middleware"""
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        if scope['type'] == 'http' and scope.get('path') == '/health/':
            await send({
                'type': 'http.response.start',
                'status': 200,
                'headers': [
                    (b'content-type', b'application/json'),
                ],
            })
            await send({
                'type': 'http.response.body',
                'body': b'{"status": "healthy", "environment": "' + run_as.encode() + b'", "websocket": ' + str(use_channels).encode() + b'}',
            })
            return
        
        await self.app(scope, receive, send)

# Apply health check
application = ASGIHealthCheckMiddleware(application)