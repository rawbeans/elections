from collections import defaultdict
import csv
from datetime import datetime
import os
from django.conf import settings
from django.contrib.auth.decorators import permission_required
from django.db import connection
from django.shortcuts import render_to_response
from django.template.context import RequestContext
import markdown
from ballot.models import VoteRecord, Ballot
from issues.models import Electorate, SenateCandidate, SpecialFeeRequest, GSCCandidate, Issue
from openelections import constants as oe_constants

@permission_required('ballot_add')
def admin_stats(request):
    started_records = VoteRecord.objects.filter(type='start')
    finished_records = VoteRecord.objects.filter(type='success-vote')
    failed_records = VoteRecord.objects.filter(type='failed-vote')

    sunets_started = defaultdict(int)
    sunets_finished = defaultdict(int)
    sunets_failed = defaultdict(int)

    for record in started_records:
        sunets_started[record.sunetid] += 1

    for record in finished_records:
        sunets_finished[record.sunetid] += 1

    for record in failed_records:
        sunets_failed[record.sunetid] += 1

    started_set = set(sunets_started.keys())
    failed_set = set(sunets_failed.keys())
    finished_set = set(sunets_finished.keys())

    unfinished = started_set - finished_set
    only_start = started_set - finished_set - failed_set
    only_finish = finished_set - started_set

    num_submitted = len(finished_set)
    num_marked_submitted = Ballot.objects.filter(submitted=True).count()

    start_order = sorted(sunets_started, key=sunets_started.get)
    numsubmissions_order = sorted(sunets_finished, key=sunets_finished.get)

    submitted_counts = []
    for submitted in numsubmissions_order:
        submitted_counts.append((submitted,sunets_finished[submitted]))

    slugs = ['undergrad','graduate','undergrad-2','undergrad-3','undergrad-4','undergrad-5plus',
             'gsc-gsb', 'gsc-earthsci', 'gsc-edu', 'gsc-eng', 'gsc-hs-hum', 'gsc-hs-natsci', 'gsc-hs-socsci', 'gsc-law', 'gsc-med',]

    ug = Electorate.objects.get(slug='undergrad')
    ballotcount_ug = Ballot.objects.filter(assu_populations=ug,submitted=True).count()

    grad = Electorate.objects.get(slug='graduate')
    ballotcount_grad = Ballot.objects.filter(assu_populations=grad,submitted=True).count()

    ballotcount_coterm = Ballot.objects.filter(assu_populations=ug,submitted=True).filter(assu_populations=grad).count()

    freshmen = Electorate.objects.get(slug='undergrad-2')
    ballotcount_freshmen = Ballot.objects.filter(assu_populations=ug, undergrad_class_year=freshmen,submitted=True).count()
    sophomores = Electorate.objects.get(slug='undergrad-3')
    ballotcount_sophomores = Ballot.objects.filter(assu_populations=ug, undergrad_class_year=sophomores,submitted=True).count()
    juniors = Electorate.objects.get(slug='undergrad-4')
    ballotcount_juniors = Ballot.objects.filter(assu_populations=ug, undergrad_class_year=juniors,submitted=True).count()
    seniorsup = Electorate.objects.get(slug='undergrad-5plus')
    ballotcount_seniorsup = Ballot.objects.filter(assu_populations=ug, undergrad_class_year=seniorsup,submitted=True).count()

    vcounts = {
        'ug': ballotcount_ug,
        'grad': ballotcount_grad,
        'coterm': ballotcount_coterm,
        'freshmen': ballotcount_freshmen,
        'sophomores': ballotcount_sophomores,
        'juniors': ballotcount_juniors,
        'seniorsup': ballotcount_seniorsup,
    }

    GSC_DISTRICTS = ('gsc-atlarge', 'gsc-gsb', 'gsc-earthsci', 'gsc-edu', 'gsc-eng', 'gsc-hs-hum', 'gsc-hs-natsci', 'gsc-hs-socsci', 'gsc-law', 'gsc-med',)
    districts = []
    for district in GSC_DISTRICTS:
        electorate = Electorate.objects.get(slug=district)
        ballotcount = Ballot.objects.filter(assu_populations=grad,gsc_district=electorate,submitted=True).count()
        districts.append((electorate,ballotcount))


    return render_to_response('ballot/admin_stats.html', {
        'now': datetime.now(),
        'unfinished': unfinished,
        'only_start': only_start,
        'only_finish': only_finish,
        'num_submitted': num_submitted,
        'num_marked_submitted': num_marked_submitted,
        'start_order': start_order,
        'numsubmissions_order': submitted_counts,
        'vcounts': vcounts,
        'gsc_districts': districts
    }, context_instance=RequestContext(request))

