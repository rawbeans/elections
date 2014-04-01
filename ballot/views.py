from django.http import HttpResponseRedirect
from django.conf import settings
from django.template import RequestContext
from django.template.loader import render_to_string
from django.shortcuts import render_to_response, get_object_or_404
from openelections import constants as oe_constants
from issues.models import Issue, ExecutiveSlate, ClassPresidentSlate
from ballot.forms import ballot_form_factory, BallotElectorateForm
from ballot.models import Ballot, make_voter_id
from django.contrib.auth.decorators import login_required
from ballot.models import VoteRecord
from datetime import datetime
from django.db import transaction

def get_voter_id(request):
    return make_voter_id(request.user.webauth_username)

def make_issues_json():
    return ""

#    issues = {}
#    for o in Issue.objects.all():
#        issues[str(o.pk)] = { 'statement': render_to_string('ballot/info.html', {'issue': o.get_typed(), 'detail': True, 'hidepdfs': True}) }
#    return simplejson.dumps(issues)
# put a static JS file in hosting to avoid generation every time
    
def get_exec_slates():
    return ExecutiveSlate.objects.filter(kind='Exec').order_by('?').all()
    
def get_csac_members():
    return Issue.objects.filter(kind='SMSA-CSAC').order_by('title').all()

def get_cp_slates(ballot):
    return ClassPresidentSlate.objects.filter(kind=oe_constants.ISSUE_CLASSPRES, electorates=ballot.undergrad_class_year).order_by('?').all()


def landing(request):
    return render_to_response('ballot/welcome.html', context_instance=RequestContext(request))

def closed(request):
    return render_to_response('ballot/closed.html', context_instance=RequestContext(request))


def redirect(request):
    return HttpResponseRedirect("http://ballot.stanford.edu/ballot/")

@transaction.commit_on_success
@login_required
def index(request):
    sunetid = request.user.webauth_username
    ballot, c = Ballot.get_or_create_by_sunetid(sunetid)
    if ballot.needs_ballot_choice():
        return HttpResponseRedirect('/ballot/choose')
    
    ballotform = ballot_form_factory(ballot)(instance=ballot)

    record = VoteRecord()
    record.sunetid = sunetid
    record.ip = request.META['REMOTE_ADDR']
    record.datetime = datetime.now()
    record.type = "start"
    record.save()

    return render_to_response('ballot/ballot.html', {'ballotform': ballotform, 'ballot': ballot, 'issues_json': make_issues_json(), 'cp_slates': get_cp_slates(ballot), 'csac_members': get_csac_members(), 'exec_slates': get_exec_slates(),'sunetid': sunetid},
                              context_instance=RequestContext(request))

@transaction.commit_on_success
@login_required
def choose_ballot(request):
    sunetid = request.user.webauth_username
    print request.META
    ballot = get_object_or_404(Ballot, voter_id=get_voter_id(request))
    form = None
    if request.method == 'POST':
        form = BallotElectorateForm(request.POST, instance=ballot)
        if form.is_valid():
            form.save()
            record = VoteRecord()
            record.sunetid = sunetid
            record.ip = request.META['REMOTE_ADDR']
            record.datetime = datetime.now()
            record.type = "choose"
            record.details = "chose " + ballot.get_electorate_slugs()
            record.save()
            return HttpResponseRedirect('/ballot/')
    else:
        form = BallotElectorateForm(instance=ballot)
    return render_to_response('ballot/choose.html', {'form': form, 'ballot': ballot},
                              context_instance=RequestContext(request))

@login_required
def record(request):
    ballot = get_object_or_404(Ballot, voter_id=get_voter_id(request))
    form = BallotElectorateForm(instance=ballot)
    return render_to_response('ballot/ballot_record.txt', {'ballot': ballot, 'request': request, 'form': form},
                              mimetype='text/plain', context_instance=RequestContext(request))

@transaction.commit_on_success
@login_required
def vote_all(request):
    sunetid = request.user.webauth_username

    # protect against XSS
       
    form = None
    ballot = get_object_or_404(Ballot, voter_id=get_voter_id(request))
    if request.method == 'POST':
        ballotform = ballot_form_factory(ballot)(request.POST, instance=ballot)
        if ballotform.is_valid():
            record = VoteRecord()
            record.sunetid = sunetid
            record.ip = request.META['REMOTE_ADDR']
            record.datetime = datetime.now()
            record.type = "success-vote"
            record.save()
            ballotform.save()

            vrecord = render_to_string('ballot/ballot_record.txt', {'ballot': ballot, 'request': request, 'form': form, 'sunetid': sunetid})

            f = open(settings.BALLOT_ROOT + '/%s-%d' % (sunetid,record.pk), 'w')
            f.write(vrecord.encode('utf8'))
            f.close()
        else:
            record = VoteRecord()
            record.sunetid = sunetid
            record.ip = request.META['REMOTE_ADDR']
            record.datetime = datetime.now()
            record.type = "failed-vote"
            record.details = str(ballotform.errors)
            record.save()
            return render_to_response('ballot/ballot.html', {'ballotform': ballotform, 'ballot': ballot, 'issues_json': make_issues_json(), 'cp_slates': get_cp_slates(ballot), 'csac_members': get_csac_members(),  'exec_slates': get_exec_slates(),'is_submitted': True, 'sunetid': sunetid},
                                      context_instance=RequestContext(request))
    
    #WebauthLogout(request) # not necessary.
    return render_to_response('ballot/done.html', {'sunetid': sunetid, 'ballot': ballot, 'request': request,}, context_instance=RequestContext(request))
