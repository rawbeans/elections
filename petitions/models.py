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

SIGNATURE_TYPES = ('online','paper')

class ValidationResult(models.Model):
    key = models.CharField(max_length=64)
    sunetid = models.CharField(max_length=8)
    issue = models.ForeignKey(Issue)
    location = models.CharField(max_length=6)
    sent = models.BooleanField()
    started = models.BooleanField()
    completed = models.BooleanField()
    class_petition = models.BooleanField()
    did_sign = models.BooleanField()
    undergraduate = models.BooleanField()
    provided_name = models.CharField(max_length=100,blank=True)
    extra = models.TextField(blank=True)

    def __unicode__(self):
        return "%s (%s)" % (self.key,self.sunetid)

    # note: will need to hand-count any Joint Special Fee groups, which can be signed by both
    # grads and undergrads.
    def is_valid(self):
        return (self.did_sign and self.undergraduate and not self.class_petition)