@permission_required('ballot_add')
def admin_winners(request):
    senate_candidates = SenateCandidate.objects.filter(kind=oe_constants.ISSUE_US).filter(public=1)

    senate_votes = []
    cursor = connection.cursor()
    for candidate in senate_candidates:
        # Data retrieval operation - no commit required
        cursor.execute("SELECT COUNT(*) FROM ballot_ballot_votes_senate WHERE senatecandidate_id = %s", [candidate.pk])
        row = cursor.fetchone()
        senate_votes.append((candidate,row[0]))

    senate_votes.sort(key=lambda e:e[1],reverse=True)

    referendum = {}
    referendum['a'] = Ballot.objects.filter(vote_referendum='a').count()
    referendum['b'] = Ballot.objects.filter(vote_referendum='b').count()
    referendum['c'] = Ballot.objects.filter(vote_referendum='c').count()


    exec_candidates = SenateCandidate.objects.filter(kind=oe_constants.ISSUE_EXEC).filter(public=1)

    soph_electorate = Electorate.objects.get(slug='undergrad-2').pk
    jun_electorate = Electorate.objects.get(slug='undergrad-3').pk
    sen_electorate = Electorate.objects.get(slug='undergrad-4').pk

    sp_candidates = SenateCandidate.objects.filter(kind=oe_constants.ISSUE_CLASSPRES, electorates=soph_electorate).filter(public=1)
    jp_candidates = SenateCandidate.objects.filter(kind=oe_constants.ISSUE_CLASSPRES, electorates=jun_electorate).filter(public=1)
    senp_candidates = SenateCandidate.objects.filter(kind=oe_constants.ISSUE_CLASSPRES, electorates=sen_electorate).filter(public=1)

    exec_irv = do_irv("exec",exec_candidates)
    sp_irv = do_irv("classpres",sp_candidates)
    jp_irv = do_irv("classpres",jp_candidates)
    senp_irv = do_irv("classpres",senp_candidates)

    # exec writeins
    ballots_first_choice_exec_writeins = Ballot.objects.exclude(vote_exec1_writein='').all()
    writein_exec = []
    writein_exec_candidates = defaultdict(int)
    for ballot in ballots_first_choice_exec_writeins:
        writein_exec_candidates[ballot.vote_exec1_writein.strip()] += 1
    for execc in writein_exec_candidates:
        writein_exec.append((execc,writein_exec_candidates[execc]))
    writein_exec.sort(key=lambda e: e[1])

    # senate writeins
    ballots_senate_writeins = Ballot.objects.exclude(votes_senate_writein='').all()
    writein_senate = []
    writein_senate_candidates = defaultdict(int)
    for ballot in ballots_senate_writeins:
        writeins = markdown.re.split(r'[,\n]',ballot.votes_senate_writein)
        for writein in writeins:
            writein_senate_candidates[writein.strip()] += 1
    for execc in writein_senate_candidates:
        writein_senate.append((execc,writein_senate_candidates[execc]))
    writein_senate.sort(key=lambda e: e[1])

    # SPECIAL FEES
    num_undergrads = 6858 # includes coterms
    num_grads = 8444 # includes coterms
    num_total = 14811


    undergrad_electorate = Electorate.objects.get(slug='undergrad')
    grad_electorate = Electorate.objects.get(slug='graduate')

    ug_sfissues = SpecialFeeRequest.objects.filter(kind=oe_constants.ISSUE_SPECFEE, electorates=undergrad_electorate).filter(public=1).exclude(electorates=grad_electorate)

    sf_votes = []
    for sf in ug_sfissues:
        cursor.execute("SELECT COUNT(*) FROM ballot_ballot_votes_specfee_yes WHERE specialfeerequest_id = %s", [sf.pk])
        posvotes = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM ballot_ballot_votes_specfee_no WHERE specialfeerequest_id = %s", [sf.pk])
        negvotes = cursor.fetchone()[0]

        pct_yes = float(posvotes / (posvotes + negvotes + .00001))
        pct_yes_ug = float(posvotes / float(num_undergrads))
        approved = bool(pct_yes > .5 and pct_yes_ug > .15)
        sf_votes.append((sf,posvotes,negvotes,pct_yes,pct_yes_ug,approved))

    sf_votes.sort(key=lambda e: e[3])

    joint_sfissues = SpecialFeeRequest.objects.filter(kind=oe_constants.ISSUE_SPECFEE, electorates=grad_electorate).filter(public=1)

    joint_sf_votes = []
    for sf in joint_sfissues:
        cursor.execute("SELECT COUNT(*) FROM ballot_ballot_votes_specfee_yes AS yes INNER JOIN ballot_ballot_assu_populations AS pop ON pop.ballot_id = \
        yes.ballot_id WHERE yes.specialfeerequest_id = %s AND pop.electorate_id = %s", [sf.pk,undergrad_electorate.pk])
        posvotes_ug = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM ballot_ballot_votes_specfee_no AS yes INNER JOIN ballot_ballot_assu_populations AS pop ON pop.ballot_id = \
        yes.ballot_id WHERE yes.specialfeerequest_id = %s AND pop.electorate_id = %s", [sf.pk,undergrad_electorate.pk])
        negvotes_ug = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM ballot_ballot_votes_specfee_yes AS yes INNER JOIN ballot_ballot_assu_populations AS pop ON pop.ballot_id = \
        yes.ballot_id WHERE yes.specialfeerequest_id = %s AND pop.electorate_id = %s", [sf.pk,grad_electorate.pk])
        posvotes_g = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM ballot_ballot_votes_specfee_no AS yes INNER JOIN ballot_ballot_assu_populations AS pop ON pop.ballot_id = \
        yes.ballot_id WHERE yes.specialfeerequest_id = %s AND pop.electorate_id = %s", [sf.pk,grad_electorate.pk])
        negvotes_g = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM ballot_ballot_votes_specfee_yes AS yes INNER JOIN ballot_ballot_assu_populations AS pop ON pop.ballot_id = \
        yes.ballot_id AND pop.electorate_id = %s INNER JOIN ballot_ballot_assu_populations AS pop2 ON pop2.ballot_id = yes.ballot_id AND pop2.electorate_id = %s WHERE yes.specialfeerequest_id = %s", [grad_electorate.pk,undergrad_electorate.pk,sf.pk,])
        posvotes_ct = cursor.fetchone()[0]

        pct_yes_ug = float(posvotes_ug / (posvotes_ug + negvotes_ug + .00001))
        pct_yes_g = float(posvotes_g / (posvotes_g + negvotes_g + .00001))

        pct_yes_total = float((posvotes_ug + posvotes_g - posvotes_ct) / float(num_total))
        approved = bool(pct_yes_ug > .5 and pct_yes_g > .5 and pct_yes_total > .15)
        joint_sf_votes.append((sf,posvotes_ug,negvotes_ug,posvotes_g,negvotes_g,posvotes_ct,pct_yes_ug,pct_yes_g,pct_yes_total,approved))

    joint_sf_votes.sort(key=lambda e: e[8])

    ### GSC
    GSC_DISTRICTS = ('gsc-atlarge', 'gsc-gsb', 'gsc-earthsci', 'gsc-edu', 'gsc-eng', 'gsc-hs-hum', 'gsc-hs-natsci', 'gsc-hs-socsci', 'gsc-law', 'gsc-med',)
    district_votes = []
    for district in GSC_DISTRICTS:
        electorate = Electorate.objects.get(slug=district)
        list = {}

        # declared candidates
        if district != 'gsc-atlarge': candidates = GSCCandidate.objects.filter(kind=oe_constants.ISSUE_GSC,public=True,electorates=electorate)
        else: candidates = GSCCandidate.objects.filter(kind=oe_constants.ISSUE_GSC,public=True)
        candidates_list = {}
        if len(candidates) != 0:
            for candidate in candidates:
                if district != 'gsc-atlarge': cursor.execute("SELECT COUNT(*) FROM ballot_ballot_votes_gsc_district WHERE gsccandidate_id = %s", [candidate.pk])
                else: cursor.execute("SELECT COUNT(*) FROM ballot_ballot_votes_gsc_atlarge WHERE gsccandidate_id = %s", [candidate.pk])

                votes = cursor.fetchone()[0]
                candidates_list[candidate.title] = votes

        #non-declared candidates
        if district != 'gsc-atlarge': writein_ballots = Ballot.objects.filter(gsc_district=electorate).exclude(votes_gsc_district_writein='').filter(votes_gsc_district=None)
        else: writein_ballots = Ballot.objects.exclude(votes_gsc_atlarge_writein='')
        writein_list = defaultdict(int)
        if len(writein_ballots) != 0:
            writeins = defaultdict(int)
            for ballot in writein_ballots:
                # district
                if district != 'gsc-atlarge':
                    listed = markdown.re.split(r'[,\n]',ballot.votes_gsc_district_writein)
                    listed = listed[0:1]
                    name = listed[0].strip() + " (write-in)"
                    writein_list[name] += 1
                else:
                    remaining_slots = 5
                    remaining_slots -= len(ballot.votes_gsc_atlarge.all())
                    listed = markdown.re.split(r'[,\n]',ballot.votes_gsc_atlarge_writein)
                    listed = listed[0:remaining_slots]
                    for name in listed:
                        name = name.strip() + " (write-in)"
                        writein_list[name] += 1
        list = []
        candidatedict = dict(candidates_list.items() + writein_list.items())
        for candidate in candidatedict:
            list.append((candidate,candidatedict[candidate]))
        list.sort(key=lambda e: e[1],reverse=True)
        district_votes.append((electorate,list))

    #SMSA

    smsa_data = (
        ('vote_smsa_pres', 'SMSA-P'),
        ('vote_smsa_vpo', 'SMSA-VPO'),
        ('vote_smsa_vpa', 'SMSA-VPA'),
        ('vote_smsa_t', 'SMSA-T'),

        ('vote_smsa_ccap_pc', 'SMSA-CCAP-PC'),
        # clinical is multi
        ('vote_smsa_ccap_md', 'SMSA-CCAP-MD'),
        ('vote_smsa_ccap_yo', 'SMSA-CCAP-YO'),

        # two social chairs are multi
        ('vote_smsa_sc_yo', 'SMSA-SC-YO'),

        ('vote_smsa_mw_pc', 'SMSA-Mentorship-PC'),
        ('vote_smsa_mw_c', 'SMSA-Mentorship-C'),
        ('vote_smsa_alumni', 'SMSA-Alumni'),
        ('vote_smsa_prospective', 'SMSA-Prospective'),
        )

    smsa_result = ""
    for f_id, kind in smsa_data:
        candidates = Issue.objects.filter(kind=kind,public=True)
        smsa_result += "\n" + kind + "\n"
        for candidate in candidates:
            print f_id,kind
            cursor.execute(("SELECT COUNT(*) FROM ballot_ballot WHERE %s_id = %%s" % f_id), [candidate.pk])
            count = cursor.fetchone()[0]
            smsa_result += "%s: %s\n" % (candidate, count)

    smsa_multi_data = (
        ('votes_smsa_ccap_c', 'SMSA-CCAP-C'),
        ('votes_smsa_sc_pc', 'SMSA-SC-C'),
        ('votes_smsa_sc_c', 'SMSA-SC-PC'),
        )
    for f_id, kind in smsa_multi_data:
        candidates = Issue.objects.filter(kind=kind,public=True)
        smsa_result += "\n" + kind + "\n"
        for candidate in candidates:
            cursor.execute(("SELECT COUNT(*) FROM ballot_ballot_%s WHERE smsacandidate_id = %%s" % f_id), [candidate.pk])
            count = cursor.fetchone()[0]
            smsa_result += "%s: %s\n" % (candidate, count)



    return render_to_response('ballot/admin_winners.html', {
        'now': datetime.now(),
        'senate': senate_votes,
        'referendum': referendum,
        'exec_irv': exec_irv,
        'sp_irv': sp_irv,
        'jp_irv': jp_irv,
        'senp_irv': senp_irv,
        'exec_writeins': writein_exec,
        'senate_writeins': writein_senate,
        'ug_sf': sf_votes,
        'joint_sf': joint_sf_votes,
        'gsc': district_votes,
        'smsa': smsa_result
    }, context_instance=RequestContext(request))

