"""Базовые настройки Django проекта."""
import os
import sys
from pathlib import Path

from decouple import config

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Добавляем пути к приложениям в sys.path
sys.path.append(str(BASE_DIR))
sys.path.append(os.path.join(BASE_DIR, 'apps'))


SECRET_KEY = config('SECRET_KEY', cast=str)

# Stripe - USD keys (default)
STRIPE_SECRET_KEY = config('STRIPE_SECRET_KEY', cast=str)
STRIPE_PUBLIC_KEY = config('STRIPE_PUBLIC_KEY', cast=str)

# Stripe optional
STRIPE_SECRET_KEY_KZT = (
    config('STRIPE_SECRET_KEY_KZT', default='', cast=str) or
    STRIPE_SECRET_KEY
)
STRIPE_PUBLIC_KEY_KZT = (
    config('STRIPE_PUBLIC_KEY_KZT', default='', cast=str) or
    STRIPE_PUBLIC_KEY
)


DEBUG = config('DEBUG', cast=bool)

ALLOWED_HOSTS = config(
    'ALLOWED_HOSTS',
    default='*',
    cast=lambda v: (
        [s.strip() for s in v.split(',')] if v != '*' else ['*']
    )
)


DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

PROJECT_APPS = [
    'abstracts.apps.AbstractsConfig',
    'items.apps.ItemsConfig',
    'orders.apps.OrdersConfig'
]

INSTALLED_APPS = DJANGO_APPS + PROJECT_APPS

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'settings.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'settings.wsgi.application'


# Database configuration
# По умолчанию используется PostgreSQL, если указаны переменные окружения
# Иначе используется SQLite для локальной разработки
if 'DATABASE_URL' in os.environ:
    # Использование PostgreSQL через DATABASE_URL (для продакшена)
    import dj_database_url
    DATABASES = {
        'default': dj_database_url.parse(os.environ.get('DATABASE_URL'))
    }
elif all([
    config('DB_NAME', default='', cast=str),
    config('DB_USER', default='', cast=str),
    config('DB_PASSWORD', default='', cast=str),
]):
    # Использование PostgreSQL через отдельные переменные окружения
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': config('DB_NAME', cast=str),
            'USER': config('DB_USER', cast=str),
            'PASSWORD': config('DB_PASSWORD', cast=str),
            'HOST': config('DB_HOST', default='localhost', cast=str),
            'PORT': config('DB_PORT', default='5432', cast=str),
        }
    }
else:
    # SQLite для локальной разработки (если PostgreSQL не настроен)
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }


AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': (
            'django.contrib.auth.password_validation.'
            'UserAttributeSimilarityValidator'
        ),
    },
    {
        'NAME': (
            'django.contrib.auth.password_validation.'
            'MinimumLengthValidator'
        ),
    },
    {
        'NAME': (
            'django.contrib.auth.password_validation.'
            'CommonPasswordValidator'
        ),
    },
    {
        'NAME': (
            'django.contrib.auth.password_validation.'
            'NumericPasswordValidator'
        ),
    },
]


LANGUAGE_CODE = 'ru-RU'

TIME_ZONE = 'Asia/Almaty'

USE_I18N = True

USE_TZ = True


STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'


MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"


if not DEBUG:
    MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')
    STATICFILES_STORAGE = (
        'whitenoise.storage.CompressedManifestStaticFilesStorage'
    )
