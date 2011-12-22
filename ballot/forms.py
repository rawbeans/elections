import random
from django import forms
from django.forms.formsets import formset_factory, BaseFormSet
from django.utils.safestring import mark_safe
from openelections import constants as c
from openelections.ballot.models import Ballot
from openelections.issues.models import Issue, SenateCandidate, GSCCandidate, ExecutiveSlate, Electorate, SpecialFeeRequest, ClassPresidentSlate, kinds_classes

def html_id(issue):
    return 'issue_%d' % issue.pk
Issue.html_id = html_id

def objs_to_pks(objs):
    return ','.join([str(o.pk) for o in objs])
    
def pks_to_objs(pks):
    return [Issue.objects.get(pk=pk) for pk in map(int, pks.split(','))]

class BallotElectorateForm(forms.ModelForm):
    class Meta:
        model = Ballot
        fields = ['assu_populations', 'undergrad_class_year', 'gsc_district', 'smsa_class_year']

    class ElectorateChoiceField(forms.ModelChoiceField):
        widget = forms.RadioSelect
        
        def label_from_instance(self, instance):
            return instance.voter_name

    class ElectorateMultipleChoiceField(forms.ModelMultipleChoiceField):
        widget = forms.CheckboxSelectMultiple
        
        def label_from_instance(self, instance):
            return instance.voter_name

    def __init__(self, *args, **kwargs):
        if not kwargs['instance']:
            raise Exception("no instance for BallotElectorateForm")
        super(BallotElectorateForm, self).__init__(*args, **kwargs)
    
    assu_populations = ElectorateMultipleChoiceField(
        queryset=Electorate.queryset_with_slugs(Electorate.ASSU_POPULATIONS), 
        label='ASSU populations', help_text="Choose both if you are a coterm and currently registered as both an undergrad and a grad.",
        required=False)
        
    undergrad_class_year = ElectorateChoiceField(
        queryset=Electorate.queryset_with_slugs(Electorate.UNDERGRAD_CLASS_YEARS),
        label='NEXT YEAR: Undergraduate Class Year',
        help_text='If unsure, choose the class year that you will most closely socially identify with NEXT YEAR. Seniors \
        may vote as a 5+ year undergraduate regardless of their graduation plans.',
        empty_label='(I am not an undergrad)', required=False)
    
    gsc_district = ElectorateChoiceField(
        queryset=Electorate.queryset_with_slugs(Electorate.GSC_DISTRICTS_NO_ATLARGE),
        label='Graduate School Council (GSC) district', help_text='Choose the GSC district with which you most closely associate yourself. If you are in multiple GSC districts, choose the one in which you want to select your local GSC rep.',
        empty_label='(I am not a grad student)', required=False)
    
    smsa_class_year = ElectorateChoiceField(
        queryset=Electorate.queryset_with_slugs(Electorate.SMSA_CLASS_YEARS),
        label='NEXT YEAR: School of Medicine class year (SMSA)',
        empty_label='(I am not in SMSA--not a School of Med candidate)', required=False)

