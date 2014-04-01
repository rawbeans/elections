from django.db import models
from issues.models import *
from django.conf import settings
import hashlib
from issues.models import ClassPresidentSlate, SMSACandidate, SMSAClassRepCandidate

def make_voter_id(sunetid):
    return sunetid
#    m = hashlib.sha1()
#    m.update(settings.WEBAUTH_SHARED_SECRET + 'sunetid_to_voter_id' + sunetid)
#    return m.hexdigest()
# the database will be deleted per bylaws. Hashing SUNetIDs does not provide security when you know the
# SUNetID, and it will be useful to watch for voter fraud.

class Ballot(models.Model):
    @classmethod
    def get_or_create_by_sunetid(klass, sunetid):
        v = make_voter_id(sunetid)
        return klass.objects.get_or_create(voter_id=v)

    voter_id = models.CharField(max_length=64, db_index=True)
    submitted = models.BooleanField(default=False)

    assu_populations = models.ManyToManyField(Electorate, related_name='ballot_assu_pops')
    undergrad_class_year = models.ForeignKey(Electorate, related_name='ballot_undergrad_class_year', blank=True, null=True)
    gsc_district = models.ForeignKey(Electorate, related_name='ballot_gsc_district', blank=True, null=True)
    smsa_class_year = models.ForeignKey(Electorate, related_name='ballot_smsa_class_year', blank=True, null=True)
    date_updated = models.DateTimeField(auto_now=True)

    votes_senate = models.ManyToManyField(SenateCandidate, related_name='votes', blank=True)
    votes_senate_writein = models.CharField(max_length=500, blank=True)

    votes_gsc_district = models.ManyToManyField(GSCCandidate, related_name='votes_district', blank=True)
    votes_gsc_district_writein = models.CharField(max_length=500, blank=True)

    votes_gsc_atlarge = models.ManyToManyField(GSCCandidate, related_name='votes_atlarge', blank=True)
    votes_gsc_atlarge_writein = models.CharField(max_length=500, blank=True)

    votes_specfee_yes = models.ManyToManyField(SpecialFeeRequest, related_name='votes_yes', blank=True)
    votes_specfee_no = models.ManyToManyField(SpecialFeeRequest, related_name='votes_no', blank=True)
    votes_specfee_ab = models.ManyToManyField(SpecialFeeRequest, related_name='votes_ab', blank=True)


    N_EXEC_VOTES = 3
    vote_exec1 = models.ForeignKey(ExecutiveSlate, blank=True, null=True, related_name='votes_exec1')
    vote_exec2 = models.ForeignKey(ExecutiveSlate, blank=True, null=True, related_name='votes_exec2')
    vote_exec3 = models.ForeignKey(ExecutiveSlate, blank=True, null=True, related_name='votes_exec3')
    #vote_exec4 = models.ForeignKey(ExecutiveSlate, blank=True, null=True, related_name='votes_exec4')
    #vote_exec5 = models.ForeignKey(ExecutiveSlate, blank=True, null=True, related_name='votes_exec5')
    #vote_exec6 = models.ForeignKey(ExecutiveSlate, blank=True, null=True, related_name='votes_exec6')
    vote_exec1_writein = models.CharField(max_length=75, blank=True)
    vote_exec2_writein = models.CharField(max_length=75, blank=True)
    vote_exec3_writein = models.CharField(max_length=75, blank=True)
    #vote_exec4_writein = models.CharField(max_length=75, blank=True)
    #vote_exec5_writein = models.CharField(max_length=75, blank=True)
    #vote_exec6_writein = models.CharField(max_length=75, blank=True)

    N_CLASSPRES_VOTES = 5
    vote_classpres1 = models.ForeignKey(ClassPresidentSlate, blank=True, null=True, related_name='votes_classpres1')
    vote_classpres2 = models.ForeignKey(ClassPresidentSlate, blank=True, null=True, related_name='votes_classpres2')
    vote_classpres3 = models.ForeignKey(ClassPresidentSlate, blank=True, null=True, related_name='votes_classpres3')
    vote_classpres4 = models.ForeignKey(ClassPresidentSlate, blank=True, null=True, related_name='votes_classpres4')
    vote_classpres5 = models.ForeignKey(ClassPresidentSlate, blank=True, null=True, related_name='votes_classpres5')
    vote_classpres1_writein = models.CharField(max_length=75, blank=True)
    vote_classpres2_writein = models.CharField(max_length=75, blank=True)
    vote_classpres3_writein = models.CharField(max_length=75, blank=True)
    vote_classpres4_writein = models.CharField(max_length=75, blank=True)
    vote_classpres5_writein = models.CharField(max_length=75, blank=True)

    vote_referendum = models.CharField(max_length=1,blank=True,null=True)

    vote_smsa_pres = models.ForeignKey(SMSACandidate, related_name='votes_smsa_pres', blank=True, null=True)
    vote_smsa_vpo = models.ForeignKey(SMSACandidate, related_name='votes_smsa_vpo', blank=True, null=True)
    vote_smsa_vpa = models.ForeignKey(SMSACandidate, related_name='votes_smsa_vpa', blank=True, null=True)
    vote_smsa_t = models.ForeignKey(SMSACandidate, related_name='votes_smsa_t', blank=True, null=True)

    votes_smsa_classrep = models.ManyToManyField(SMSAClassRepCandidate, related_name='votes_smsa_classrep', blank=True)

    vote_smsa_ccap_pc = models.ForeignKey(SMSACandidate, related_name='votes_smsa_ccap_pc', blank=True, null=True)
    votes_smsa_ccap_c = models.ManyToManyField(SMSACandidate, related_name='votes_smsa_ccap_c', blank=True)
    vote_smsa_ccap_md = models.ForeignKey(SMSACandidate, related_name='votes_smsa_ccap_md', blank=True, null=True)
    vote_smsa_ccap_yo = models.ForeignKey(SMSACandidate, related_name='votes_smsa_ccap_yo', blank=True, null=True)

    votes_smsa_sc_pc = models.ManyToManyField(SMSACandidate, related_name='votes_smsa_sc_pc', blank=True)
    votes_smsa_sc_c = models.ManyToManyField(SMSACandidate, related_name='votes_smsa_sc_c', blank=True)
    vote_smsa_sc_yo = models.ForeignKey(SMSACandidate, related_name='votes_smsa_yo', blank=True, null=True)

    vote_smsa_mw_pc = models.ForeignKey(SMSACandidate, related_name='votes_smsa_mw_pc', blank=True, null=True)
    vote_smsa_mw_c = models.ForeignKey(SMSACandidate, related_name='votes_smsa_mw_c', blank=True, null=True)
    vote_smsa_alumni = models.ForeignKey(SMSACandidate, related_name='votes_smsa_alumni', blank=True, null=True)
    vote_smsa_prospective = models.ForeignKey(SMSACandidate, related_name='votes_smsa_prospective', blank=True, null=True)

    def needs_ballot_choice(self):
        if not self.is_grad() and not self.is_undergrad():
            return 'You must select either "Grad" or "Undergrad," or both.'
        if self.is_grad():
            if not self.gsc_district:
                return 'You must select your GSC district, or uncheck "Grad" if you are not a grad student.'
            if self.is_smsa():
                if not self.smsa_class_year:
                    return 'You must select your SMSA class year, or deselect the SMSA population if you are not in SMSA.'
        elif self.is_undergrad():
            if not self.undergrad_class_year:
                return 'You must select your undergrad class year, or uncheck "Undergrad" if you are not an undergrad.'
        return False

    def electorate_slugs(self):
        return map(lambda e: e and e.slug or '', list(self.assu_populations.all()) + [self.undergrad_class_year, self.gsc_district, self.smsa_class_year])

    def is_undergrad(self):
        return bool(self.assu_populations.filter(slug='undergrad').all())

    def is_grad(self):
        return bool(self.assu_populations.filter(slug='graduate').all())

    def is_smsa(self):
        return self.smsa_class_year

    def get_electorate_slugs(self):
        return ','.join(self.electorate_slugs())

    def __unicode__(self):
        return "Ballot: voter %s [%s]" % (self.voter_id, ','.join(self.electorate_slugs()))


class VoteRecord(models.Model):
    sunetid = models.CharField(max_length=12)
    type = models.CharField(max_length=48)
    datetime = models.DateTimeField()
    ip = models.CharField(max_length=15)
    comments = models.CharField(max_length=160)
