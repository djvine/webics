"""
Django settings for webics project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
from django.conf import settings

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'c$#x%^aabbt-3#r1l_qgbs0m5m4qa$!oy3(p7^y=)kd7o4i*9k'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = ['webics.xray.aps.anl.gov']


# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'south',
    'scans',
    'chat',
    'det_buttons',
    'history',
    'socket_manager',
    'lineplots',
    'images',
    'scan_oview',
    'overview',
    'compressor',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'webics.urls'

WSGI_APPLICATION = 'webics.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE':'django.db.backends.mysql',
        'NAME': 'webics_hershel',
        'USER': 'maggie',
        'PASSWORD': 'inthepracticeoftoleranceonesenemyisthebestteacher',
        'HOST': 'localhost',
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'America/Chicago'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/
STATIC_ROOT =  os.path.join(BASE_DIR, "static")
STATIC_URL = '/static/'

STATICFILES_DIRS = (
    '/home/david/web/dev/webics/webics/static',
    '/home/david/web/dev/webics/chat/static',
    '/home/david/web/dev/webics/det_buttons/static',
    '/home/david/web/dev/webics/history/static',
    '/home/david/web/dev/webics/socket_manager/static',
    '/home/david/web/dev/webics/lineplots/static',
    '/home/david/web/dev/webics/images/static',
    '/home/david/web/dev/webics/scan_oview/static',
    '/home/david/web/dev/webics/overview/static',
)

TEMPLATE_DIRS = (
  '/home/david/web/dev/webics/webics/templates',
  '/home/david/web/dev/webics/scans/templates',
  '/home/david/web/dev/webics/chat/templates',
  '/home/david/web/dev/webics/det_buttons/templates',
  '/home/david/web/dev/webics/history/templates',
  '/home/david/web/dev/webics/lineplots/templates',
  '/home/david/web/dev/webics/images/templates',
  '/home/david/web/dev/webics/scan_oview/templates',
  '/home/david/web/dev/webics/overview/templates',
)

settings.COMPRESS_ENABLED = True