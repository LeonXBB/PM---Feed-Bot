"""
Django settings for feed_bot project.

Generated by 'django-admin startproject' using Django 4.0.3.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.0/ref/settings/
"""

from pathlib import Path

import os

from decouple import config

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config("django_key")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config("django_debug_mode")

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'tg_bot.apps.TgBotConfig',
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

ROOT_URLCONF = 'feed_bot.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, "/templates/"),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'feed_bot.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.0/ref/settings/#databases

DATABASE_ROUTERS = ('tg_bot.dbrouters.defaultFileScan',)

DATABASES = {
    'default': {

        'ENGINE': 'django.db.backends.postgresql_psycopg2',

        'NAME': 'default',

        'USER': config("postgres_user"),

        'PASSWORD': config("postgres_password"),

        'HOST': config("postgres_host"),

        'PORT': config("postgres_port")
    },

    'logic': {

        'ENGINE': 'django.db.backends.postgresql_psycopg2',

        'NAME': 'logic',

        'USER': config("postgres_user"),

        'PASSWORD': config("postgres_password"),

        'HOST': config("postgres_host"),

        'PORT': config("postgres_port")
    },

    'localization': {

        'ENGINE': 'django.db.backends.postgresql_psycopg2',

        'NAME': 'localization',

        'USER': config("postgres_user"),

        'PASSWORD': config("postgres_password"),

        'HOST': config("postgres_host"),

        'PORT': config("postgres_port")
    },

    'telebot': {

        'ENGINE': 'django.db.backends.postgresql_psycopg2',

        'NAME': 'telebot',

        'USER': config("postgres_user"),

        'PASSWORD': config("postgres_password"),

        'HOST': config("postgres_host"),

        'PORT': config("postgres_port")
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Europe/Kiev'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.0/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/4.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
