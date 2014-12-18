"""Development settings and globals."""


from common import *
from os.path import join, normpath


########## DEBUG CONFIGURATION
DEBUG = True
TEMPLATE_DEBUG = DEBUG
########## END DEBUG CONFIGURATION


########## EMAIL CONFIGURATION
EMAIL_BACKEND = 'django.core.mail.backends.dummy.EmailBackend'
########## END EMAIL CONFIGURATION


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


########## DJANGO-DEBUG-TOOLBAR CONFIGURATION
MIDDLEWARE_CLASSES += (
    #'debug_toolbar.middleware.DebugToolbarMiddleware',
)

INSTALLED_APPS += (
    #'debug_toolbar',
)

# IPs allowed to see django-debug-toolbar output.
INTERNAL_IPS = ('127.0.0.1',)

########## SOCKET.IO ENV
SOCKET_ENV = 'dev'
########## END SOCKET.IO ENV
