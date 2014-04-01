from django.conf.urls.defaults import *

from django.contrib import admin
admin.autodiscover()
admin.site.login_template = 'webauth/admin_redirect.html'

urlpatterns = patterns('',
    #(r'^$', 'openelections.ballot.views.landing'),
    #(r'^ballot-test1234/', include('ballot.urls')),
    #(r'^$', 'ballot.views.redirect'),
    #(r'^ballot/', include('ballot.urls')),
    #(r'^ballot_admin/', include('ballot_admin.urls')),

    (r'^$','issues.views.index'),
    (r'^petitions/', include('petitions.urls')),
    (r'^issues/', include('issues.urls')),
    (r'^admin/', include(admin.site.urls)),
    (r'^webauth/', include('webauth.urls')),

    #(r'^media/(?P<path>.*)$', 'django.views.static.serve',
    #       {'document_root': 'public/media/'}),

    #(r'^view/(?P<issue_slug>[\w\d-]+)$', 'issues.views.detail'),

   (r'^accounts/login/$', 'webauth.views.login')
)
