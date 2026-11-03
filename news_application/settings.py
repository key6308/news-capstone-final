"""Django settings for the news application.

Secrets and database connection details are read from environment variables
(see ``.env.example``) so no credentials are stored in the repository. If a
``.env`` file exists in the project root and ``python-dotenv`` is installed,
its values are loaded first; variables already set in the environment take
precedence.

Environment variables:
    * ``DJANGO_SECRET_KEY`` -- secret key (default: a development-only value).
    * ``DJANGO_DEBUG`` -- ``True`` or ``False`` (default ``True``).
    * ``ALLOWED_HOSTS`` -- comma-separated host names
      (default ``127.0.0.1,localhost``).
    * ``DB_NAME``, ``DB_USER``, ``DB_PASSWORD``, ``DB_HOST``, ``DB_PORT`` --
      MySQL/MariaDB connection details.
    * ``APPROVED_API_URL`` -- endpoint called after an article is approved.

Other notable settings:
    * ``AUTH_USER_MODEL`` is :class:`news.models.User`.
    * The REST API uses token authentication and requires sign-in by default.
    * Emails are printed to the console (``EMAIL_BACKEND`` is the console
      backend), which is suitable for local development.
"""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

try:
    from dotenv import load_dotenv
except ImportError:  # python-dotenv is optional; use the real environment.
    pass
else:
    load_dotenv(BASE_DIR / '.env')

SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'dev-only-change-me')
DEBUG = os.getenv('DJANGO_DEBUG', 'True').lower() == 'true'
ALLOWED_HOSTS = [
    host.strip()
    for host in os.getenv('ALLOWED_HOSTS', '127.0.0.1,localhost').split(',')
    if host.strip()
]

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework.authtoken',
    'news',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'news_application.urls'
TEMPLATES = [{
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'DIRS': [BASE_DIR / 'news' / 'templates'],
    'APP_DIRS': True,
    'OPTIONS': {
        'context_processors': [
            'django.template.context_processors.request',
            'django.contrib.auth.context_processors.auth',
            'django.contrib.messages.context_processors.messages',
        ],
    },
}]
WSGI_APPLICATION = 'news_application.wsgi.application'
ASGI_APPLICATION = 'news_application.asgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.getenv('DB_NAME', 'news_capstone'),
        'USER': os.getenv('DB_USER', 'news_user'),
        'PASSWORD': os.getenv('DB_PASSWORD', 'change-me'),
        'HOST': os.getenv('DB_HOST', '127.0.0.1'),
        'PORT': os.getenv('DB_PORT', '3306'),
        'OPTIONS': {'charset': 'utf8mb4'},
    }
}

_VALIDATORS = 'django.contrib.auth.password_validation'
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': f'{_VALIDATORS}.UserAttributeSimilarityValidator'},
    {'NAME': f'{_VALIDATORS}.MinimumLengthValidator'},
    {'NAME': f'{_VALIDATORS}.CommonPasswordValidator'},
    {'NAME': f'{_VALIDATORS}.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'America/Chicago'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
AUTH_USER_MODEL = 'news.User'
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'home'
LOGOUT_REDIRECT_URL = 'home'

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
DEFAULT_FROM_EMAIL = 'news@example.com'
APPROVED_API_URL = os.getenv(
    'APPROVED_API_URL', 'http://127.0.0.1:8000/api/approved/'
)

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}
