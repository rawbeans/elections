import random
from datetime import datetime
from django.http import HttpResponseRedirect, QueryDict, HttpResponse
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.core.urlresolvers import reverse
from openelections.petitions.models import Signature
from openelections.petitions.forms import SignatureForm
from openelections.issues.models import Issue
from django.contrib.auth.decorators import login_required, permission_required
from petitions.models import PaperSignature

def index(request):
    return HttpResponseRedirect('/issues/petitioning')

@login_required
def detail(request, issue_slug):
    issue = get_object_or_404(Issue, slug=issue_slug).get_typed()
    
    sunetid = request.user.webauth_username
    can_manage = issue.sunetid_can_manage(sunetid)
    
    signatures = Signature.objects.filter(issue=issue).order_by('-id') #signatures are public
    newsig = Signature()
    newsig.issue = issue
    newsig.sunetid = sunetid
    form = None
    if not issue.signed_by_sunetid(sunetid) and issue.petition_open():
        form = SignatureForm(issue, instance=newsig)
    return render_to_response('petitions/detail.html', {
        'issue': issue,
        'form': form,
        'can_manage': can_manage,
        'signatures': signatures,
        'sunetid': sunetid
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
    if form.is_valid() and issue.petition_open():
        form.save()
        return HttpResponseRedirect(reverse('openelections.petitions.views.detail', None, [issue_slug])+'#sign-form')
    else:
        return render_to_response('petitions/detail.html',
                                  {
                                    'issue': issue, 
                                    'form': form, 
                                    'jumptosign':True
                                  }, context_instance=RequestContext(request))

def api_count(request, issue_slug):
    issue = get_object_or_404(Issue, slug=issue_slug).get_typed()
    sig_count = Signature.objects.filter(issue=issue).count()
    response = HttpResponse(sig_count)
    response['Access-Control-Allow-Origin'] = '*'
    return response

@permission_required('signature.can_add')
def add_signatures(request,issue_slug):
    issue = get_object_or_404(Issue,slug=issue_slug).get_typed()

    if request.method != "POST":
        return render_to_response('petitions/admin_entersig.html',
                                    {'issue': issue,
                                  }, context_instance=RequestContext(request))

    signatures = request.POST.getlist('suid')
    responsetext = ""
    num_added = 0
    for signature in signatures:
        if signature is not None and signature != "":
            papersig = PaperSignature()
            papersig.sunetid = signature
            papersig.entered_by = request.user
            papersig.issue = issue
            papersig.save()
            responsetext += "Entered '%s'<br /> " % signature
            num_added += 1
    return render_to_response('petitions/admin_entersig.html',
                                    {'issue': issue, 'responsetext': responsetext, 'num_added': num_added
                                  }, context_instance=RequestContext(request))

@permission_required('signature.can_add')
def view_signatures(request,issue_slug):
    issue = get_object_or_404(Issue,slug=issue_slug).get_typed()
    signatures = issue.papersignature_set.all()

    considered_set = set()
    problem_set = (list(),list(),list()) # 0 = duplicate online, 1 = duplicate on paper, 2 = clean
    for signature in signatures:
        if signature.sunetid in considered_set:
            problem_set[1].append(signature)
            continue

        if Signature.objects.filter(sunetid=signature.sunetid).count() > 0:
            problem_set[0].append(signature)
        else:
            problem_set[2].append(signature)
        considered_set.add(signature.sunetid)
        

    return render_to_response('petitions/admin_viewsig.html',
                                    {'issue': issue,
                                     'problem_set': problem_set,
                                     'considered': considered_set,
                                     'total': len(signatures)
                                  }, context_instance=RequestContext(request))

