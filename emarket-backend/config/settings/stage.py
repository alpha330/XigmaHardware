from .base import *
from django.core.exceptions import ImproperlyConfigured

DEBUG = False
ENVIRONMENT = 'staging'

SECRET_KEY = os.getenv('SECRET_KEY')
if not SECRET_KEY:
    raise ImproperlyConfigured('SECRET_KEY is required in staging.')

ALLOWED_HOSTS = [
    host.strip() for host in os.getenv('ALLOWED_HOSTS', '').split(',')
    if host.strip()
]

DB_SSLMODE = os.getenv('DB_SSLMODE', 'prefer')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME'),
        'USER': os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST'),
        'PORT': os.getenv('DB_PORT', '5432'),
        'CONN_MAX_AGE': 600,
        'OPTIONS': {'sslmode': DB_SSLMODE},
    }
}

# Security settings
SECURE_SSL_REDIRECT = os.getenv('SECURE_SSL_REDIRECT', 'false').lower() == 'true'
SECURE_COOKIES = os.getenv('SECURE_COOKIES', 'false').lower() == 'true'
SESSION_COOKIE_SECURE = SECURE_COOKIES
CSRF_COOKIE_SECURE = SECURE_COOKIES
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_HSTS_SECONDS = int(os.getenv('SECURE_HSTS_SECONDS', '0'))
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
USE_X_FORWARDED_HOST = True

CORS_ALLOWED_ORIGINS = [
    origin.strip() for origin in os.getenv('CORS_ALLOWED_ORIGINS', '').split(',')
    if origin.strip()
]
CSRF_TRUSTED_ORIGINS = [
    origin.strip() for origin in os.getenv('CSRF_TRUSTED_ORIGINS', '').split(',')
    if origin.strip()
]

if os.getenv('DJANGO_LOG_TO_FILE', 'false').lower() == 'true':
    (BASE_DIR / 'logs').mkdir(parents=True, exist_ok=True)
    LOGGING['handlers']['file'] = {
        'class': 'logging.handlers.RotatingFileHandler',
        'filename': BASE_DIR / 'logs/django.log',
        'maxBytes': 1024 * 1024 * 10,
        'backupCount': 5,
        'formatter': 'verbose',
    }
    LOGGING['root']['handlers'].append('file')
