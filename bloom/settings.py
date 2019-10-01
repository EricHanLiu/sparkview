"""
Django settings for bloom project.

Generated by 'django-admin startproject' using Django 1.11.5.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.11/ref/settings/
"""

import os
import sys

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE_DIR = os.path.join(BASE_DIR, 'templates')

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '1x^c8ut0-jx0fo4i+cn0(0ev5y&t3d6w8y4ydfr8wb6(ly%7u7'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

SITE_ID = 1

ALLOWED_HOSTS = [
    '35.203.133.58',
    '127.0.0.1',
    'localhost',
    'app.mibhub.com',
    "*"
]

ADMINS = [
    ('Bloom Dev', 'dev@makeitbloom.com'),
    ('Lexi', 'lexi@makeitbloom.com'),
    ('Sam', 'sam@makeitbloom.com')
]
# Application definition

INSTALLED_APPS = [
    'accounts',
    'adwords_dashboard',
    'bing_dashboard',
    'facebook_dashboard',
    'budget',
    'tools',
    'client_area',
    'user_management',
    'reports',
    'insights',
    'notifications',
    'social_django',
    'monitor',
    'corsheaders',
    'django_crontab',
    'django_extensions',
    'django_celery_results',
    'django_celery_beat',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'admin_honeypot',
    'rest_framework',
    'rest_framework.authtoken'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'social_django.middleware.SocialAuthExceptionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
]

AUTHENTICATION_BACKENDS = (
    'social_core.backends.google.GoogleOAuth2',
    'django.contrib.auth.backends.ModelBackend')

ROOT_URLCONF = 'bloom.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [TEMPLATE_DIR, ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'social_django.context_processors.backends',
                'social_django.context_processors.login_redirect',
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
        'NAME': os.environ.get('PSQL_NAME', 'bloom'),
        'USER': os.environ.get('PSQL_USER', 'bloom'),
        'PASSWORD': os.environ.get('PSQL_PASSWORD', 'bloom123'),
        'HOST': os.environ.get('PSQL_HOST', 'localhost'),
        'PORT': 5432,
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

TIME_ZONE = 'EST'

USE_I18N = True

USE_L10N = False

USE_TZ = True

DATE_FORMAT = 'Y-m-d'

SOCIAL_AUTH_PIPELINE = (
    'social_core.pipeline.social_auth.social_details',
    'social_core.pipeline.social_auth.social_uid',
    'social_core.pipeline.social_auth.auth_allowed',
    'social_core.pipeline.social_auth.social_user',
    'social_core.pipeline.user.get_username',
    'social_core.pipeline.social_auth.associate_by_email',
    # 'social_core.pipeline.user.create_user',
    'social_core.pipeline.social_auth.associate_user',
    'social_core.pipeline.social_auth.load_extra_data',
    'social_core.pipeline.user.user_details',
)

SOCIAL_AUTH_POSTGRES_JSONFIELD = True
SOCIAL_AUTH_GOOGLE_OAUTH2_AUTH_EXTRA_ARGUMENTS = {
    'hd': 'makeitbloom.com',
    'access_type': 'online',
}
SOCIAL_AUTH_GOOGLE_OAUTH2_WHITELISTED_DOMAINS = ['makeitbloom.com']
SOCIAL_AUTH_RAISE_EXCEPTIONS = False
SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = '967183304564-54i17l22sad6f9dt28eos6bjaohf1frh.apps.googleusercontent.com'
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = 'AFQ5EqzWXICEFMwLfEumz9C5'

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = '/var/www/bloom/static'

STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static/')]

ADWORDS_YAML = os.path.join(BASE_DIR, 'adwords_dashboard/google_auth/googleads.yaml')
API_VERSION = 'v201809'
BING_API_VERSION = 13
FACEBOOK_ADS_VERSION = 'v3.3'

LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'index'
LOGIN_ERROR_URL = 'login'
SOCIAL_AUTH_LOGIN_ERROR_URL = 'login'

ACCESS_TOKEN = 'ya29.GlsFBWxsC2vXxFe52v0roxsypsGipRsVl1yxipBvE-L1JIgT1v1zkH_Yntfg79IsbFLFeCCS8tAcMEa3YqhVHf5rWgBKo12LCRQCKxCa563tFnL1Ve_WwXGic239'

