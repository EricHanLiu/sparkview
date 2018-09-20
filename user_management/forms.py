from django import forms
from .models import Team, Member

class NewTeamForm(forms.ModelForm):
    class Meta:
        model = Team
        exclude = ()

class NewMemberForm(forms.ModelForm):
    class Meta:
        model = Member
        exclude = ()
