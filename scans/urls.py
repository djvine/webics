from django.conf.urls import patterns, url

import scans.views
import lineplots.views

#Regex named pattern (?P<name>pattern)

urlpatterns = patterns('',
    # ex: /scans/
    url(r'^$', scans.views.ScansListView.as_view(), name='scans-list'),
    # ex: /scans/2-ID-B/plots/
    url(r'^(?P<beamline>.*?)/plots/$', lineplots.views.lineplots, name='plots'),
    # ex: /scans/2-ID-B/images/
    url(r'^(?P<beamline>.*?)/images/$', scans.views.images, name='images'),
)