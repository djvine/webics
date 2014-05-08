"""Development settings and globals."""


from common import *
from os.path import join, normpath


########## DATABASE CONFIGURATION
DATABASES = {
    'default': {
        'ENGINE':'django.db.backends.mysql',
        'NAME': 'webics_hershel',
        'USER': 'maggie',
        'PASSWORD': 'inthepracticeoftoleranceonesenemyisthebestteacher',
        'HOST': 'localhost',
    }
}
########## END DATABASE CONFIGURATION


########## CACHE CONFIGURATION
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}
########## END CACHE CONFIGURATION

########## DJANGO-COMPRESSOR CONFIGURATION
settings.COMPRESS_ENABLED = True
########## END DJANGO_COMPRESSOR CONFIGURATION