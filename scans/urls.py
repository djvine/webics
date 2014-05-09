from django.conf.urls import patterns, url

import scans
import lineplots
import images
import scan_oview
from scans import views
from lineplots import views
from images import views
from scan_oview import views

#Regex named pattern (?P<name>pattern)

urlpatterns = patterns('',
    # ex: /scans/2-ID-B/overview
    url(r'^(?P<beamline>.*?)/overview/$', scan_oview.views.scan_oview, name='oview'),
    # ex: /scans/2-ID-B/plots/
    url(r'^(?P<beamline>.*?)/plots/$', lineplots.views.lineplots, name='plots'),
    # ex: /scans/2-ID-B/images/
    url(r'^(?P<beamline>.*?)/images/$', images.views.images, name='images'),
)
