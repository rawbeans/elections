from django.conf.urls.defaults import *

urlpatterns = patterns('openelections.ballot_admin.views',
(r'^stats$', 'admin_stats'),
(r'^winners$', 'admin_winners'),
(r'^studentcheck$', 'admin_studentcheck'),

(r'^delballots$', 'admin_del_ballots'),
(r'^breakdown$', 'admin_breakdown'),
                       )