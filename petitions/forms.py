from django import forms
from openelections import constants as oe_constants
from issues.models import Issue, Electorate
from petitions.models import Signature
from petitions.models import PaperSignature
from django.forms.widgets import Textarea

class SignatureForm(forms.ModelForm):
    name = forms.CharField(widget=forms.TextInput(attrs=dict(size=45)), required=True,
                           help_text='Use your real name or your signature may not count.')
    sunetid = forms.CharField(widget=forms.TextInput(attrs=dict(size=12)), required=True)
    ip_address = forms.CharField()
    signed_at = forms.DateTimeField()
    issue = forms.ModelChoiceField(queryset=Issue.objects)
    
    class ElectorateChoiceField(forms.ModelChoiceField):
        def label_from_instance(self, instance):
            return instance.name
    
    def __init__(self, issue, *args, **kwargs):
        super(SignatureForm, self).__init__(*args, **kwargs)
        electorates = issue.petition_electorates()
        if electorates:
            self.fields['electorate'] = SignatureForm.ElectorateChoiceField(queryset=electorates,
                                                     widget=forms.RadioSelect,
                                                     empty_label=None)
        else:
            self.fields['electorate'] = None
        
        
    def clean_sunetid(self):
        '''Checks that the provided SUNet ID is alphanumeric and 3-8 chars long
           Ref: https://sunetid.stanford.edu/'''
        sunetid = self.cleaned_data.get('sunetid')
        if sunetid and sunetid.isalnum() and \
           len(sunetid) >= 3 and len(sunetid) <= 8:
            return sunetid
        else:
            raise forms.ValidationError("The SUNet ID '%s' is invalid." % sunetid)
            
    def clean(self):
        '''Ensures that this SUNet ID has not already signed this petition'''
        
        if not self.cleaned_data.get('sunetid'):
            return
        
        # SUNet ID uniqueness - TODOsqs: test
        existing_sig = Signature.objects.filter(sunetid=self.cleaned_data['sunetid'],
                                                issue=self.cleaned_data['issue'])
        if existing_sig:
            raise forms.ValidationError("User '%s' has already signed this petition." % self.cleaned_data['sunetid'])
        else:
            return self.cleaned_data
    
    class Meta:
        model = Signature

class ValidationForm(forms.Form):
    name = forms.CharField(label="Name",widget=forms.TextInput(attrs=dict(size=45)), required=True, \
                           help_text='Use your real name or else your signature won\'t count.')
    did_sign = forms.BooleanField(label="Signed", help_text="Check this box if you signed this petition.",required=False)
    class_petition = forms.BooleanField(label="Solicited in class", help_text="Check this box if you were solicited during a class to sign this petition.",required=False)
    undergrad = forms.BooleanField(label="Undergraduate", help_text="Check this box if you are currently registered as an undergraduate or coterm student.",required=False)
    extra = forms.CharField(label="Additional Comments",widget=Textarea(),required=False)