# CRONJOBS = [
#     # ('0 * * * *', 'cron_clients.main', '> ' + BASE_DIR + '/logs/clients_budgets.log'),
#     # ('00 13 15 * *', 'cron_no_changes.main', '> ' + BASE_DIR + '/logs/cron_no_changes_15.log'),
#     # ('00 13 30 * *', 'cron_no_changes.main', '> ' + BASE_DIR + '/logs/cron_no_changes_30.log'),
#     ('0 8 * * *', 'cron_accounts.main', '> ' + BASE_DIR + '/logs/accounts.log'),
#     ('0 8 * * *', 'bing_accounts.main', '> ' + BASE_DIR + '/logs/bing_accounts.log'),
#     ('0 8 * * *', 'facebook_accounts.main', '> ' + BASE_DIR + '/logs/facebook_accounts.log'),
#     ('00 * * * *', 'cron_campaigns.main', '> ' + BASE_DIR + '/logs/aw_campaigns.log'),
#     ('00 * * * *', 'bing_campaigns.main', '> ' + BASE_DIR + '/logs/bing_campaigns.log'),
#     ('00 * * * *', 'facebook_campaigns.main', '> ' + BASE_DIR + '/logs/facebook_campaigns.log'),
#     ('30 9 * * *', 'facebook_alerts.main', '> ' + BASE_DIR + '/logs/facebook_alerts.log'),
#     ('00 12 * * *', 'cron_budgets.main', '> ' + BASE_DIR + '/logs/budgets.log'),
#     ('00 * * * *', 'cron_ovu.main', '> ' + BASE_DIR + '/logs/ovu.log'),
#     ('00 * * * *', 'bing_ovu.main', '> ' + BASE_DIR + '/logs/bing_ovu.log'),
#     ('00 * * * *', 'facebook_ovu.main', '> ' + BASE_DIR + '/logs/facebook_ovu.log'),
#     ('00 15 * * *', 'cron_account_changes.main', '> ' + BASE_DIR + '/logs/cron_account_changes.log'),
#     ('10 11 * * *', 'cron_ch_mail.main', '> ' + BASE_DIR + '/logs/cron_changes_mail.log'),
#     ('00 12 * * *', 'create_notifications.main', '> ' + BASE_DIR + '/logs/notifications.log'),
#     ('0 0 1 * *', 'create_tier_proposals.main', '> ' + BASE_DIR + '/logs/tier_proposals.log'),
#     ('0 0 1 * *', 'set_inactive_lost_budgets.main', '> ' + BASE_DIR + '/logs/set_inactive_lost_budgets.log'),
#     ('0 22 * * *', 'daily_context.main', '> ' + BASE_DIR + '/logs/daily_context.log'),
#     ('0 0 1 * *', 'set_budget_update_false.main', '> ' + BASE_DIR + '/logs/set_budget_update_false.log'),
#     ('45 10 * * *', 'ninety_days_update.main', '> ' + BASE_DIR + '/logs/ninety_days_update.log'),
#     ('00 * * * *', 'campaign_groups.main', '> ' + BASE_DIR + '/logs/campaign_groups.log'),
#     ('00 * * * *', 'client_area.cron.bad_ads', '> ' + BASE_DIR + '/logs/promo_ads.log'),
#     ('15 11 * * *', 'notifications.cron.prepare_todos', '> ' + BASE_DIR + '/logs/todos.log'),
#     ('55 7 * * *', 'budget.cron.reset_all_campaign_spends', '> ' + BASE_DIR + '/logs/reset_all_campaign_spends.log'),
#     ('00 11 * * *', 'budget.cron.update_budget_spend_history',
#      '> ' + BASE_DIR + '/logs/update_budget_spend_history.log'),
#     ('00 7 1 * *', 'budget.cron.reset_all_budget_renewal_needs',
#      '> ' + BASE_DIR + '/logs/reset_all_budget_renewal_needs.log'),
#
#     ('00 * * * *', 'adwords_dashboard.cron.get_all_spends_by_campaign_this_month',
#      '> ' + BASE_DIR + '/logs/google_get_all_spends_by_campaign_this_month.log'),
#
#     ('00 * * * *', 'facebook_dashboard.cron.get_all_spends_by_facebook_campaign_this_month',
#      '> ' + BASE_DIR + '/logs/get_all_spends_by_facebook_campaign_this_month.log'),
#
#     ('00 * * * *', 'bing_dashboard.cron.get_all_spends_by_bing_campaign_this_month',
#      '> ' + BASE_DIR + '/logs/get_all_spends_by_bing_campaign_this_month.log'),
#
#     ('00 * * * *', 'adwords_dashboard.cron.get_all_spend_by_campaign_custom',
#      '> ' + BASE_DIR + '/logs/google_get_all_spend_by_campaign_custom.log'),
#
#     ('00 * * * *', 'facebook_dashboard.cron.get_all_spend_by_facebook_campaign_custom',
#      '> ' + BASE_DIR + '/logs/get_all_spend_by_facebook_campaign_custom.log'),
#
#     ('00 * * * *', 'bing_dashboard.cron.get_all_spend_by_bing_campaign_custom',
#      '> ' + BASE_DIR + '/logs/get_all_spend_by_bing_campaign_custom.log'),
# ]

# Bing Stuff

if DEBUG:
    REDIRECT_URI = 'http://localhost:8000/dashboards/bing/auth/exchange'
    INSIGHTS_PATH = '/home/sam/Projects/bloom-master/insights/'
else:
    REDIRECT_URI = 'https://app.mibhub.com/dashboards/bing/auth/exchange'
    INSIGHTS_PATH = '/home/sam/bloom-master/insights/'