def do_irv(issue_type,issues):
    issue_dict = {}
    for issue in issues:
        issue_dict[issue.pk] = issue

    result_str = ""

    issue_set = set()
    eliminated = set()
    for issue in issues:
        issue_set.add(issue.pk)
    issue_set.add('NULL')

    cursor = connection.cursor()
    querystart = "SELECT COUNT(*) FROM ballot_ballot WHERE ("
    queryelement = "vote_%s%d_id IN (%s)"
    queryelementeq = "vote_%s%d_id = %s"
    queryelementnull = "vote_%s%d_id IS NULL"
    queryend = ") AND vote_%s1_id IS NOT NULL"


    num_issues = len(issue_set)
    for round in range(1,num_issues-1):
        support = {}

        for issue in issue_set:

            #### construct query to figure out how many ballot support
            query = querystart
            for slot in range(1,round+1):
                query += "("
                for subslot in range(1,slot):
                    query += queryelement % (issue_type, subslot, ','.join(eliminated))
                    query += " AND "
                if issue != 'NULL':
                    query += queryelementeq % (issue_type,slot,issue) + ")"
                else:
                    query += queryelementnull % (issue_type,slot) + ")"

                if slot != round:
                    query += " OR "

            ### now we have support in round i
            query += queryend % issue_type
            #print query
            results = cursor.execute(query)
            support[issue] = cursor.fetchone()[0]

        ## print some stats
        result_str += "\nRound %d\n" % round
        result_str += "Ballots exhausted:\t%d\n" % support['NULL']
        del support['NULL']

        ## re-order
        supportlist = sorted(support, key=support.get)
        for item in supportlist:
            result_str += "%s:\t%d\n" % (issue_dict[item],support[item])

        eliminate = supportlist[:1]
        result_str += "Eliminated: " + str(issue_dict[eliminate[0]]) + "\n"

        issue_set = issue_set - set(eliminate)
        eliminated.add(str(eliminate[0]))

    issue_set.remove('NULL')
    issue_list = list(issue_set)
    result_str += "\nWinner is %s" % str(issue_dict[issue_list[0]])
    return result_str

