from django import forms

from client_area.models import Industry, Service, Language, ClientType
from user_management.models import Member, Team

# Only used for validation, form will be created manually
class NewClientForm(forms.Form):
    account_name  = forms.CharField(label='Account name', max_length=100, required=False)
    budget        = forms.IntegerField(label='Budget', required=False)
    team          = forms.ModelChoiceField(queryset=Team.objects.all(), required=False)
    client_type   = forms.ModelChoiceField(queryset=ClientType.objects.all(), required=False)
    industry      = forms.ModelChoiceField(queryset=Industry.objects.all(), required=False)
    language      = forms.ModelChoiceField(queryset=Language.objects.all(), required=False)
    contact_email = forms.EmailField(max_length=255, required=False)
    contact_name  = forms.CharField(max_length=255, required=False)
    tier          = forms.IntegerField(required=False)
    sold_by       = forms.ModelChoiceField(queryset=Member.objects.all(), required=False)
    services      = forms.ModelChoiceField(queryset=Service.objects.all(), required=False)
    status        = forms.IntegerField(required=False)
    client_grade  = forms.IntegerField(required=False)
