from django.forms import ModelForm
from core.models import Lead


class LeadForm(ModelForm):
    class Meta:
        model = Lead
        fields = ['first_name', 'last_name', 'phone', 'email', 'gender', 'gclid','source']

