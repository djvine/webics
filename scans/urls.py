from django.conf.urls import patterns, url

from scans import views

#Regex named pattern (?P<name>pattern)

urlpatterns = patterns('',
    # ex: /scans/
    url(r'^$', views.main, name='main'),
    # ex: /scans/2-ID-B/plots/
    url(r'^(?P<beamline>.*?)/plots/$', views.plots, name='plots'),
    # ex: /scans/2-ID-B/images/
    url(r'^(?P<beamline>.*?)/images/$', views.images, name='images'),
)