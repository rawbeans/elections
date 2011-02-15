import random
from datetime import datetime
from django.http import HttpResponseRedirect, QueryDict
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.core.urlresolvers import reverse
from openelections.petitions.models import Signature
from openelections.petitions.forms import SignatureForm
from openelections.issues.models import Issue
from django.contrib.auth.decorators import login_required

def index(request):
    return HttpResponseRedirect('/issues/petitioning')

@login_required
def detail(request, issue_slug):
    issue = get_object_or_404(Issue, slug=issue_slug).get_typed()
    
    sunetid = request.user.webauth_username
    can_manage = issue.sunetid_can_manage(sunetid)
    
    signatures = None
    signatures = Signature.objects.filter(issue=issue).order_by('-id') #signatures are public
    newsig = Signature()
    newsig.issue = issue
    newsig.sunetid = sunetid
    form = None
    if not issue.signed_by_sunetid(sunetid):
        form = SignatureForm(issue, instance=newsig)
    return render_to_response('petitions/detail.html', {
        'issue': issue,
        'form': form,
        'can_manage': can_manage,
        'signatures': signatures,
    }, context_instance=RequestContext(request))

@login_required
def sign(request, issue_slug):
    issue = get_object_or_404(Issue, slug=issue_slug).get_typed()
    
    if request.method != 'POST':
        return HttpResponseRedirect(reverse('openelections.petitions.views.detail', None, [issue_slug]))
    
    sunetid = request.user.webauth_username
    attrs = request.POST.copy()
    attrs['sunetid'] = sunetid
    attrs['issue'] = issue.id
    attrs['ip_address'] = request.META['REMOTE_ADDR']
    attrs['signed_at'] = datetime.now()
    form = SignatureForm(issue, attrs)
    if form.is_valid():
        form.save()
        return HttpResponseRedirect(reverse('openelections.petitions.views.detail', None, [issue_slug])+'#sign-form')
    else:
        return render_to_response('petitions/detail.html',
                                  {
                                    'issue': issue, 
                                    'form': form, 
                                    'jumptosign':True
                                  }, context_instance=RequestContext(request))
