from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^$', 'webics.views.home', name='home'),
    url(r'^scans/', include('scans.urls', namespace='scans')),
    url(r'^test_chat/', 'chat.views.chat'),
    url(r'^test_det_buttons/', 'det_buttons.views.det_buttons'),
    url(r'^test_history/', 'history.views.history'),
    url(r'^test_lineplots/', 'lineplots.views.lineplots'),
    url(r'^admin/', include(admin.site.urls)),
)