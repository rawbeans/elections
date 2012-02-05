from django import forms
from openelections.constants import ISSUE_TYPES
from openelections.issues.models import Electorate, Issue, SpecialFeeRequest, Slate, ExecutiveSlate, ClassPresidentSlate, Candidate, SenateCandidate, GSCCandidate
from issues.models import SMSACandidate

class IssueForm(forms.ModelForm):
    class Meta:
        model = Issue

class NewIssueForm(IssueForm):
    kind = forms.ChoiceField(choices=ISSUE_TYPES, widget=forms.HiddenInput)
    slug = forms.RegexField(label='URL name', help_text='Your public petition will be at petitions.stanford.edu/petitions/your-url-name. Use only lowercase letters, numbers, and hyphens.',
                            regex=r'^[a-z\d-]+$', widget=forms.TextInput(attrs={'size':'25'}))
    sponsor_phone = forms.CharField(label="Contact phone number",help_text="Will not be displayed publicly.")
    qual_fields = {}
    
    def __init__(self, *args, **kwargs):
        super(NewIssueForm, self).__init__(*args, **kwargs)
        instance = getattr(self, 'instance', None)
        if instance:
            self.fields['sunetid1'].widget.attrs['readonly'] = True
    
    def clean_sunetid1(self):
        """Always use the sunetid set on the instance instead of taking the first sunetid
        from the form POSTdata, since we don't verify that."""
        return self.instance.sunetid1
    
    def clean_slug(self):
        '''Ensure slug is unique'''
        slug = self.cleaned_data.get('slug')
        if slug:
            sameslugs = Issue.objects.filter(slug=slug).count()
            if sameslugs != 0:
                raise forms.ValidationError("Your desired URL name is already in use. Choose another.")
        return slug

    def clean(self):
        for i in range(0,len(self.qual_fields)):
            if "qual_" + str(i) not in self.data or self.data["qual_" + str(i)] != 'True':
                raise forms.ValidationError("You did not respond to all the qualification questions. Please review the Qualification Questions "
                                            "section and ensure you meet the qualifications to declare intent.")
        return self.cleaned_data

    def get_qual_fields(self):
        for i in range(0,len(self.qual_fields)):
            yield i, self.qual_fields[i]
    
class NewSlateForm(NewIssueForm):
    title = forms.CharField(label='Slate name', widget=forms.TextInput(attrs={'size':'40'}),
                            help_text='You can change this any time until the start of Spring Quarter.')

class NewExecutiveSlateForm(NewSlateForm):
    class Meta:
        model = ExecutiveSlate
        fields = ('title', 'kind', 'name1', 'sunetid1', 'suid1', 'name2', 'sunetid2', 'suid2', 'sponsor_phone', 'slug')
    
    name1 = forms.CharField(label='President\'s name (you)', widget=forms.TextInput(attrs={'size':'40'}))
    sunetid1 = forms.CharField(label='President\'s SUNet ID @stanford.edu (you)', widget=forms.TextInput(attrs={'size':'12'}))
    name2 = forms.CharField(label='Vice President\'s name', widget=forms.TextInput(attrs={'size':'40'}))
    sunetid2 = forms.CharField(label='Vice President\'s SUNet ID @stanford.edu', widget=forms.TextInput(attrs={'size':'12'}))

    suid1 = forms.CharField(label='President\'s SUID Number', help_text='Will not be displayed publicly. e.g.: 05512345', widget=forms.TextInput(attrs={'size':12}))
    suid2 = forms.CharField(label='Vice President\'s SUID Number', help_text='Will not be displayed publicly. e.g.: 05512345', widget=forms.TextInput(attrs={'size':12}))

    qual_fields = [
                    'Both the candidate for President and the candidate for Vice President are currently registered students at Stanford University.',
                    'Both the candidate for President and the candidate for Vice President intend to be registered students at Stanford University throughout '
                    'the 2011-2012 academic year (Fall, Winter, and Spring quarters.)',
                    'We agree to follow the Executive Campaign Finance restrictions, spending a maximum of $1000 on '
                    'our campaign. We understand that failure to adhere to these guidelines, failure to submit complete budgets '
                    'and spending reports by the specified deadlines, or failure to inform the Elections Commission of changes in '
                    'our budget can result in disqualification from the election.',
                    'We certify that the candidate for President has not previously served in that position for longer than four months.',
                    'We understand that serving as the ASSU Executive is a significant time commitment, includes a time commitment during the summer, '
                    'and that we are expected to remain students in good standing at Stanford throughout our term.',
                    'We understand that the University has existing rules and regulations that continue to apply to us during our candidacy,'
                    'including policies on flyer placement, use of e-mail, speech in White Plaza, and other areas. We agree to follow those rules and regulations.',
                    'We understand that violations of these rules and regulations may result in ineligibility to run for / hold ASSU office until the following '
                    'Spring Quarter.'
    ]
