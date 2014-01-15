from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'webics.views.home', name='home'),
    url(r'^scans/', include('scans.urls')),
    url(r'^admin/', include(admin.site.urls)),
)