"""
Main URL Configuration for Marketplace

این فایل شامل:
- Django Admin
- API v1 Routes
- API Documentation (Swagger/ReDoc)
- Health Check
- Debug Toolbar (dev only)
- Static & Media files (dev only)
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include, re_path
from django.views.generic import TemplateView, RedirectView
from django.http import JsonResponse
from rest_framework import permissions
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)


# ==================== Health Check View ====================
def health_check(request):
    """
    Health check endpoint برای Docker و Load Balancer
    """
    from django.db import connections
    from django.db.utils import OperationalError
    from django.core.cache import cache

    health_status = {
        'status': 'healthy',
        'environment': settings.ENVIRONMENT if hasattr(settings, 'ENVIRONMENT') else 'unknown',
        'version': '1.0.0',
        'timestamp': __import__('django').utils.timezone.now().isoformat(),
        'checks': {
            'database': 'ok',
            'cache': 'ok',
            'celery': 'ok',
        }
    }

    # Check database
    try:
        db_conn = connections['default']
        db_conn.cursor()
    except OperationalError:
        health_status['checks']['database'] = 'error'
        health_status['status'] = 'unhealthy'
    except Exception:
        health_status['checks']['database'] = 'unknown'

    # Check cache
    try:
        cache.set('health_check', 'ok', 10)
        if cache.get('health_check') != 'ok':
            health_status['checks']['cache'] = 'error'
            health_status['status'] = 'degraded'
    except Exception:
        health_status['checks']['cache'] = 'error'
        health_status['status'] = 'degraded'

    # Check Celery (simple ping)
    try:
        from config.celery import app
        result = app.control.ping(timeout=1)
        if not result:
            health_status['checks']['celery'] = 'error'
    except Exception:
        health_status['checks']['celery'] = 'unknown'

    status_code = 200 if health_status['status'] == 'healthy' else 503

    return JsonResponse(health_status, status=status_code)


def ready_check(request):
    """
    Readiness check برای Kubernetes
    """
    return JsonResponse({'ready': True})


def live_check(request):
    """
    Liveness check برای Kubernetes
    """
    return JsonResponse({'alive': True})


# ==================== API Documentation ====================

# api_info = openapi.Info(
#     title="Marketplace API",
#     default_version='v1',
#     description="""
#     # Marketplace Backend API

#     ## 🔐 Authentication
#     - JWT Token based authentication
#     - Login with email/mobile + password
#     - OTP verification support
#     - Token refresh mechanism

#     ## 👤 User Types
#     - **Super Admin**: Full system access
#     - **Client/Customer**: Regular users
#     - **Accountant**: Financial management
#     - **Courier**: Delivery management
#     - **Stock Keeper**: Inventory management

#     ## 📋 Features
#     - User & Profile Management
#     - Wallet & Transaction System
#     - Device Management & Security
#     - Multi-environment support (Dev/Stage/Prod)

#     ## 🌐 Base URLs
#     - **Development**: http://localhost:8000/api/v1/
#     - **Staging**: https://staging-api.marketplace.com/api/v1/
#     - **Production**: https://api.marketplace.com/api/v1/

#     ## 📧 Testing Emails (Dev)
#     - MailHog: http://localhost:8025/

#     ## 📚 More Documentation
#     - Swagger UI: /swagger/
#     - ReDoc: /redoc/
#     """,
#     terms_of_service="https://marketplace.com/terms/",
#     contact=openapi.Contact(
#         name="Marketplace Team",
#         email="dev@marketplace.com",
#         url="https://marketplace.com/contact",
#     ),
#     license=openapi.License(
#         name="Proprietary License",
#         url="https://marketplace.com/license/",
#     ),
# )

# schema_view = get_schema_view(
#     api_info,
#     public=True,
#     permission_classes=(permissions.AllowAny,),
#     patterns=[
#         path('api/v1/', include('config.api_urls')),
#     ],
#     authentication_classes=[],
#     validators=['flex', 'ssv'],
# )


# ==================== Admin Site Customization ====================

admin.site.site_header = "Marketplace Administration"
admin.site.site_title = "Marketplace Admin"
admin.site.index_title = "Welcome to Marketplace Admin Panel"
admin.site.site_url = "/api/v1/"


# ==================== URL Patterns ====================

urlpatterns = [
    # ==================== Admin ====================
    path('admin/', admin.site.urls),
    path('admin/doc/', include('django.contrib.admindocs.urls')),

    # ==================== Health Checks ====================
    path('health/', health_check, name='health-check'),
    path('ready/', ready_check, name='ready-check'),
    path('live/', live_check, name='live-check'),
    path('healthz/', health_check, name='healthz'),  # Kubernetes standard
    path('readyz/', ready_check, name='readyz'),      # Kubernetes standard

    # ==================== API v1 ====================
    path('api/v1/', include('config.api_urls')),

    # ==================== API Documentation ====================
     # API Schema
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),

    # Swagger UI
    path('swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),

    # ReDoc
    path('redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    path(
        'api-docs/',
        RedirectView.as_view(url='/swagger/', permanent=False),
        name='api-docs'
    ),

    # ==================== Auth (اختیاری - برای Browsable API) ====================
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),

    # ==================== API Root ====================
    path('api/', RedirectView.as_view(url='/api/v1/', permanent=False)),
    path('', RedirectView.as_view(url='/swagger/', permanent=False)),
]

# ==================== Development Only ====================

if settings.DEBUG:
    # Debug Toolbar
    import debug_toolbar
    urlpatterns += [
        path('__debug__/', include(debug_toolbar.urls)),
    ]

    # Silk Profiling
    urlpatterns += [
        path('silk/', include('silk.urls', namespace='silk')),
    ]

    # Static & Media Files
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

    # Browser Reload (for development)
    urlpatterns += [
        path('__reload__/', include('django_browser_reload.urls')),
    ]

# ==================== Error Handlers ====================

handler400 = 'config.error_handlers.bad_request'
handler403 = 'config.error_handlers.permission_denied'
handler404 = 'config.error_handlers.page_not_found'
handler500 = 'config.error_handlers.server_error'