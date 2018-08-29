from django.forms import ModelForm
from .models import Team

class TeamForm(forms.ModelForm):
    class Meta:
        model = Team
