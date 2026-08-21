from .base import *

DEBUG = True
ALLOWED_HOSTS = ['*']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME', 'marketplace_dev'),
        'USER': os.getenv('DB_USER', 'postgres'),
        'PASSWORD': os.getenv('DB_PASSWORD', 'postgres'),
        'HOST': os.getenv('DB_HOST', 'localhost'),
        'PORT': os.getenv('DB_PORT', '5432'),
    }
}
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]


# Django Debug Toolbar
INSTALLED_APPS = [*INSTALLED_APPS, 'debug_toolbar', 'silk', 'django_browser_reload']
MIDDLEWARE = [*MIDDLEWARE,
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'silk.middleware.SilkyMiddleware',
    'django_browser_reload.middleware.BrowserReloadMiddleware',
]
INTERNAL_IPS = ['127.0.0.1']
