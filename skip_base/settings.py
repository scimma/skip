"""
Django settings for skip_base project.

Generated by 'django-admin startproject' using Django 3.0.5.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.0/ref/settings/
"""

import boto3
import logging.config
import os

# Logging

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        }
    },
    'loggers': {
        '': {
            'handlers': ['console'],
            'level': 'INFO'
        }
    }
}
logging.config.dictConfig(LOGGING)
logger = logging.getLogger(__name__)

logger.warn('you have reached the settings, this is a logging test')


def get_secret(secret_name):
    try:
        secrets_manager = boto3.client('secretsmanager', region_name='us-west-2')
        return secrets_manager.get_secret_value(SecretId=secret_name)['SecretString']
    except Exception as e:
        logger.error(f'Unable to get secret {secret_name}: {e}')
        # Not re-raising the exception so that collectstatic and other management commands can succeed


# def get_rds_db(db_instance_id):
#     try:
#         rds = boto3.client('rds', region_name='us-west-2')
#         resp = rds.describe_db_instances(Filters=[
#             {'Name': 'db-instance-id', 'Values': [db_instance_id]},
#         ])
#         return resp['DBInstances'][0]
#     except Exception as e:
#         logger.error(f'Unable to get RDS DB {db_instance_id}: {e}')


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 't8oh)-ej%uc!&!p&0ugyy8oxgu3=w(yy$68++hc7we#g@j7m+c'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = [
    'whitenoise.runserver_nostatic',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework.authtoken',
    'corsheaders',
    'django_extensions',
    'django_filters',
    'webpack_loader',
    'skip',
    'django.contrib.postgres',
    # 'skip_dpd',
    # 'django_plotly_dash.apps.DjangoPlotlyDashConfig',
    'bootstrap4',
    'alert_scraper'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'skip_base.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
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

WSGI_APPLICATION = 'skip_base.wsgi.application'

CORS_ORIGIN_ALLOW_ALL = True


# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases
# This is here to debug kubernetes secrets for eventual move to kubernetes
for key in ['HOPSKOTCH_PASSWORD', 'DB_NAME', 'DB_USERNAME', 'DB_PASSWORD', 'DB_HOST', 'DB_PORT']:
    print(f'{key}: {os.getenv(key, "")}')
DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': os.getenv('DB_NAME', 'skip_db'),
        'USER': os.getenv('DB_USERNAME', 'skip'),
        'PASSWORD': os.getenv('DB_PASSWORD', get_secret('skip-db-password-5')),
        'HOST': os.getenv('DB_HOST', 'skip-postgres.cgaf3c8se1sj.us-west-2.rds.amazonaws.com'),
        'PORT': os.getenv('DB_PORT', '5432'),
    }
}

DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, '_static')
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]

STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',

    # 'django_plotly_dash.finders.DashAssetFinder',
    # 'django_plotly_dash.finders.DashComponentFinder',
    # 'django_plotly_dash.finders.DashAppDirectoryFinder',
]

# Vue and django-webpack-loader/webpack-bundle-tracker configuration
VUE_FRONTEND_DIR = os.path.join(BASE_DIR, 'vue')
WEBPACK_LOADER = {
    'DEFAULT': {
        'CACHE': not DEBUG,
        'BUNDLE_DIR_NAME': 'vue/',  # must end with slash
        'STATS_FILE': os.path.join(VUE_FRONTEND_DIR, 'webpack-stats.json'),
        'POLL_INTERVAL': 0.1,
        'TIMEOUT': None,
        'IGNORE': [r'.+\.hot-update.js', r'.+\.map']
    }
}

# Django REST Framework configuration

REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'skip.pagination.SkipPagination',
    'DEFAULT_VERSIONING_CLASS': 'rest_framework.versioning.NamespaceVersioning',
    'DEFAULT_VERSION': 'v2',
    'PAGE_SIZE': 10,
    'DEFAULT_FILTER_BACKENDS': ['django_filters.rest_framework.DjangoFilterBackend'],
    'DEFAULT_AUTHENTICATION_CLASSES': (
        # TODO: BasicAuthentication has not been included--it may need to be included for running tests
        # TODO: TokenAuthentication may need to be restricted for certain views, and same for SessionAuthentication
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    )
}

# Hopskotch Consumer Configuration

HOPSKOTCH_SERVER = os.getenv('HOPSKOTCH_SERVER', 'dev.hop.scimma.org')
HOPSKOTCH_PORT = os.getenv('HOPSKOTCH_PORT', '9092')
HOPSKOTCH_CONSUMER_POLLING_TIMEOUT = 10

HOPSKOTCH_CONSUMER_CONFIGURATION = {
    'bootstrap.servers': f'{HOPSKOTCH_SERVER}:{HOPSKOTCH_PORT}',
    'group.id': os.getenv('HOPSKOTCH_GROUP', 'dcollom-a5c1897c-test'),  # group.id must be prefix with credential name
    'auto.offset.reset': 'latest',
    'security.protocol': 'sasl_ssl',
    'sasl.mechanism': 'SCRAM-SHA-512',
    'sasl.username': 'dcollom-a5c1897c',
    'sasl.password': os.getenv('HOPSKOTCH_PASSWORD', ''),

    # system dependency: ssl.ca.location may need to be set
    # this does not seem to be necessary on Ubuntu. However,
    # for example on centos7: 'ssl.ca.location': '/etc/ssl/certs/ca-bundle.crt',
}

HOPSKOTCH_TOPICS = [  # Topics that the ingesting consumer reads from
    'gcn',
    'gcn-circular',
    'lvc.gcn-test',
    'lvc.gcn-circular-test',
    'lvc.lvc-counterpart',
    'TOMToolkit.test'
]

HOPSKOTCH_PARSERS = {  # keys are valid hopskotch topics, values are lists of parsers in order of precedence
    'gcn': ['skip.parsers.gcn_lvc_notice_plaintext_parser.GCNLVCNoticeParser'],
    'gcn-circular': ['skip.parsers.gcn_circular_parser.GCNCircularParser'],
    'lvc.gcn-test': ['skip.parsers.gcn_lvc_notice_plaintext_parser.GCNLVCNoticeParser'],
    'lvc.gcn-circular-test': ['skip.parsers.gcn_circular_parser.GCNCircularParser'],
    'lvc.lvc-counterpart': ['skip.parsers.gcn_lvc_counterpart_notice_parser.GCNLVCCounterpartNoticeParser',
                            'skip.parsers.custom_format_parser.CustomFormatParser'],
    # 'tomtoolkit-test': ['skip.parsers.tomtoolkit_parser.TOMToolkitParser'],
    'default': ['skip.parsers.base_parser.DefaultParser']
}

SKIP_CLIENT = 'skip.skip_client.SkipORMClient'
DEFAULT_PAGE_SIZE = 20
SKIP_API_KEY = os.getenv('SKIP_API_KEY', '')
X_FRAME_OPTIONS = 'SAMEORIGIN'

# PLOTLY_COMPONENTS = [
#     # Common components
#     'dash_core_components',
#     'dash_html_components',
#     'dash_renderer',

#     # django-plotly-dash components
#     'dpd_components',
#     # static support if serving local assets
#     'dpd_static_support',

#     # Other components, as needed
#     'dash_bootstrap_components',
#     'dash_table'
# ]


try:
    from local_settings import *  # noqa
except ImportError:
    pass