class NewClassPresidentSlateForm(NewSlateForm):
    class Meta:
        model = ClassPresidentSlate
        fields = ('title', 'kind', 'electorates', 'name1', 'sunetid1', 'suid1', 'name2', 'sunetid2', 'suid2', 'name3', 'sunetid3', 'suid3',
                               'name4', 'sunetid4','suid4', 'name5', 'sunetid5', 'suid5',  'sponsor_phone', 'slug')
    
    electorates = forms.ModelChoiceField(label='Class year',
                                        queryset=Electorate.objects.filter(slug__in=Electorate.UNDERGRAD_CLASS_YEARS),
                                        widget=forms.RadioSelect,
                                        empty_label=None,
                                        help_text="Select the class whose presidency you're seeking. For example, if you're running for Sophomore Class President, choose Sophomore.")
    
    name1 = forms.CharField(label='1st member\'s name (you)', widget=forms.TextInput(attrs={'size':'40'}),
                            help_text='The order of slate members (who\'s #1, #2, etc.) doesn\'t matter.')
    sunetid1 = forms.CharField(label='1st member\'s SUNet ID @stanford.edu (you)', widget=forms.TextInput(attrs={'size':'12'}))
    name2 = forms.CharField(label='2nd member\'s name', widget=forms.TextInput(attrs={'size':'40'}))
    sunetid2 = forms.CharField(label='2nd member\'s SUNet ID @stanford.edu', widget=forms.TextInput(attrs={'size':'12'}))
    name3 = forms.CharField(label='3rd member\'s name', widget=forms.TextInput(attrs={'size':'40'}))
    sunetid3 = forms.CharField(label='3rd member\'s SUNet ID @stanford.edu', widget=forms.TextInput(attrs={'size':'12'}))
    name4 = forms.CharField(label='4th member\'s name', widget=forms.TextInput(attrs={'size':'40'}))
    sunetid4 = forms.CharField(label='4th member\'s SUNet ID @stanford.edu', widget=forms.TextInput(attrs={'size':'12'}))
    name5 = forms.CharField(label='5th member\'s name', widget=forms.TextInput(attrs={'size':'40'}),
                            help_text='Only Junior Class President slates can have 5 members (as long as 4 are on campus at one time).',
                            required=False)
    sunetid5 = forms.CharField(label='5th member\'s SUNet ID @stanford.edu', widget=forms.TextInput(attrs={'size':'12'}),
                               required=False)
#    name6 = forms.CharField(label='6th member\'s name', widget=forms.TextInput(attrs={'size':'40'}),
#                            help_text='Only Junior Class President slates can have 5/6 members (as long as 4 are on campus at one time).',
#                            required=False)
#    sunetid6 = forms.CharField(label='6th member\'s SUNet ID @stanford.edu', widget=forms.TextInput(attrs={'size':'12'}),
#                               required=False)

    suid1 = forms.CharField(label='1st member\'s SUID', help_text='Will not be displayed publicly. e.g.: 05512345', widget=forms.TextInput(attrs={'size':12}))
    suid2 = forms.CharField(label='2nd member\'s SUID', help_text='Will not be displayed publicly. e.g.: 05512345', widget=forms.TextInput(attrs={'size':12}))
    suid3 = forms.CharField(label='3rd member\'s SUID', help_text='Will not be displayed publicly. e.g.: 05512345', widget=forms.TextInput(attrs={'size':12}))
    suid4 = forms.CharField(label='4th member\'s SUID', help_text='Will not be displayed publicly. e.g.: 05512345', widget=forms.TextInput(attrs={'size':12}))
    suid5 = forms.CharField(label='5th member\'s SUID', help_text='Will not be displayed publicly. e.g.: 05512345', widget=forms.TextInput(attrs={'size':12}), required=False)

    qual_fields = {'test':'lollerskating'}


    def clean_electorates(self):
        electorate = self.cleaned_data.get('electorates')
        print electorate

        if electorate is not None:
            return [electorate]
  
