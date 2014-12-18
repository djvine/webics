import django.contrib.auth.views
from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

import overview.views

urlpatterns = patterns('',
    # Examples:
    url(r'^$', 'overview.views.overview', name='overview'),
    url(r'^scans/', include('scans.urls', namespace='scans')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^login/', django.contrib.auth.views.login),
    url(r'^logout/', django.contrib.auth.views.logout),
)
