from django.forms import ModelForm
from core.models import Lead


class LeadForm(ModelForm):
    class Meta:
        model = Lead
        # fields = ['first_name', 'last_name', 'phone', 'email', 'postal_code', 'address', 'location', 'gclid']
        fields = [ 'first_name', 'last_name', 'phone', 'email', 'state', 'zip_code', 'accept_privacy_policy','additional_comments','gclid']


