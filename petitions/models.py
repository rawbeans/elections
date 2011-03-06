from datetime import datetime
from django.db import models
from openelections.issues.models import Electorate, Issue, SenateCandidate
from webauth.models import WebauthUser
from django.contrib.auth.models import User

class Signature(models.Model):
    name = models.CharField(max_length=100)
    sunetid = models.CharField(max_length=8)
    electorate = models.ForeignKey(Electorate)    
    issue = models.ForeignKey(Issue, related_name='signatures')
    signed_at = models.DateTimeField(default=datetime.now)
    ip_address = models.CharField(max_length=15)
    
    def __unicode__(self):
        return u'%s for %s' % (self.sunetid, self.issue.title)

def signed_by_sunetid(issue, sunetid):
    return Signature.objects.filter(sunetid=sunetid, issue=issue)
Issue.signed_by_sunetid = signed_by_sunetid

class PaperSignature(models.Model):
    sunetid = models.CharField(max_length=8)
    issue = models.ForeignKey(Issue)
    entered_by = models.ForeignKey(User)

    def __unicode__(self):
        return self.sunetid