class NewCandidateForm(NewIssueForm):
    class Meta:
        model = Candidate
        fields = ('title', 'kind', 'name1', 'sunetid1', 'suid1', 'sponsor_phone', 'slug')
    
    name1 = forms.CharField(label='Your name', help_text='(as you would want it to appear on the ballot)',
                            widget=forms.TextInput(attrs={'size':'40'}))
    sunetid1 = forms.CharField(label='SUNet ID', widget=forms.TextInput(attrs={'size':'12'}))
    title = forms.CharField(widget=forms.HiddenInput, required=False)
    suid1 = forms.CharField(label='SUID Number', help_text='Will not be displayed publicly. e.g.: 05512345', widget=forms.TextInput(attrs={'size':12}))

    
    def clean(self):
        self.cleaned_data['title'] = self.cleaned_data.get('name1')
        return super(NewCandidateForm,self).clean()
    

class NewSenateCandidateForm(NewCandidateForm):
    pass
    
class NewGSCCandidateForm(NewCandidateForm):
    class Meta:
        model = GSCCandidate
        fields = ('title', 'kind', 'name1', 'sunetid1', 'electorate', 'sponsor_phone', 'slug')
    
    electorate = forms.ModelChoiceField(label='GSC district',
                                        help_text='Choose At-Large if you want to run ONLY as an At-Large candidate. All school-specific candidates are also considered as At-Large candidates, unless they choose otherwise.',
                                        queryset=Electorate.GSC_DISTRICTS,
                                        widget=forms.RadioSelect,
                                        empty_label=None,)
    
    def clean_electorate(self):
        electorate = self.cleaned_data.get('electorate')
        if electorate:
            return [electorate]
            
    def __init__(self, *args, **kwargs):
        super(NewGSCCandidateForm, self).__init__(*args, **kwargs)
        self.fields['slug'].help_text = 'Your candidate statement will be at voterguide.stanford.edu/your-url-name. Use only lowercase letters, numbers, and hyphens.'                              

class EditIssueForm(IssueForm):
    class Meta:
        model = Issue
        fields = ('statement', 'image',)
    
    statement = forms.CharField(widget=forms.Textarea(attrs={'rows':15, 'cols':70, 'style':'width:98%'}), required=False)

    def __init__(self, *args, **kwargs):
        super(EditIssueForm, self).__init__(*args, **kwargs)
        instance = getattr(self, 'instance', None)
        if instance:
            if instance.image:
                self.fields['image'].label = 'Replace existing image with another image'

class EditSpecialFeeRequestForm(EditIssueForm):
    class Meta:
        model = SpecialFeeRequest
        fields = ('statement', 'image', 'account_statement')


## SMSA
class NewSMSACandidateForm(NewCandidateForm):
    class Meta:
        model = SMSACandidate
        fields = ('title', 'kind', 'name1', 'electorates', 'sunetid1', 'slug')

    electorates = forms.ModelChoiceField(label='SMSA',
                                        queryset=None,
                                        widget=forms.RadioSelect,
                                        empty_label=None,
                                        )

    def __init__(self, *args, **kwargs):
        super(NewSMSACandidateForm, self).__init__(*args, **kwargs)
        self.fields['slug'].help_text = 'Your candidate statement will be at voterguide.stanford.edu/your-url-name. Use only lowercase letters, numbers, and hyphens.'
        instance = getattr(self, 'instance', None)
        if instance:
            electorate_label = instance.candidate_electorate_label()
            if electorate_label == 'SMSA class year':
                self.fields['electorates'].label = 'SMSA class year'
                self.fields['electorates'].queryset = instance.candidate_electorates()
                self.fields['electorates'].help_text = 'Reminder: These are positions for next year. For example, if you are a 1st year, run for 2nd-Year Class Rep.'
            else:
                del self.fields['electorates']

    def clean_electorates(self):
        electorate = self.cleaned_data.get('electorates')
        if electorate:
            return [electorate]


issue_edit_forms = {
    #'CandidateUS': EditCandidateUSForm,
    'Issue': EditIssueForm,
    'SpecialFeeRequest': EditSpecialFeeRequestForm,
}

issue_new_forms = {
    'Issue': NewIssueForm,
    'SenateCandidate': NewSenateCandidateForm,
    'ClassPresidentSlate': NewClassPresidentSlateForm,
    'ExecutiveSlate': NewExecutiveSlateForm,
    'GSCCandidate': NewGSCCandidateForm,
    'SpecialFeeRequest': NewIssueForm,

    ## SMSA
    'SMSACandidate': NewSMSACandidateForm,
    'SMSAClassRepCandidate': NewSMSACandidateForm,
}

def form_class_for_issue(issue):
    issue_class_name = issue.__class__.__name__
    if issue.pk:
        return issue_edit_forms.get(issue_class_name, EditIssueForm)
    else:
        return issue_new_forms.get(issue_class_name, NewIssueForm)

class MultiCreateForm(forms.Form):
    text = forms.CharField(widget=forms.Textarea)