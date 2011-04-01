import random
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.core.files.uploadedfile import SimpleUploadedFile
from django.http import HttpResponseRedirect, HttpResponseNotFound, HttpResponseForbidden, HttpResponse
from django.core.urlresolvers import reverse
from openelections import constants as oe_constants
from openelections.issues.models import Issue
from openelections.issues.forms import IssueForm, form_class_for_issue
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import AnonymousUser
from webauth.models import WebauthUser
from issues.forms import MultiCreateForm
from issues.models import Electorate

index_filters = {
    'exec': (oe_constants.ISSUE_EXEC,),
    'gsc': (oe_constants.ISSUE_GSC,),
    'senate': (oe_constants.ISSUE_US,),
    'class-presidents': (oe_constants.ISSUE_CLASSPRES,),
    
    'special-fee-requests': (oe_constants.ISSUE_SPECFEE,),
    'referendums': (oe_constants.ISSUE_REFERENDUM,),

    
    'petitioning': [oe_constants.ISSUE_EXEC,oe_constants.ISSUE_US,oe_constants.ISSUE_CLASSPRES,oe_constants.ISSUE_SPECFEE,],
    'all': [oe_constants.ISSUE_EXEC,oe_constants.ISSUE_US,oe_constants.ISSUE_CLASSPRES,oe_constants.ISSUE_SPECFEE,oe_constants.ISSUE_GSC,oe_constants.ISSUE_REFERENDUM],
    'undergrad': [oe_constants.ISSUE_EXEC,oe_constants.ISSUE_US,oe_constants.ISSUE_CLASSPRES,oe_constants.ISSUE_SPECFEE,oe_constants.ISSUE_REFERENDUM],
    'grad': [oe_constants.ISSUE_GSC,oe_constants.ISSUE_EXEC,oe_constants.ISSUE_SPECFEE,oe_constants.ISSUE_REFERENDUM]
}

def index(request, show=None):
    issues = None
    if show:
        kind_filter = index_filters.get(show, None)
        if kind_filter is None:
            return HttpResponseNotFound()
        issues = Issue.filter_by_kinds(kind_filter).filter(public=True).all()
    else:
        return render_to_response('issues/welcome.html', context_instance=RequestContext(request))

    issues = map(Issue.get_typed, issues)
    random.shuffle(issues)

    if show == 'grad':
        newissues = list()
        for i in issues:
            if i.kind == oe_constants.ISSUE_SPECFEE and i.is_grad_issue() == False:
                continue
            newissues.append(i)
        issues = newissues
    print issues

    return render_to_response('issues/index.html', {'issues': issues, 'detail': False}, context_instance=RequestContext(request))

def detail(request, issue_slug):
    issue = get_object_or_404(Issue, slug=issue_slug).get_typed()
    sunetid = ""
    if isinstance(request.user,WebauthUser):
        sunetid = request.user.webauth_username 
    can_manage = issue.sunetid_can_manage(sunetid)
    print issue.is_grad_issue()
    return render_to_response('issues/detail.html', {'issue': issue, 'can_manage': can_manage, 'detail': True}, context_instance=RequestContext(request))

@login_required
def manage_index(request):
    sunetid = request.user.webauth_username
    issues = map(Issue.get_typed, Issue.filter_by_sponsor(sunetid))
    return render_to_response('issues/manage/index.html', {'issues': issues}, context_instance=RequestContext(request))

@login_required
def manage_new(request, issue_kind):
    sunetid = request.user.webauth_username
    new_issue = Issue(kind=issue_kind, sunetid1=sunetid).get_typed()
    form = form_class_for_issue(new_issue)(instance=new_issue)
    return render_to_response('issues/manage/new.html', {'new_issue': new_issue, 'form': form}, context_instance=RequestContext(request))

@login_required
def create(request):
    sunetid = request.user.webauth_username
    attrs = request.POST.copy()
    if len(attrs) == 0 or 'kind' not in attrs:
        return HttpResponseNotFound("The form did not submit correctly. Please try again.")
    new_issue = Issue(kind=attrs['kind'], sunetid1=sunetid).get_typed()
    form = form_class_for_issue(new_issue)(attrs, instance=new_issue)
    if form.is_valid() and new_issue.can_declare():
        form.save()
        return HttpResponseRedirect(reverse('openelections.issues.views.manage_index'))
    else:
        return render_to_response('issues/manage/new.html', {'new_issue': new_issue, 'form': form}, context_instance=RequestContext(request))

@login_required
def manage_edit(request, issue_slug):
    issue = get_object_or_404(Issue, slug=issue_slug).get_typed()
    
    # only sponsors of an issue may edit it
    sunetid = request.user.webauth_username
    if not issue.sunetid_can_manage(sunetid):
        return HttpResponseForbidden()
    
    form = None
    if request.method == 'POST':
        form = form_class_for_issue(issue)(request.POST, request.FILES, instance=issue)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('openelections.issues.views.manage_edit', None, [issue.slug]))
    else:
        form = form_class_for_issue(issue)(instance=issue)
    
    return render_to_response('issues/manage/edit.html', {'issue': issue, 'form': form}, context_instance=RequestContext(request))

@permission_required('issue.create')
def admin_multicreate(request):
    form = MultiCreateForm()
    message = ""

    if request.method == 'POST':
        form = MultiCreateForm(request.POST)

    if form.is_valid():
        undergrad = Electorate.objects.filter(slug='undergrad').get()
        coterm = Electorate.objects.filter(slug='coterm').get()
        text = form.cleaned_data['text']
        lines = text.split("\n")
        for line in lines:
            (groupname,requestamt,prevrequest,sponsor,sponsoremail,perug,pergrad,contentprefix,slug) = line.split("\t",9)
            groupname = groupname.strip()
            sponsorsunet = sponsoremail.strip()
            slug = slug.strip()
            if Issue.objects.filter(slug=slug).exists():
                message += "<span style = 'color:red;'>%s already exists</span><br />" % (groupname)
                continue

            group = Issue()
            group.kind = 'SF'
            group.title = groupname
            group.slug = slug
            group.public = True

            group.petition_validated = True

            group.name1 = sponsor
            group.sunetid1 = sponsorsunet

            group.budget = 'specialfees/%s-FundingRequest.pdf' % contentprefix
            group.account_statement = 'specialfees/%s-AcctStatement.pdf' % contentprefix
            group.total_request_amount = requestamt
            group.amount_per_undergrad_annual = perug
            group.amount_per_grad_annual = pergrad
            group.total_past_request_amount = prevrequest
            group.admin_notes = "MultiCreated"
            group.save()
            group.electorates = [undergrad,coterm]
            group.save()


            message += "Added %s<br />" % (groupname)

    message += "Remember to change the details of Joint vs. UG Special Fee groups."
    return render_to_response('issues/manage/admin_multicreate.html', {'message': message, 'form': form}, context_instance=RequestContext(request))
