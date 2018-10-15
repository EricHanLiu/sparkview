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
DEBUG = True

SITE_ID=1

ALLOWED_HOSTS = [
    '35.203.133.58',
    '127.0.0.1',
    'localhost',
    'app.mibhub.com',
]
ADMINS = [('Octavian','octavian@hdigital.io')]
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
    'social_django',
    'django_crontab',
    'django_extensions',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
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
]

AUTHENTICATION_BACKENDS = (
    'social_core.backends.google.GoogleOAuth2',
    'django.contrib.auth.backends.ModelBackend')

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
SOCIAL_AUTH_GOOGLE_OAUTH2_WHITELISTED_DOMAINS = ['makeitbloom.com', 'hdigital.io']
SOCIAL_AUTH_RAISE_EXCEPTIONS = False
SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = '967183304564-54i17l22sad6f9dt28eos6bjaohf1frh.apps.googleusercontent.com'
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = 'AFQ5EqzWXICEFMwLfEumz9C5'

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = "/var/www/bloom/static"

STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static/')]


ADWORDS_YAML = os.path.join(BASE_DIR, 'adwords_dashboard/google_auth/googleads.yaml')
API_VERSION = 'v201802'
BING_API_VERSION = 12

LOGIN_URL = "login"
LOGIN_REDIRECT_URL = 'index'
LOGIN_ERROR_URL = 'login'
SOCIAL_AUTH_LOGIN_ERROR_URL = 'login'

ACCESS_TOKEN = 'ya29.GlsFBWxsC2vXxFe52v0roxsypsGipRsVl1yxipBvE-L1JIgT1v1zkH_Yntfg79IsbFLFeCCS8tAcMEa3YqhVHf5rWgBKo12LCRQCKxCa563tFnL1Ve_WwXGic239'

CRONJOBS = [
    ('*/5 * * * *', 'cron_clients.main', '> ' + BASE_DIR + '/logs/clients_budgets.log'),
    ('55 4 1 * *', 'cron_last_month.main', '> ' + BASE_DIR + '/logs/last_month.log'),
    ('00 13 15 * *', 'cron_no_changes.main', '> ' + BASE_DIR + '/logs/cron_no_changes_15.log'),
    ('00 13 30 * *', 'cron_no_changes.main', '> ' + BASE_DIR + '/logs/cron_no_changes_30.log'),
    ('0 8 * * *', 'cron_accounts.main', '> ' + BASE_DIR + '/logs/accounts.log'),
    ('0 8 * * *', 'bing_accounts.main', '> ' + BASE_DIR + '/logs/bing_accounts.log'),
    ('0 8 * * *', 'facebook_accounts.main', '> ' + BASE_DIR + '/logs/facebook_accounts.log'),
    ('5 8 * * *', 'cron_labels.main', '> ' + BASE_DIR + '/logs/labels.log'),
    ('30 8 * * *', 'cron_campaigns.main', '> ' + BASE_DIR + '/logs/aw_campaigns.log'),
    ('30 8 * * *', 'bing_campaigns.main', '> ' + BASE_DIR + '/logs/bing_campaigns.log'),
    ('30 8 * * *', 'facebook_campaigns.main', '> ' + BASE_DIR + '/logs/facebook_campaigns.log'),
    ('30 9 * * *', 'cron_alerts.main', '> ' + BASE_DIR + '/logs/alerts.log'),
    ('30 9 * * *', 'bing_alerts.main', '> ' + BASE_DIR + '/logs/bing_alerts.log'),
    ('30 9 * * *', 'facebook_alerts.main', '> ' + BASE_DIR + '/logs/facebook_alerts.log'),
    ('00 12 * * *', 'cron_budgets.main', '> ' + BASE_DIR + '/logs/budgets.log'),
    ('00 12 * * *', 'cron_ovu.main', '> ' + BASE_DIR + '/logs/ovu.log'),
    ('00 12 * * *', 'bing_ovu.main', '> ' + BASE_DIR + '/logs/bing_ovu.log'),
    ('00 12 * * *', 'facebook_ovu.main', '> ' + BASE_DIR + '/logs/facebook_ovu.log'),
    ('00 12 * * *', 'cron_account_changes.main', '> ' + BASE_DIR + '/logs/cron_account_changes.log'),
    ('10 12 * * *', 'cron_ch_mail.main', '> ' + BASE_DIR + '/logs/cron_changes_mail.log'),
    ('15 12 * * *', 'cron_adgroups.main', '> ' + BASE_DIR + '/logs/adwords_adgroups.log'),
    ('20 12 * * *', 'cron_anomalies.main', '> ' + BASE_DIR + '/logs/anomalies.log'),
    ('30 12 * * *', 'bing_anomalies.main', '> ' + BASE_DIR + '/logs/bing_anomalies.log'),
    ('30 12 * * *', 'facebook_anomalies.main', '> ' + BASE_DIR + '/logs/facebook_anomalies.log'),
    ('45 12 * * *', 'cron_flight_dates.main', '> ' + BASE_DIR + '/logs/aw_flight_dates.log'),
    ('45 12 * * *', 'bing_flight_dates.main', '> ' + BASE_DIR + '/logs/bing_flight_dates.log'),
    ('45 12 * * *', 'facebook_flight_dates.main', '> ' + BASE_DIR + '/logs/fb_flight_dates.log'),
    ('*/5 * * * *', 'cron_clients.main', '> ' + BASE_DIR + '/logs/client_spend.log'),
    ('30 12 * * *', 'cron_budget_alert.main', '> ' + BASE_DIR + '/logs/budget_breakfast.log'),
    ('00 13 * * *', 'cron_trends.main', '> ' + BASE_DIR + '/logs/trends_report.log'),
    ('00 13 * * *', 'bing_trends.main', '> ' + BASE_DIR + '/logs/bing_trends_report.log'),
    ('05 13 * * *', 'cron_qualityscore.main', '> ' + BASE_DIR + '/logs/cron_qualityscore_report.log'),
    ('10 13 * * *', 'cron_accounts_not_running.main', '> ' + BASE_DIR + '/logs/cron_not_running.log'),
    ('25 13 * * *', 'bing_qualityscore.main', '> ' + BASE_DIR + '/logs/bing_qualityscore_report.log'),
    ('25 13 * * *', 'bing_accounts_not_running.main', '> ' + BASE_DIR + '/logs/bing_not_running.log'),
    ('35 13 * * *', 'cron_extensions.main', '> ' + BASE_DIR + '/logs/cron_extensions.log'),
    ('40 13 * * *', 'cron_nlc_am.main', '> ' + BASE_DIR + '/logs/cron_nlc_am.log'),
    ('50 13 * * *', 'cron_wasted_spend.main', '> ' + BASE_DIR + '/logs/cron_wasted_spend.log'),
    ('00 14 * * *', 'bing_wasted_spend.main', '> ' + BASE_DIR + '/logs/bing_wasted_spend.log'),
    ('10 14 * * *', 'cron_kw_wastage.main', '> ' + BASE_DIR + '/logs/cron_kw_wastage.log'),
    ('10 14 * * *', 'bing_kw_wastage.main', '> ' + BASE_DIR + '/logs/bing_kw_wastage.log'),
]