def elec(slug):
    if slug is None: return None
    return Electorate.objects.get(slug=slug)

@permission_required('ballot_add')
def admin_studentcheck(request):
    assu_pops = {
        '1- Undergraduate Student': ['undergrad'],
        '2 - Coterm': ['undergrad','graduate'],
        '3 - Graduate Student': ['graduate'],
        }
    class_years = {
        '5 - Fifth year or more Senior': 'undergrad-5plus',
        '4 - Senior Class Affiliation': 'undergrad-5plus',
        '3 - Junior Class Affiliation': 'undergrad-4',
        '2 - Sophomore Class Affiliation': 'undergrad-3',
        '1 - Freshman Class Affiliation': 'undergrad-2',
        }

    students_path = os.path.join(settings.BALLOT_ROOT, '../students.csv')
    students = csv.DictReader(open(students_path,'rU'))

    studentdict = {}
    studentset = set()
    for row in students:
        sunetid = row['SUNetID']
        studentset.add(sunetid)
        groups = map(str.strip, row['Class Level'].split(','))
        pops = set()
        undergrad_class_year = None
        for g in groups:
            if g in assu_pops:
                pops.add(map(elec, assu_pops[g])[0])
            if g in class_years:
                undergrad_class_year = elec(class_years[g])
        studentdict[sunetid] = (pops,undergrad_class_year)

    all_ballots = Ballot.objects.filter(submitted=True).all()

    not_students = set()
    changed_sunetids = []
    for ballot in all_ballots:
        if ballot.voter_id not in studentset:
            not_students.add(ballot)
            continue
        for pop in ballot.assu_populations.all():
            if pop not in studentdict[ballot.voter_id][0]:
                changed_sunetids.append((ballot,"Added population: %s" % pop))
        if elec('undergrad') in ballot.assu_populations.all():
            if ballot.undergrad_class_year != studentdict[ballot.voter_id][1]:
                changed_sunetids.append((ballot, "Changed UG class year: originally %s, now %s" % (studentdict[ballot.voter_id][1],ballot.undergrad_class_year)))

    return render_to_response('ballot/admin_studentcheck.html', {
        'now': datetime.now(),
        'notstudents': not_students,
        'changed': changed_sunetids
    }, context_instance=RequestContext(request))

