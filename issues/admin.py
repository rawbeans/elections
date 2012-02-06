from openelections.issues.models import Electorate, Issue
from django.contrib import admin

class ElectorateAdmin(admin.ModelAdmin):
    save_on_top = True
    list_display_links = ('pk', )
    list_display = ('pk', 'name', 'slug', 'voter_name_opt',)
    list_editable = ('name', 'slug', 'voter_name_opt',)
    ordering = ('slug',)

admin.site.register(Electorate, ElectorateAdmin)

def issue_num_signatures(issue):
    return issue.signatures.count()
issue_num_signatures.short_description = '# signatures (unverified)'

def issue_members(issue):
    m = ((issue.sunetid1, issue.name1), (issue.sunetid2, issue.name2), (issue.sunetid3, issue.name3), 
         (issue.sunetid4, issue.name4), (issue.sunetid5, issue.name5))
    return ', '.join(['%s (%s)' % (s,n) for (s,n) in m if s])
issue_members.short_description = 'Candidate/members/sponsors'      

class IssueAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ('title', 'kind', 'slug', 'public', 'admin_notes')}),
        ('Electorate', {'fields': ('electorates',)}),
        ('Person 1', {'fields': ('name1', 'sunetid1',)}),
        ('People 2-5', {'fields': ('name2', 'sunetid2',
                                   'name3', 'sunetid3',
                                   'name4', 'sunetid4',
                                   'name5', 'sunetid5',)}),
        ('Statement', {'fields': ('statement', 'image', )}),
        ('Misc.', {'fields': ('signed_qualifications',)}),
        ('Petition', {'fields': ('petition_validated', 'petition_signatures_count')}),
        ('Special Fee group', {'fields': ('total_request_amount', 'total_past_request_amount', 'declared_petition',
                                          'budget', 'past_budget', 'account_statement',
                                          'advisory_vote_gsc', 'advisory_vote_senate',
                                          'statement_gsc','statement_senate','petition_required')}),
    ]
    prepopulated_fields = {'slug': ('title',)}
    save_on_top = True
    list_display = ('title', 'kind', issue_members, 'public', 'admin_notes')
    #list_editable = ('electorates',)
    list_filter = ('kind',)
    list_per_page = 200

admin.site.register(Issue, IssueAdmin)
