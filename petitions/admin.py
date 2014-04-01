from petitions.models import Signature
from django.contrib import admin
from petitions.models import PaperSignature, ValidationResult

class SignatureAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Signer', {'fields': ('name', 'sunetid', 'electorate')}),
        ('Issue', {'fields': ('issue',)}),
    ]
    list_display = ('sunetid', 'name', 'electorate', 'issue', 'ip_address', 'signed_at')
    list_filter = ('issue', 'electorate')
    search_fields = ('sunetid', 'name')
    list_per_page = 20000;

admin.site.register(Signature, SignatureAdmin)
admin.site.register(PaperSignature)
admin.site.register(ValidationResult)
