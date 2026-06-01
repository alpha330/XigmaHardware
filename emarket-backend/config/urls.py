"""
Main URL Configuration for Marketplace
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include, re_path
from django.views.generic import TemplateView
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# ==================== API Documentation ====================

schema_view = get_schema_view(
    openapi.Info(
        title="Marketplace API",
        default_version='v1',
        description="""
        Marketplace API Documentation
        
        ## Authentication
        - JWT Token based authentication
        - Login with email or mobile
        - OTP verification support
        
        ## Features
        - User Management
        - Profile Management (Individual/Legal)
        - Wallet System
        - Device Management
        
        ## Base URL
        - Development: http://localhost:8000/api/v1/
        - Staging: https://staging-api.example.com/api/v1/
        - Production: https://api.example.com/api/v1/
        """,
        terms_of_service="https://www.example.com/terms/",
        contact=openapi.Contact(
            name="Marketplace Support",
            email="support@marketplace.com",
            url="https://www.marketplace.com/contact",
        ),
        license=openapi.License(
            name="Proprietary",
            url="https://www.example.com/license/",
        ),
        x_logo={
            "url": "https://www.example.com/logo.png",
            "backgroundColor": "#FFFFFF",
            "altText": "Marketplace Logo"
        },
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
    patterns=[
        path('api/v1/', include('config.api_urls')),
    ],
)

# ==================== URL Patterns ====================

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # API Documentation
    re_path(
        r'^swagger(?P<format>\.json|\.yaml)$',
        schema_view.without_ui(cache_timeout=0),
        name='schema-json'
    ),
    path(
        'swagger/',
        schema_view.with_ui('swagger', cache_timeout=0),
        name='schema-swagger-ui'
    ),
    path(
        'redoc/',
        schema_view.with_ui('redoc', cache_timeout=0),
        name='schema-redoc'
    ),
    
    # API v1
    path('api/v1/', include('config.api_urls')),
    
    # Health Check
    path('health/', include('health_check.urls')),
    
    # Debug Toolbar (only in dev)
    path('__debug__/', include('debug_toolbar.urls')),
]

# Serve static and media files in development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    
    # API Root
    urlpatterns += [
        path('', TemplateView.as_view(template_name='api_root.html'), name='api-root'),
    ]