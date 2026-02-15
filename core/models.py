from django.conf import settings
from django.db import models
from core.utils import send_email
from requests.auth import HTTPBasicAuth
from dict2xml import dict2xml
from datetime import timezone
from constance import config
import requests


# -------FORM TEMPLATES START

class Form(models.Model):
    STYLE_A = 1
    STYLES = [
        (STYLE_A, 'Style A'),
    ]

    # GERMANY = 1
    # SPAIN = 2
    # COUNTRIES = [
    #     (GERMANY, 'Germany'),
    #     (SPAIN, 'Spain'),
    # ]

    name = models.CharField(max_length=200)
    subtitle = models.CharField(max_length=200, blank=True)
    subject = models.CharField(max_length=128, blank=True)
    contact_form_title = models.CharField(max_length=128, blank=True)
    contact_form_button_title = models.CharField(max_length=128, blank=True)
    brand_name = models.CharField(max_length=128, blank=True)
    created = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    questions = models.ManyToManyField('core.Question', blank=True)
    order = models.IntegerField(default=0)
    style = models.IntegerField(choices=STYLES, default=STYLE_A)
    contact_people = models.ManyToManyField('core.FormContactPerson', blank=True)
    external_thank_you_page = models.URLField(blank=True, null=True)
    contact_title = models.CharField(max_length=200, blank=True)
    contact_subtitle = models.CharField(max_length=200, blank=True)

    # country = models.IntegerField(choices=COUNTRIES, default=GERMANY)

    class Meta:
        verbose_name = 'Form'
        verbose_name_plural = 'Forms'
        ordering = ['order']

    def __str__(self):
        return u'{}'.format(self.name)


class Question(models.Model):
    name = models.CharField(max_length=128)
    order = models.IntegerField(default=0)
    created = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    special = models.BooleanField(u'Tipo escalera', default=False)
    special2 = models.BooleanField(u'Ubicación escalera', default=False)

    class Meta:
        verbose_name = 'Question'
        verbose_name_plural = 'Questions'
        ordering = ['order']

    def __str__(self):
        return u'{} - {}'.format(self.id, self.name)


class Answer(models.Model):
    name = models.CharField(max_length=128)
    value = models.CharField(max_length=64)
    points = models.IntegerField(default=0)
    image = models.ImageField(null=True, blank=True, upload_to='answers/')
    order = models.IntegerField(default=0)
    created = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    question = models.ForeignKey('core.Question', on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Answer'
        verbose_name_plural = 'Answers'
        ordering = ['order']

    def __str__(self):
        return u'{}'.format(self.name)

# -------FORM TEMPLATES END


# -------LEAD START

class Lead(models.Model):
    first_name = models.CharField(max_length=64)
    last_name = models.CharField(max_length=64, blank=True)
    postal_code = models.CharField(max_length=16, blank=True)
    address = models.CharField(max_length=128, blank=True)
    location = models.CharField(max_length=128, blank=True)
    county = models.CharField(max_length=128, blank=True)
    phone = models.CharField(max_length=16)
    email = models.EmailField(blank=True)
    created = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    gclid = models.CharField(max_length=256, blank=True)

    class Meta:
        verbose_name = 'Lead'
        verbose_name_plural = 'Leads'
        ordering = ['-created', 'first_name', 'last_name']

    def __str__(self):
        return u'{} {}'.format(self.first_name, self.last_name)


class FormAnswered(models.Model):
    lead = models.ForeignKey('core.Lead', on_delete=models.CASCADE)
    form = models.ForeignKey('core.Form', on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    answers = models.ManyToManyField('core.Answer')
    accept_privacy_policy = models.BooleanField(default=True)
    ip_address = models.GenericIPAddressField()

    class Meta:
        verbose_name = 'Form answered'
        verbose_name_plural = 'Forms answered'
        ordering = ['created']

    def __str__(self):
        return u'{} - {}'.format(self.lead, self.form)

    def send_mail_to_admins(self):
        managers = self.form.contact_people.all()
        managers = list(manager.email for manager in managers)
        context = {
            'lead': self.lead,
            'form': self
        }
        send_email(
            subject='%s: #%s Lead Form Widget' % (self.form.subject, self.id),
            _from=config.FROM_EMAIL,
            to=managers,
            template='core/emails/communicate_lead_to_admin.html',
            context=context
        )

    def send_lead_by_api(self):
        data = {
            'lead_id': 'widget ' + str(self.lead.id),
            'bought_at': self.created.strftime('%Y-%m-%dT%H:%M:%SZ'),
            'bought_at_unix': self.created.replace(tzinfo=timezone.utc).timestamp(),
            'offer_contact': {
                'first_name': self.lead.first_name,
                'last_name': self.lead.last_name,
                'address': self.lead.address,
                'zip_code': self.lead.postal_code,
                'country': 'Spain',
                'country_code': 'es',
                'email': self.lead.email,
                'phone': self.lead.phone,
            },
        }

        if self.lead.gclid:
            data['lead_id'] = 'widget - %s' % self.lead.gclid

        xml = dict2xml(data, wrap='lead')
        headers = {'Content-Type': 'text/xml'}
        response = requests.post(settings.ASIOSO_API,
                                 data=xml.encode(),
                                 headers=headers,
                                 auth=HTTPBasicAuth(settings.ASIOSO_USER, settings.ASIOSO_PASSWORD))
        aux = response

    @property
    def total_points(self):
        answers = self.answers.aggregate(total_points=models.Sum('points'))
        return answers["total_points"]

# -------LEAD END


class FormContactPerson(models.Model):
    first_name = models.CharField(max_length=64, blank=True)
    last_name = models.CharField(max_length=64, blank=True)
    phone = models.CharField(max_length=16, blank=True)
    email = models.EmailField(max_length=64, unique=True)

    class Meta:
        verbose_name = 'Form contact person'
        verbose_name_plural = 'Form contact people'
        ordering = ['email']

    def __str__(self):
        return u'{}'.format(self.email)




