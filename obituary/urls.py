from django.conf.urls.defaults import *
from obituary.views import deaths, fh_index, logout_view, manage_death_notice, \
    manage_obituary

urlpatterns = patterns('',
    url(r'^deaths/(?P<death_notice_id>\d+)/$', manage_death_notice, name='manage_death_notice'),
    url(r'^deaths/$', manage_death_notice, name='add_death_notice'),
    url(r'^obituaries/$', manage_obituary, name='add_obituary'),
    url(r'^funeral-home/$', fh_index, name='death_notice_index'),
    url(r'^logout/$', logout_view, name='logout'),
    (r'^deaths/print/$', deaths, {'model': 'Death_notice'},),
    (r'^obits/print/$', deaths, {'model': 'Obituary'},),
)