from django.forms import ModelForm
from core.models import Lead


class LeadForm(ModelForm):
    class Meta:
        model = Lead
        fields = ['first_name', 'last_name', 'postal_code', 'address', 'location', 'phone', 'email', 'gclid', 'adgroup', 'keyword', 'campaign']

