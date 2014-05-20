"""Development settings and globals."""


from common import *
from os.path import join, normpath

SERVER_EMAIL = 'dvine@anl.gov'

########## DATABASE CONFIGURATION
DATABASES = {
    'default': {
        'ENGINE':'django.db.backends.mysql',
        'NAME': 'webics_hershel',
        'USER': 'maggie',
        'PASSWORD': 'inthepracticeoftoleranceonesenemyisthebestteacher',
        'HOST': 'joule.xray.aps.anl.gov',
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
COMPRESS_ENABLED = False
########## END DJANGO_COMPRESSOR CONFIGURATION

########## SOCKET.IO ENV
SOCKET_ENV = 'prod'
########## END SOCKET.IO ENV