# Bing Stuff

if DEBUG:
    REDIRECT_URI = "http://localhost:8000/dashboards/bing/auth/exchange"
else:
    REDIRECT_URI = "https://app.mibhub.com/dashboards/bing/auth/exchange"

# Bing Auth
CLIENT_ID = "b154faf8-2248-4eb5-83fe-f1897ef45cb7"
CLIENT_SECRET = "hspjJNTY4]-udkLBM3045*~"
DEVELOPER_TOKEN = "1215QQ0H16176244"
DEVELOPER_TOKEN_SANDBOX = "BBD37VB98"
ENVIRONMENT = "production"
BINGADS_REPORTS = os.path.join(BASE_DIR, 'bing_reports/')

# Facebook Auth

bloomworker='100025980313978'
app_id = '582921108716849'
business_id = '10154654586810511'
app_secret = '17bc991966f6895650068fe41bc87aa0'
# access_token = "EAAISKeWdZCTEBABaA5WtXSNP3vOGxEAFx2MBjKWGV6nfpOVxcMoHtTuqeyGx47rkDXJWErA4SPI1ikCHIKLOmorHpqHkNKxuEuSudMtjPdiLGV6MZArB4HRJPhDlpHmq53qrqarZBPMyClGOkhOMBGZBYmQUQXGX6pEFlHaO2gZDZD"
access_token = "EAAISKeWdZCTEBAGyyF5cheVZAGbr546TflaDJ4BhThFKigmetLZAW3SB0YHIGoZAoGGI0wZAYlPZBvV2hHUv6wtO8gD3is8eQGNIqKZAyBkVO5H8FnCTG6lRvV4TSLDpovlAgUrCYqA34I5zWBHrlOKALg8vo8dBqAZD"
w_access_token = "EAAISKeWdZCTEBANbBD1ZA4igkrUYzdacd02E0IggsEfbrKvwvMZBlXvdZCPOgwEycpHTnrmsZCkFFNG7ehPDeo8Ez3PXQlMi6Kz3QWwhMFdqBMXKZCMZAvrAeOIExRdnw0tUNo4VVphEPhRhlD7epvYiwny80W6HlrZCccAXC3cDJduysrZBdmZBMU"
# E-mail settings
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST='smtp.gmail.com'
EMAIL_HOST_USER = 'dev@makeitbloom.com'
EMAIL_HOST_PASSWORD = 'ujfgvsieuwptnrgp'
EMAIL_PORT=587
EMAIL_USE_TLS = True
DEFAULT_EMAIL_FROM = 'dev@makeitbloom.com'

if DEBUG:
    MAIL_ADS = ['octavian@hdigital.io']
else:
    MAIL_ADS = [
        'xurxo@makeitbloom.com',
        'jeff@makeitbloom.com',
        'franck@makeitbloom.com',
        'marina@makeitbloom.com',
        'lexi@makeitbloom.com',
        'octavian@hdigital.io',
]
