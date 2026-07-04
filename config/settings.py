"""
Django settings for ИРВЦ project.

Все чувствительные значения — из .env через python-dotenv.
См. .env.example для полного списка переменных.
"""

from pathlib import Path
import os
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / '.env')

# ==============================================================
# Основное
# ==============================================================
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'insecure-key-for-dev-only-change-in-production')
DEBUG = os.environ.get('DJANGO_DEBUG', 'True').lower() == 'true'
ALLOWED_HOSTS = os.environ.get('DJANGO_ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')
CSRF_TRUSTED_ORIGINS = (
    os.environ.get('DJANGO_CSRF_TRUSTED_ORIGINS', '').split(',')
    if os.environ.get('DJANGO_CSRF_TRUSTED_ORIGINS') else []
)

# ==============================================================
# Приложения
# ==============================================================
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third-party
    'solo',                          # singleton для SiteSettings
    'django_celery_beat',            # расписание Celery-задач в БД

    # Наши приложения
    'apps.core',
    'apps.team',
    'apps.news',
    'apps.projects',
    'apps.contacts',
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

ROOT_URLCONF = 'config.urls'
WSGI_APPLICATION = 'config.wsgi.application'

# ==============================================================
# Шаблоны
# ==============================================================
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'apps.core.context_processors.site_context',
            ],
        },
    },
]

# ==============================================================
# База данных
# ==============================================================
# Если MYSQL_HOST задан (в docker-compose) — MySQL.
# Иначе — SQLite для быстрых локальных тестов без Docker.
if os.environ.get('MYSQL_HOST'):
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': os.environ.get('MYSQL_DATABASE', 'irvc'),
            'USER': os.environ.get('MYSQL_USER', 'irvc'),
            'PASSWORD': os.environ.get('MYSQL_PASSWORD', 'irvc'),
            'HOST': os.environ.get('MYSQL_HOST'),
            'PORT': os.environ.get('MYSQL_PORT', '3306'),
            'OPTIONS': {
                # utf8mb4 умеет всю кириллицу + эмодзи; utf8 (без mb4) — устаревшее
                'charset': 'utf8mb4',
                # Строгий SQL-режим ловит ошибки типа неявных обрезаний строк
                'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
            },
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# ==============================================================
# Валидация паролей
# ==============================================================
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ==============================================================
# Локаль
# ==============================================================
LANGUAGE_CODE = 'ru-ru'
TIME_ZONE = 'Europe/Moscow'
USE_I18N = True
USE_TZ = True

# ==============================================================
# Статика и media
# ==============================================================
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ==============================================================
# Celery
# ==============================================================
CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL', 'redis://localhost:6379/0')
CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')
CELERY_TIMEZONE = TIME_ZONE
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 5 * 60                     # жёсткий лимит 5 минут на задачу
CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'

# ==============================================================
# Настройки проекта
# ==============================================================
VK_SERVICE_TOKEN = os.environ.get('VK_SERVICE_TOKEN', '')
VK_API_VERSION = '5.199'
