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
import socket

hostname = socket.gethostname()

if hostname == 'lemon.xray.aps.anl.gov':
    webics_root = '/local'
elif hostname in ['david-laptop', 'david-APS']:
    webics_root = '/home/david/web/dev'
    

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
    webics_root+'/webics/webics/static',
    webics_root+'/webics/chat/static',
    webics_root+'/webics/det_buttons/static',
    webics_root+'/webics/history/static',
    webics_root+'/webics/socket_manager/static',
    webics_root+'/webics/lineplots/static',
    webics_root+'/webics/images/static',
    webics_root+'v/webics/scan_oview/static',
    webics_root+'/webics/overview/static',
)

TEMPLATE_DIRS = (
  webics_root+'/webics/webics/templates',
  webics_root+'/webics/scans/templates',
  webics_root+'/webics/chat/templates',
  webics_root+'/webics/det_buttons/templates',
  webics_root+'/webics/history/templates',
  webics_root+'/webics/lineplots/templates',
  webics_root+'/webics/images/templates',
  webics_root+'/webics/scan_oview/templates',
  webics_root+'/webics/overview/templates',
)

settings.COMPRESS_ENABLED = True