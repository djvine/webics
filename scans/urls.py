from django.conf.urls import patterns, url

from scans import views

urlpatterns = patterns('',
    # ex: /scans/
    url(r'^$', views.index, name='index'),
    # ex: /scans/2-ID-B/
    url(r'^(?P<beamline>.+\\)/$', views.plots, name='plots'),
    # ex: /scans/2-ID-B/plots/
    url(r'^(?P<beamline>.+\\)/plots/$', views.plots, name='plots'),
    # ex: /scans/2-ID-B/images/
    url(r'^(?P<question_id>.+\\)/images/$', views.images, name='images'),
)