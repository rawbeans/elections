from django.conf.urls.defaults import *

urlpatterns = patterns('openelections.ballot.views',
    (r'^$', 'index'),
    (r'^vote$', 'vote_all'),
    (r'^choose$', 'choose_ballot'),
    (r'^record$', 'record'),

#    (r'^$', 'closed'),
#    (r'^vote$', 'closed'),
#    (r'^choose$', 'closed'),
#    (r'^record$', 'closed'),

)