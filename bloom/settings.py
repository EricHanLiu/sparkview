"""
Django settings for bloom project.

Generated by 'django-admin startproject' using Django 1.11.5.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.11/ref/settings/
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE_DIR = os.path.join(BASE_DIR, 'templates')

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '1x^c8ut0-jx0fo4i+cn0(0ev5y&t3d6w8y4ydfr8wb6(ly%7u7'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

SITE_ID=1
ALLOWED_HOSTS = ['bloom.hyperdigitalserver.com', '127.0.0.1', '35.199.174.226', 'localhost']
ADMINS = [('Octavian','octavian@hdigital.io')]
# Application definition

INSTALLED_APPS = [
    'accounts',
    'adwords_dashboard',
    'bing_dashboard',
    'budget',
    'django_crontab',
    'django_extensions',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
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

ROOT_URLCONF = 'bloom.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [TEMPLATE_DIR,],
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

WSGI_APPLICATION = 'bloom.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'bloom',
        'USER': 'bloom',
        'PASSWORD': 'Digital987x123',
        'HOST': 'localhost',
        'PORT': '',
    }
}


# Password validation
# https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/1.11/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = "/var/www/bloom/static"

STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static/')]

ADWORDS_YAML = os.path.join(BASE_DIR, 'adwords/google_auth/googleads.yaml')

LOGIN_URL = "/"

ACCESS_TOKEN = 'ya29.GlsFBWxsC2vXxFe52v0roxsypsGipRsVl1yxipBvE-L1JIgT1v1zkH_Yntfg79IsbFLFeCCS8tAcMEa3YqhVHf5rWgBKo12LCRQCKxCa563tFnL1Ve_WwXGic239'

CRONJOBS = [
    ('0 5 * * *', 'cron_accounts.main', '> ' + BASE_DIR + '/logs/accounts.log'),
    ('5 5 * * *', 'cron_labels.main', '> ' + BASE_DIR + '/logs/labels.log'),
    ('10 5 * * *', 'cron_ovu.main', '> ' + BASE_DIR + '/logs/ovu.log'),
    ('0 6 * * *', 'cron_anomalies.main', '> ' + BASE_DIR + '/logs/anomalies.log'),
    ('0 7 * * *', 'cron_404.main', '> ' + BASE_DIR + '/logs/404.log'),
    ('0 8 * * *', 'cron_alerts.main', '> ' + BASE_DIR + '/logs/alerts.log'),
    ('0 5 * * *', 'bing_accounts.main', '> ' + BASE_DIR + '/logs/bing_accounts.log'),
    ('40 5 * * *', 'bing_ovu.main', '> ' + BASE_DIR + '/logs/bing_ovu.log'),
    ('30 6 * * *', 'bing_anomalies.main', '> ' + BASE_DIR + '/logs/bing_anomalies.log'),
]

# Bing Stuff

#if DEBUG:
#    REDIRECT_URI = "http://localhost:8000/dashboards/bing/auth/exchange"
#else:
REDIRECT_URI = "https://bloom.hyperdigitalserver.com/dashboards/bing/auth/exchange"

CLIENT_ID = "b154faf8-2248-4eb5-83fe-f1897ef45cb7"
CLIENT_SECRET = "hspjJNTY4]-udkLBM3045*~"
DEVELOPER_TOKEN = "1215QQ0H16176244"
DEVELOPER_TOKEN_SANDBOX = "BBD37VB98"
ENVIRONMENT = "production"
BINGADS_REPORTS = os.path.join(BASE_DIR, 'bing_reports/')