def ballot_form_factory(ballot):
    class _BallotForm(forms.ModelForm):
        class Meta:
            model = Ballot
            exclude = ['voter_id', 'assu_populations', 'undergrad_class_year', 'gsc_district', 'smsa_class_year']
        
        def __init__(self, *args, **kwargs):
            if not kwargs['instance']:
                raise Exception("no instance for BallotForm")
            super(_BallotForm, self).__init__(*args, **kwargs)
        
        def clean(self):
            #self.cleaned_data = self.clean_exec_votes()
            #self.cleaned_data = self.clean_classpres_votes()
            self.cleaned_data = self.clean_special_fee_votes()
            return self.cleaned_data
        
        def clean_exec_votes(self):
            pass
            
        def clean_classpres_votes(self):
            pass
        
        def clean_votes_senate(self):
            v = self.cleaned_data['votes_senate']
            max_choices = self.fields['votes_senate'].max_choices
            if len(v) > max_choices:
                raise forms.ValidationError('You may only cast %d votes for Senate (you chose %d).' % (max_choices, len(v)))
            return self.cleaned_data['votes_senate']
            
        def clean_votes_gsc_district(self):
            v = self.cleaned_data['votes_gsc_district']
            max_choices = self.fields['votes_gsc_district'].max_choices
            if len(v) > max_choices:
                raise forms.ValidationError('You may only cast %d vote(s) for GSC %s District rep (you chose %d).' % \
                                            (max_choices, self.instance.gsc_district.name, len(v)))
            return self.cleaned_data['votes_gsc_district']
            
        def clean_votes_gsc_atlarge(self):
            v = self.cleaned_data['votes_gsc_atlarge']
            max_choices = self.fields['votes_gsc_atlarge'].max_choices
            if len(v) > max_choices:
                raise forms.ValidationError('You may only cast %d at-large votes for GSC reps (you chose %d).' % (max_choices, len(v)))
            return self.cleaned_data['votes_gsc_atlarge']
        
        def clean_votes_smsa_classrep(self):
            v = self.cleaned_data['votes_smsa_classrep']
            max_choices = self.fields['votes_smsa_classrep'].max_choices
            if len(v) > max_choices:
                raise forms.ValidationError('You may only cast %d votes for SMSA Class Rep (you chose %d).' % (max_choices, len(v)))
            return self.cleaned_data['votes_smsa_classrep']
        
        def clean_votes_smsa_ccap(self):
            v = self.cleaned_data['votes_smsa_ccap']
            max_choices = self.fields['votes_smsa_ccap'].max_choices
            if len(v) > max_choices:
                raise forms.ValidationError('You may only cast %d votes for SMSA CCAP Rep (you chose %d).' % (max_choices, len(v)))
            return self.cleaned_data['votes_smsa_ccap']
        
        def clean_special_fee_votes(self):
            yes_votes = []
            no_votes = []
            ab_votes = []

            errors = []
            
            for k,v in self.cleaned_data.items():
                if k.startswith('vote_specfee'):
                    pk = int(k[len('vote_specfee')+1:])
                    sf = SpecialFeeRequest.objects.get(pk=pk)
                    if not v:
                        #print "error on %s" % sf.title
                        self._errors['vote_specfee_' + str(pk)] = self.error_class(['You must submit a vote on %s or choose to abstain.' % sf.title])
                        continue
                    v = int(v)
                    if v == c.VOTE_YES:
                        yes_votes.append(sf)
                    elif v == c.VOTE_NO:
                        no_votes.append(sf)
                    elif v == c.VOTE_AB:
                        ab_votes.append(sf)

            if len(errors) > 0:
                raise forms.ValidationError("Errors exist.")

            self.cleaned_data['votes_specfee_yes'] = yes_votes
            self.cleaned_data['votes_specfee_no'] = no_votes
            self.cleaned_data['votes_specfee_ab'] = ab_votes

            
            return self.cleaned_data

        def clean_vote_referendum(self):
            if not self.cleaned_data['vote_referendum']:
                raise forms.ValidationError("You must submit a vote on Measure A - Advisory Question on ROTC or choose to abstain.")
            return self.cleaned_data['vote_referendum']
        
        def save(self, commit=True):            
            #print "cd: %s" % self.cleaned_data
            
            # special fees
            self.instance.votes_specfee_yes = self.cleaned_data['votes_specfee_yes']
            self.instance.votes_specfee_no = self.cleaned_data['votes_specfee_no']
            self.instance.votes_specfee_ab = self.cleaned_data['votes_specfee_ab']
            self.instance.submitted = True
            
            super(_BallotForm, self).save(commit)
    
    
    exec_qs = ExecutiveSlate.objects.filter(kind=c.ISSUE_EXEC).order_by('pk').all()
    for i in range(1, Ballot.N_EXEC_VOTES+1):
        f_id = 'vote_exec%d' % i
        f = SlateChoiceField(queryset=exec_qs, required=False)
        _BallotForm.base_fields[f_id] = f
        _BallotForm.base_fields[f_id+'_writein'] = forms.CharField(required=False)
    
    all_specfees_qs = SpecialFeeRequest.objects.filter(kind=c.ISSUE_SPECFEE).filter(public=1).order_by('?')
    _BallotForm.base_fields['votes_specfee_yes'] = forms.ModelMultipleChoiceField(queryset=all_specfees_qs, required=False)
    _BallotForm.base_fields['votes_specfee_no'] = forms.ModelMultipleChoiceField(queryset=all_specfees_qs, required=False)
    _BallotForm.base_fields['votes_specfee_ab'] = forms.ModelMultipleChoiceField(queryset=all_specfees_qs, required=False)

    if ballot.is_undergrad():
        senate_qs = SenateCandidate.objects.filter(kind=c.ISSUE_US).filter(public=1).order_by('?')
        _BallotForm.base_fields['votes_senate'] = SenateCandidatesField(queryset=senate_qs, required=False)
        _BallotForm.base_fields['votes_senate_writein'] = forms.CharField(required=False, widget=forms.Textarea(attrs=dict(rows=2, cols=40)))
        
        classpres_qs = ClassPresidentSlate.objects.filter(kind=c.ISSUE_CLASSPRES, electorates=ballot.undergrad_class_year).order_by('pk').all()
        n_classpres = min(len(classpres_qs), Ballot.N_CLASSPRES_VOTES)
        for i in range(1, n_classpres+1):
            f_id = 'vote_classpres%d' % i
            f = SlateChoiceField(queryset=classpres_qs, required=False)
            _BallotForm.base_fields[f_id] = f
            _BallotForm.base_fields[f_id+'_writein'] = forms.CharField(required=False)
        for j in range(n_classpres+1, Ballot.N_CLASSPRES_VOTES+1):
            f_id = 'vote_classpres%d' % j
            del _BallotForm.base_fields[f_id]
            del _BallotForm.base_fields[f_id+'_writein']
    else:
        del _BallotForm.base_fields['votes_senate']
        del _BallotForm.base_fields['vote_classpres1']
        del _BallotForm.base_fields['vote_classpres2']
        del _BallotForm.base_fields['vote_classpres3']
        del _BallotForm.base_fields['vote_classpres4']
        del _BallotForm.base_fields['vote_classpres5']

    
    if ballot.is_grad():
        gsc_district_qs = GSCCandidate.objects.filter(kind=c.ISSUE_GSC, electorates=ballot.gsc_district).order_by('?').all()
        f = GSCDistrictCandidatesField(queryset=gsc_district_qs, required=False, ballot=ballot)
        _BallotForm.base_fields['votes_gsc_district'] = f
        _BallotForm.base_fields['votes_gsc_district_writein'] = forms.CharField(required=False, widget=forms.Textarea(attrs=dict(rows=1, cols=40)))
        
        gsc_atlarge_qs = GSCCandidate.objects.filter(kind=c.ISSUE_GSC).order_by('?').all()
        _BallotForm.base_fields['votes_gsc_atlarge'] = GSCAtLargeCandidatesField(queryset=gsc_atlarge_qs, required=False)
        _BallotForm.base_fields['votes_gsc_atlarge_writein'] = forms.CharField(required=False, widget=forms.Textarea(attrs=dict(rows=2, cols=40)))
    else:
        del _BallotForm.base_fields['votes_gsc_district']
        del _BallotForm.base_fields['votes_gsc_district_writein']
        del _BallotForm.base_fields['votes_gsc_atlarge']
        del _BallotForm.base_fields['votes_gsc_atlarge_writein']
    
    if ballot.is_smsa():
        _BallotForm.smsa = True
        
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

        # set querysets
        smsa_electorates = [ballot.smsa_class_year, None]
        for f_id, kind in smsa_data:
            qs = kinds_classes[kind].objects.filter(kind=kind).all()
            sel = None
            if len(qs) == 1: # default to selected if only one candidate
                setattr(ballot, f_id, qs[0])
            _BallotForm.base_fields[f_id] = SMSACandidatesChoiceField(queryset=qs, required=False, initial=sel)
        
        # smsa positions with multiple votes
        smsa_multi_data = (
            ('votes_smsa_ccap_c', 'SMSA-CCAP-C'),
            ('votes_smsa_sc_pc', 'SMSA-SC-C'),
            ('votes_smsa_sc_c', 'SMSA-SC-PC'),
        )
        
        # set querysets
        for f_id, kind in smsa_multi_data:
            qs = kinds_classes[kind].objects.filter(kind=kind).all()
            _BallotForm.base_fields[f_id] = SMSACandidatesMultiChoiceField(queryset=qs, required=False, label='Choose up to 2.')

        _BallotForm.base_fields['votes_smsa_classrep'] = SMSACandidatesMultiChoiceField(
                queryset=kinds_classes['SMSA-ClassRep'].objects.filter(kind='SMSA-ClassRep',electorates__in=smsa_electorates).all(),
                required=False, label='Choose up to 2.')
                
    else:
        for k,v in _BallotForm.base_fields.items():
            if 'smsa' in k:
                del _BallotForm.base_fields[k]
    
    specfee_qs = SpecialFeeRequest.objects.filter(kind=c.ISSUE_SPECFEE, electorates__in=ballot.assu_populations.all()).order_by('?').filter(public=1).all()
    _BallotForm.fields_specfees = []
    for sf in specfee_qs:
        initial = None
        if sf in ballot.votes_specfee_yes.all():
            initial = c.VOTE_YES
        elif sf in ballot.votes_specfee_no.all():
            initial = c.VOTE_NO
        elif sf in ballot.votes_specfee_ab.all():
            initial = c.VOTE_AB
        else:
            initial = None
        f_id = 'vote_specfee_%d' % sf.pk
        f = forms.ChoiceField(choices=c.VOTES_YNA, label=sf.title, required=False, initial=initial, widget=forms.RadioSelect)
        f.is_special_fee = True
        f.issue = sf
        _BallotForm.base_fields[f_id] = f


    ## referendum: Measure A
    refchoices = (
                ('a', "a. I support the reinstatement of ROTC at Stanford University."),
                ('b', "b. I oppose the reinstatement of ROTC at Stanford University."),
                ('c', "c. I choose to abstain."),
        )
    _BallotForm.base_fields['vote_referendum'] = forms.ChoiceField(choices=refchoices, label="Choices", required=False, initial=ballot.vote_referendum, widget=forms.RadioSelect)
    
    return _BallotForm