@permission_required('ballot_add')
def admin_del_ballots(request):
    list = [] # fill in
    ballots = Ballot.objects.filter(voter_id__in=list)

    print len(ballots)

    for ballot in ballots:
        ballot.delete()


    print "done"

@permission_required('ballot_add')
def admin_breakdown(request):
    cursor = connection.cursor()

    GSC_DISTRICTS = ('gsc-atlarge', 'gsc-gsb', 'gsc-earthsci', 'gsc-edu', 'gsc-eng', 'gsc-hs-hum', 'gsc-hs-natsci', 'gsc-hs-socsci', 'gsc-law', 'gsc-med',)
    UNDERGRAD_YEARS = ('undergrad-2','undergrad-3','undergrad-4','undergrad-5plus')
    CATEGORIES = ('undergrad','graduate')

    referendum_choices = ('a','b','c')
    results = "REFERENDUM\n"

    president_results = "PRESIDENT\n"
    prez_choices = []
    exec_candidates = SenateCandidate.objects.filter(kind=oe_constants.ISSUE_EXEC).filter(public=1)
    for candidate in exec_candidates:
        prez_choices.append((candidate.pk,candidate.slug))

    for cat in CATEGORIES:
        electorate_pk = Electorate.objects.get(slug=cat).pk
        for choice in referendum_choices:
            cursor.execute("SELECT COUNT(*) FROM ballot_ballot AS ballot INNER JOIN ballot_ballot_assu_populations AS pop ON pop.ballot_id = \
            ballot.id WHERE ballot.vote_referendum = %s AND pop.electorate_id = %s AND ballot.submitted = 1", [choice,electorate_pk])
            votes = cursor.fetchone()[0]
            results += "%s\t%s\t%d\n" % (cat,choice,votes)

        for pk,name in prez_choices:
            cursor.execute("SELECT COUNT(*) FROM ballot_ballot AS ballot INNER JOIN ballot_ballot_assu_populations AS pop ON pop.ballot_id = \
            ballot.id WHERE ballot.vote_exec1_id = %s AND pop.electorate_id = %s AND ballot.submitted = 1", [pk,electorate_pk])
            votes = cursor.fetchone()[0]
            president_results += "%s\t%s\t%d\n" % (cat,name,votes)

    for district in GSC_DISTRICTS:
        graduate_pk = Electorate.objects.get(slug='graduate').pk
        district_pk = Electorate.objects.get(slug=district).pk
        for choice in referendum_choices:
            cursor.execute("SELECT COUNT(*) FROM ballot_ballot AS ballot INNER JOIN ballot_ballot_assu_populations AS pop ON pop.ballot_id = \
            ballot.id WHERE ballot.vote_referendum = %s AND pop.electorate_id = %s AND ballot.gsc_district_id = %s AND ballot.submitted = 1", [choice,graduate_pk,district_pk])
            votes = cursor.fetchone()[0]
            results += "%s\t%s\t%d\n" % (district,choice,votes)

        for pk,name in prez_choices:
            cursor.execute("SELECT COUNT(*) FROM ballot_ballot AS ballot INNER JOIN ballot_ballot_assu_populations AS pop ON pop.ballot_id = \
            ballot.id WHERE ballot.vote_exec1_id = %s AND pop.electorate_id = %s AND ballot.gsc_district_id = %s AND ballot.submitted = 1", [pk,graduate_pk,district_pk])
            votes = cursor.fetchone()[0]
            president_results += "%s\t%s\t%d\n" % (district,name,votes)

    for year in UNDERGRAD_YEARS:
        ug_pk = Electorate.objects.get(slug='undergrad').pk
        year_pk = Electorate.objects.get(slug=year).pk
        for choice in referendum_choices:
            cursor.execute("SELECT COUNT(*) FROM ballot_ballot AS ballot INNER JOIN ballot_ballot_assu_populations AS pop ON pop.ballot_id = \
            ballot.id WHERE ballot.vote_referendum = %s AND pop.electorate_id = %s AND ballot.undergrad_class_year_id = %s AND ballot.submitted = 1", [choice,ug_pk,year_pk])
            votes = cursor.fetchone()[0]
            results += "%s\t%s\t%d\n" % (year,choice,votes)

        for pk,name in prez_choices:
            cursor.execute("SELECT COUNT(*) FROM ballot_ballot AS ballot INNER JOIN ballot_ballot_assu_populations AS pop ON pop.ballot_id = \
            ballot.id WHERE ballot.vote_exec1_id = %s AND pop.electorate_id = %s AND ballot.undergrad_class_year_id = %s AND ballot.submitted = 1", [pk,ug_pk,year_pk])
            votes = cursor.fetchone()[0]
            president_results += "%s\t%s\t%d\n" % (year,name,votes)


    results = results + "\n" + president_results
    return render_to_response('ballot/admin_breakdown.html', {
        'breakdown': results,
        }, context_instance=RequestContext(request))