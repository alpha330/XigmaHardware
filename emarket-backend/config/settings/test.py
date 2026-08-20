from .base import *


DEBUG = False
ENVIRONMENT = 'test'
SECRET_KEY = 'test-only-secret-key'
ALLOWED_HOSTS = ['testserver', 'localhost', '127.0.0.1']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'xigma-hardware-tests',
    }
}

SESSION_ENGINE = 'django.contrib.sessions.backends.db'
EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'
PASSWORD_HASHERS = ['django.contrib.auth.hashers.MD5PasswordHasher']

CELERY_BROKER_URL = 'memory://'
CELERY_RESULT_BACKEND = 'cache+memory://'
CELERY_TASK_ALWAYS_EAGER = False