class CandidatesField(forms.ModelMultipleChoiceField):
    widget = forms.CheckboxSelectMultiple
    
    def __init__(self, *args, **kwargs):
        self.ballot = kwargs.pop('ballot', None)
        super(CandidatesField, self).__init__(*args, **kwargs)
        
    def label_from_instance(self, instance):
        return instance.ballot_name()

class SenateCandidatesField(CandidatesField):
    max_choices = 15
    
    def label_from_instance(self, instance):
        return instance.ballot_name()

class SlateChoiceField(forms.ModelChoiceField):
    #widget = forms.RadioSelect
    
    def label_from_instance(self, instance):
        return instance.ballot_name()
        
class GSCCandidatesField(CandidatesField):
    pass
    
class GSCDistrictCandidatesField(GSCCandidatesField):
    def __init__(self, *args, **kwargs):
        if kwargs['ballot'].gsc_district.slug == 'gsc-eng':
            self.max_choices = 2
            kwargs['label'] = 'Choose up to 2 candidates.'
            kwargs['widget'] = forms.CheckboxSelectMultiple
        else:
            self.max_choices = 1
            kwargs['label'] = 'Choose 1 candidate.'
            kwargs['widget'] = forms.CheckboxSelectMultiple
        super(GSCDistrictCandidatesField, self).__init__(*args, **kwargs)
    
    def section_title(self):
        return "GSC %s District" % self.electorate.name
    
    def gsc_district(self):
        self.electorates.filter(slug__in=Electorate.GSC_DISTRICTS)
    
    def is_engineering(self):
        return self.gsc_district().slug == 'gsc-eng'
    
    def label(self):
        if self.is_engineering():
            return "Choose up to 2."
        else:
            return "Choose 1."
        
class GSCAtLargeCandidatesField(GSCCandidatesField):
    max_choices = 5
    
    def label_from_instance(self, instance):
        return "%s (%s)" % (instance.ballot_name(), instance.get_typed().district().name)

class SMSACandidatesMultiChoiceField(CandidatesField):
    max_choices = 2
    

class SMSACandidatesChoiceField(forms.ModelChoiceField):
    widget = forms.RadioSelect
    
    def __init__(self, *args, **kwargs):
        super(SMSACandidatesChoiceField, self).__init__(*args, empty_label=None, **kwargs)
    
    def label_from_instance(self, instance):
        return instance.ballot_name()

