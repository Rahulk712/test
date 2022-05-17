from django.contrib import admin
from django.forms import forms, ModelForm, Select
from django.contrib import admin
from apis.models import CandidateDetails
from import_export.admin import ImportExportModelAdmin
from import_export import resources, fields
from django.utils.translation import ugettext_lazy as _

# Register your models here.
class CandidateDetailsResource(resources.ModelResource):
    name = fields.Field(column_name=_('Name'), attribute='name')
    email = fields.Field(column_name=_('Candidate Email'), attribute='email')
    mobile_no = fields.Field(column_name=_('Mobile No'), attribute='mobile_no')
    from_email = fields.Field(column_name=_('From Email'), attribute='from_email')
    to_email = fields.Field(column_name=_('To Email'), attribute='to_email')
    email_subject = fields.Field(column_name=_('Subject'), attribute='email_subject')
    resume = fields.Field(column_name=_('Resume path'), attribute='resume')
    created_date = fields.Field(column_name=_('Created Date'), attribute='created_date')
    
    class Meta:
        model = CandidateDetails
        fields = ('name', 'email','mobile_no','resume','created_date',)
        import_id_fields = fields
        export_order = fields
    
class CandidateDetailsAdmin(ImportExportModelAdmin):
    resource_class = CandidateDetailsResource
    list_display = ('name', 'email','mobile_no','resume','created_date')
    search_fields = ('email','mobile_no','created_date')

admin.site.register(CandidateDetails, CandidateDetailsAdmin)
