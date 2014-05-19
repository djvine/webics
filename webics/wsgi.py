"""
WSGI config for webics project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/howto/deployment/wsgi/
"""

import os
import sys
import socket

if socket.gethostname()=='joule-vm.xray.ps.anl.gov':
    sys.path.append('/home/beams/WEBICS/webics')
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "webics.settings.prod")

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
