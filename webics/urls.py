from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

import overview.views

urlpatterns = patterns('',
    # Examples:
    url(r'^$', 'overview.views.overview', name='overview'),
    url(r'^scans/', include('scans.urls', namespace='scans')),
    url(r'^admin/', include(admin.site.urls)),
)
