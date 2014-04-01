from django import forms
from openelections.constants import ISSUE_TYPES
from issues.models import Electorate, Issue, SpecialFeeRequest, Slate, ExecutiveSlate, ClassPresidentSlate, Candidate, SenateCandidate, GSCCandidate
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
                    'the 2013-2014 academic year (Fall, Winter, and Spring quarters.)',

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
                               'name4', 'sunetid4','suid4', 'name5', 'sunetid5', 'suid5', 'name6', 'sunetid6', 'suid6',  'sponsor_phone', 'slug')
    
    electorates = forms.ModelChoiceField(label='Class year',
                                        queryset=Electorate.objects.filter(slug__in=Electorate.UNDERGRAD_CLASS_YEARS).exclude(slug='undergrad-5plus'),
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
    name6 = forms.CharField(label='6th member\'s name', widget=forms.TextInput(attrs={'size':'40'}),
                            help_text='Only Junior Class President slates can have 5/6 members (as long as 4 are on campus at one time).',
                            required=False)
    sunetid6 = forms.CharField(label='6th member\'s SUNet ID @stanford.edu', widget=forms.TextInput(attrs={'size':'12'}),
                                help_text='Only Junior Class President slates can have 5/6 members (as long as 4 are on campus at one time).',
                               required=False)

    suid1 = forms.CharField(label='1st member\'s SUID', help_text='Will not be displayed publicly. e.g.: 05512345', widget=forms.TextInput(attrs={'size':12}))
    suid2 = forms.CharField(label='2nd member\'s SUID', help_text='Will not be displayed publicly. e.g.: 05512345', widget=forms.TextInput(attrs={'size':12}))
    suid3 = forms.CharField(label='3rd member\'s SUID', help_text='Will not be displayed publicly. e.g.: 05512345', widget=forms.TextInput(attrs={'size':12}))
    suid4 = forms.CharField(label='4th member\'s SUID', help_text='Will not be displayed publicly. e.g.: 05512345', widget=forms.TextInput(attrs={'size':12}))
    suid5 = forms.CharField(label='5th member\'s SUID', help_text='Will not be displayed publicly. e.g.: 05512345', widget=forms.TextInput(attrs={'size':12}), required=False)
    suid6 = forms.CharField(label='6th member\'s SUID', help_text='Will not be displayed publicly. e.g.: 05512345', widget=forms.TextInput(attrs={'size':12}), required=False)


    qual_fields = [
        'All slate members are currently registered undergraduate students at Stanford University.',

        'All slate members intend to be registered undergraduate students at Stanford University throughout '
        'the 2013-2014 academic year (Fall, Winter, and Spring quarters.)',

        'If we are a Sophomore or Senior class president slate, our slate contains exactly four members. If we are a Junior slate, '
        'we understand that our slate may contain four, five, or six members, AND four members must be on campus at all times.',

        'We certify that our slate is running for the Class President position of the undergraduate class with which we most '
        'closely identify socially.',

        'We understand that serving as Class Presidents is a significant time commitment, '
        'and that we are expected to remain students in good standing at Stanford throughout our term.',

        'We understand that the University has existing rules and regulations that continue to apply to us during our candidacy, '
        'including policies on flyer placement, use of e-mail, speech in White Plaza, and other areas. We agree to follow those rules and regulations.',
    ]


    def clean_electorates(self):
        electorate = self.cleaned_data.get('electorates')

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
    qual_fields = [
        'I am a currently registered undergraduate student at Stanford University.',

        'I intend to remain a registered undergradaute student at Stanford University throughout '
        'the 2013-2014 academic year (Fall, Winter, and Spring quarters.)',

        'I understand that I may only go abroad spring quarter of my first term, or any single quarter of my second or subsequent term, while I serve on the Undergraduate Senate.',

        'I understand that serving as a member of the Undergraduate Senate is a time commitment, and that I will be expected to attend its '
        'regular meetings, as well as meetings of any subcommittees of which I am a member. I additionally understand that not attending '
        'meetings can lead to my removal as a Senator.',

        'I understand that my term as a member of the Undergraduate Senate begins this year, no later than 14 days before the end of Spring Quarter',

        'I understand that the University has existing rules and regulations that continue to apply to me during my candidacy, '
        'including policies on flyer placement, use of e-mail, speech in White Plaza, and other areas. I agree to follow those rules and regulations.',
        ]
    
class NewGSCCandidateForm(NewCandidateForm):
    class Meta:
        model = GSCCandidate
        fields = ('title', 'kind', 'name1', 'sunetid1', 'electorates', 'sponsor_phone', 'slug')
    
    electorates = forms.ModelChoiceField(label='GSC district',
                                        help_text='Choose At-Large if you want to run ONLY as an At-Large candidate. All school-specific candidates are also considered as At-Large candidates, unless they choose otherwise.',
                                        queryset=Electorate.objects.filter(slug__in=Electorate.GSC_DISTRICTS),
                                        widget=forms.RadioSelect,
                                        empty_label=None,)

    qual_fields = [
        'I am a currently registered graduate student at Stanford University.',

        'I intend to remain a registered gradaute student at Stanford University throughout '
        'the 2013-2014 academic year (Fall, Winter, and Spring quarters.)',

        'If I am declaring candidacy in a non-at-large district, I certify that this is the district with which I most closely identify, '
        'e.g. because I was admitted to a department in this district, or because I am currently funded through a department in this district.',

        'I understand that I may take a leave of absence from the GSC for up to one quarter at a time.',

        'I understand that I may be suspended or expelled from the GSC should I miss more than 6 GSC meetings in a three-month period '
        'without obtaining a leave of absence, or if I violate University regulations.',

        'I will not violate University rules/regulations in an attempt to influence the outcome of the election, and I understand '
        'that doing so is grounds for disqualification.',
        ]

    def clean_electorates(self):
        electorate = self.cleaned_data.get('electorates')

        if electorate is not None:
            return [electorate]
            
    def __init__(self, *args, **kwargs):
        super(NewGSCCandidateForm, self).__init__(*args, **kwargs)
        self.fields['slug'].help_text = 'Your candidate statement will be at voterguide.stanford.edu/your-url-name. Use only lowercase letters, numbers, and hyphens.You do not need to petition.'

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


class NewSpecialFeeForm(NewIssueForm):
    class Meta:
        model = SpecialFeeRequest
        fields = ('title', 'kind', 'electorates', 'declared_petition', 'total_request_amount','total_past_request_amount', 'budget', 'past_budget', 'budget_spreadsheet', 'account_statement', 'name1', 'sunetid1', 'suid1', 'sponsor_phone', 'slug',)

    name1 = forms.CharField(label='Sponsor\'s name', widget=forms.TextInput(attrs={'size':'40'}))
    sunetid1 = forms.CharField(label='Sponsor\'s SUNetID', widget=forms.TextInput(attrs={'size':'12'}))
    suid1 = forms.CharField(label='Sponsor\'s SUID Number', help_text='Will not be displayed publicly. e.g.: 05512345', widget=forms.TextInput(attrs={'size':12}))

    title = forms.CharField(label='Group name', widget=forms.TextInput(attrs={'size':'40'}))
    budget = forms.FileField(label='MyGroups2 Funding Request for next year',help_text='PDF files only. Must be a completed MyGroups2 funding reqeuest.')
    past_budget = forms.FileField(label='MyGroups2 funding request from this year', required=False,help_text='PDF files only. If you did not request Special Fees for this year, leave this blank.')
    budget_spreadsheet = forms.FileField(label='PDF of Excel Budgeting Spreadsheet', help_text='PDF files only. The Elections Commission provides you with this file after you submit your Excel budget.')
    account_statement = forms.FileField(label="Current MyGroups2 account statement",help_text='PDF files only')
    total_request_amount = forms.DecimalField(max_digits=8, decimal_places=2,help_text='Must match the exact amount being requested in Special Fees on your MyGroups2 funding request ' \
                                                                                       'for next year. If your request includes reserve transfers to cover some fees, do not include '
                                                                                       'those reserve transfers. Include only money sought directly in Special Fees.',
                                                label="Exact amount requested in Special Fees next year")
    total_past_request_amount = forms.DecimalField(max_digits=8, decimal_places=2,label="Amount requested in Special Fees last year",help_text="Must match the exact amount specified " \
                                                                                  "on your MyGroups2 funding request from last year.")


    electorates = forms.ChoiceField(label='Fee Type',
        choices=(('U','Undergraduate'),('G','Graduate'),('J','Joint')),
        widget=forms.RadioSelect,
    )

    declared_petition = forms.ChoiceField(label='Petition Type',
        choices=(
                ('no-petition','Previous Special Fee, small increase, & legislative body approval: no petition'),
                ('10-percent', 'Legislative body approval: 10% petition'),
                ('15-percent', 'No legislative body approval: 15% petition')
        ),
        widget=forms.RadioSelect,
    )

    qual_fields = [
        'Our group is currently a registered Voluntary Student Organization (VSO) at Stanford University, and intends to remain a VSO next year.',

        'Our group is not an agency of the Association or an umbrella group. If we are, we will contact the Elections Commission prior to submitting this form.',

        'Our group understands all the ballot deadlines, including the hard deadline for all petition materials and signatures on Sunday, March 9, at 11:59PM.',

        'Our group understands the full disclosure requirements as outlined on the Special Fees website and in the Special Fees information packet, and agrees to provide '
        'full disclosure of the required financial information by the deadline. We understand that not doing so is grounds for disqualification from Special Fees.',

        'Our group understands that petition signatures for one budget are not valid for any other budget, and that if our budget changes, we must start over petitioning.',

        'Our group understands that students may waive their Special Fees after the election.',

        'Our group understands that we may not deprive any students of any or all of our group\'s services unless they receive a fee waiver from our group.',

        'Our group understands that the University has existing rules and regulations that continue to apply during the Special Fees process, '
        'including policies on flyer placement, use of e-mail, speech in White Plaza, and other areas. We collectively agree to follow those rules and regulations.',
    ]

    def clean_electorates(self):
        electorate = self.cleaned_data.get('electorates')
        if electorate == 'U':
            return [Electorate.objects.get(slug='undergrad'), Electorate.objects.get(slug='coterm')]
        elif electorate == 'G':
            return [Electorate.objects.get(slug='graduate'), Electorate.objects.get(slug='coterm')]
        elif electorate == 'J':
            return [Electorate.objects.get(slug='undergrad'),Electorate.objects.get(slug='graduate'), Electorate.objects.get(slug='coterm')]
        else:
            raise forms.ValidationError("Illegal population selected")

    def clean_kind(self):
        return 'SF'

    def clean(self):
        self.cleaned_data['public'] = False
        return super(NewSpecialFeeForm,self).clean()


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
    'SpecialFeeRequest': NewSpecialFeeForm,

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