# Bing Auth
CLIENT_ID = 'b154faf8-2248-4eb5-83fe-f1897ef45cb7'
CLIENT_SECRET = 'hspjJNTY4]-udkLBM3045*~'
DEVELOPER_TOKEN = '1215QQ0H16176244'
DEVELOPER_TOKEN_SANDBOX = 'BBD37VB98'
ENVIRONMENT = 'production'
BINGADS_REPORTS = os.path.join(BASE_DIR, 'bing_reports/')

# Facebook Auth

bloomworker = '100025980313978'
app_id = '582921108716849'
business_id = '10154654586810511'
app_secret = '15a5a1a6c5c4903c678e2b20ce35c66b'
access_token = "EAAISKeWdZCTEBAGyyF5cheVZAGbr546TflaDJ4BhThFKigmetLZAW3SB0YHIGoZAoGGI0wZAYlPZBvV2hHUv6wtO8gD3is8eQGNIqKZAyBkVO5H8FnCTG6lRvV4TSLDpovlAgUrCYqA34I5zWBHrlOKALg8vo8dBqAZD"
w_access_token = "EAAISKeWdZCTEBANbBD1ZA4igkrUYzdacd02E0IggsEfbrKvwvMZBlXvdZCPOgwEycpHTnrmsZCkFFNG7ehPDeo8Ez3PXQlMi6Kz3QWwhMFdqBMXKZCMZAvrAeOIExRdnw0tUNo4VVphEPhRhlD7epvYiwny80W6HlrZCccAXC3cDJduysrZBdmZBMU"

# E-mail settings

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = 'dev@makeitbloom.com'
EMAIL_HOST_PASSWORD = 'ujfgvsieuwptnrgp'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
DEFAULT_EMAIL_FROM = 'dev@makeitbloom.com'

if DEBUG:
    MAIL_ADS = ['lexi@makeitbloom.com', 'sam@makeitbloom.com']
else:
    MAIL_ADS = [
        'xurxo@makeitbloom.com',
        'jeff@makeitbloom.com',
        'franck@makeitbloom.com',
        'marina@makeitbloom.com',
        'lexi@makeitbloom.com',
    ]

if DEBUG:
    WARNING_SYSTEM_EMAILS = ['sam@makeitbloom.com', 'lexi@makeitbloom.com', 'dev@makeitbloom.com']
else:
    WARNING_SYSTEM_EMAILS = ['sam@makeitbloom.com', 'lexi@makeitbloom.com', 'dev@makeitbloom.com',
                             'eric@makeitbloom.com']

if DEBUG:
    LOST_ACCOUNT_EMAILS = ['sam@makeitbloom.com', 'lexi@makeitbloom.com']
else:
    LOST_ACCOUNT_EMAILS = ['lexi@makeitbloom.com',
                           'xurxo@makeitbloom.com',
                           'phil@makeitbloom.com',
                           'mike@makeitbloom.com',
                           'nick@makeitbloom.com',
                           'martin@makeitbloom.com',
                           'jeff@makeitbloom.com',
                           'jamie@makeitbloom.com',
                           'pascal@makeitbloom.com']

if DEBUG:
    OOPS_HF_MAILING_LIST = {
        'lexi@makeitbloom.com',
        'eric@makeitbloom.com',
        'sam@makeitbloom.com'
    }
else:
    OOPS_HF_MAILING_LIST = {
        'lexi@makeitbloom.com',
        'marina@makeitbloom.com',
        'xurxo@makeitbloom.com',
        'phil@makeitbloom.com',
        'antoine@makeitbloom.com',
        'jessica@makeitbloom.com',
        'franck@makeitbloom.com',
        'mike@makeitbloom.com',
        'nick@makeitbloom.com',
        'martin@makeitbloom.com',
        'jeff@makeitbloom.com',
        'joelle@makeitbloom.com',
        'jamie@makeitbloom.com',
        'genevieve.b@makeitbloom.com',
        'doriane@makeitbloom.com',
        'avi@makeitbloom.com',
        'keith@makeitbloom.com'
    }

CELERY_RESULT_BACKEND = 'django-db'
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'UTC'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(process)d %(thread)d %(name)s:%(lineno)s %(funcName)s() %(message)s'
        },
        'verbose_sql': {
            'format': '%(levelname)s %(asctime)s %(process)d %(thread)d %(name)s:%(lineno)s %(funcName)s() %(sql)s\n%(params)s\n%(duration)ss'
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'stream': sys.stdout
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True,
            'formatters': 'verbose'
        },
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
            'formatters': 'verbose'
        },
        'django.db.backends': {
            'handlers': ['console'],
            'level': 'WARNING',
            'propagate': False,
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'DEBUG',
    }
}

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.TokenAuthentication',
        # 'rest_framework.authentication.SessionAuthentication',
        'rest_framework_simplejwt.authentication.JWTAuthentication',

    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    )

}

CORS_ORIGIN_ALLOW_ALL = True

# might need to be changed in staging/prod
MEDIA_ROOT = os.path.join(BASE_DIR, 'media/img/')
MEDIA_URL = '/media/img/'
