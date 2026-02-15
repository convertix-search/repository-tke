from django.conf import settings
from requests.auth import HTTPBasicAuth
from dict2xml import dict2xml
from django.shortcuts import render, redirect
from django.http import HttpResponse

from core.forms import LeadForm
from core.models import Form, FormAnswered
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.clickjacking import xframe_options_exempt
from datetime import timezone
from core.utils import parse_date

import json
import requests


@csrf_exempt
@xframe_options_exempt
def index(request):
    form_id = request.GET.get('form_id')
    if form_id:
        form = Form.objects.get(pk=form_id)
    else:
        form = Form.objects.all().first()

    context = {'form': form}

    if request.POST:
        # Create the Lead
        lead_form = LeadForm(request.POST)
        if lead_form.is_valid():
            lead = lead_form.save()

            # Create the Form Answered
            form_answered = FormAnswered.objects.create(
                lead=lead,
                form=form,
                ip_address=get_client_ip(request)
            )

            # Attach answers selected to the form answered
            for answer in request.POST.getlist('answer'):
                form_answered.answers.add(answer)

            # Send notification email to the administrators
            form_answered.send_mail_to_admins()
            form_answered.send_lead_by_api()

            return redirect('thank_you', form_id=form_answered.id)

    return render(request, 'core/form.html', context)


@csrf_exempt
def unbounce_lead(request):
    if request.POST.get('data.json'):
        unbounce_data = json.loads(request.POST['data.json'])
        date = parse_date(unbounce_data['date_submitted'][0], unbounce_data['time_submitted'][0][:8])
        data = {
            'bought_at': date.strftime('%Y-%m-%dT%H:%M:%SZ'),
            'bought_at_unix': date.replace(tzinfo=timezone.utc).timestamp(),
            'offer_contact': {
                'country': 'France',
                'country_code': 'fr',
            },
        }



        if unbounce_data.get('gclid'):
            data['lead_id'] = unbounce_data['gclid']

        if unbounce_data.get('numéro_de_téléphone'):
            data['offer_contact']['phone'] = unbounce_data['numéro_de_téléphone']

        elif unbounce_data.get('phone'):
            data['offer_contact']['phone'] = unbounce_data['phone']

        if unbounce_data.get('nom__prénom'):
            data['offer_contact']['first_name'] = unbounce_data['nom__prénom']

        if unbounce_data.get('adresse_email'):
            data['offer_contact']['email'] = unbounce_data['adresse_email']

        if unbounce_data.get('adresse_postale'):
            data['offer_contact']['address'] = unbounce_data['adresse_postale']

        if unbounce_data.get('ville'):
            data['offer_contact']['city'] = unbounce_data['ville']

        return send_lead_to_api(data)

    else:
        return HttpResponse(status=200)


def send_lead_to_api(data):
    xml = dict2xml(data, wrap='lead')
    headers = {'Content-Type': 'text/xml'}
    response = requests.post(settings.ASIOSO_API,
                             data=xml.encode(),
                             headers=headers,
                             auth=HTTPBasicAuth(settings.ASIOSO_USER, settings.ASIOSO_PASSWORD))
    return HttpResponse(status=200)


@xframe_options_exempt
def thank_you(request, form_id):
    form_answered = FormAnswered.objects.get(pk=form_id)
    context = {'form_answered': form_answered}
    return render(request, 'core/thank-you.html', context)


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[-1].strip()
    elif request.META.get('HTTP_X_REAL_IP'):
        ip = request.META.get('HTTP_X_REAL_IP')
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

