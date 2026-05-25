from django.forms import ModelForm
from core.models import Lead


class LeadShortForm(ModelForm):
    class Meta:
        model = Lead
        fields = ['first_name', 'phone', 'email', 'address', 'postal_code', 'gclid', 'msclkid']


class LeadForm(ModelForm):
    class Meta:
        model = Lead
        fields = ['first_name', 'last_name', 'phone', 'email', 'address', 'postal_code', 'gclid', 'msclkid']

