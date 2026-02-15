from django.forms import ModelForm
from core.models import Lead


class LeadForm(ModelForm):
    class Meta:
        model = Lead
        fields = ['first_name', 'last_name', 'phone', 'email', 'gclid']


class BookingLeadForm(ModelForm):
    class Meta:
        model = Lead
        fields = ['first_name', 'last_name', 'phone', 'email', 'gclid',
                  'postal_code', 'date1', 'date2', 'date3']


