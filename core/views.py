import json
from datetime import timezone

import requests
from dict2xml import dict2xml
from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render, redirect
from requests.auth import HTTPBasicAuth

from core.forms import LeadForm
from core.models import Form, FormAnswered
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.clickjacking import xframe_options_exempt

from core.utils import parseDate

dumy = {
    'time_submitted': ['12:39 PM UTC'],
    'page_uuid': ['344a0d87-71af-4a56-a960-49f231a23a51'],
    'email': ['john.test@samplemail.com'],
    'page_name': ['PIATTAFORMA SEA [SEARCH] Bing Short'],
    'date_submitted': ['2022-01-24'],
    'telefono': ['+4912341234'],
    'gclid': [''],
    'privacy_policy': ['Dichiaro di aver preso visione della <a href="https://homesolutions.tkelevator.com/it-it/privacy-policy/"> privacy policy</a> di TK Home Solutions S.r.l. a Socio Unico.'],
    'nome_e_cognome': ['John Test'],
    'utm_source': ['google'],
    'address': ['Samplestreet 100'],
    'zip_code': ['01234'],
    'città': ['Samplecity'],
    'utm_medium': ['cpc'],
    'ip_address': ['109.107.111.45'],
    'page_url': ['http://piattaforme.tkelevator.com/bing-short/'],
    'variant': ['c']
}


dumy_germany = {
    'time_submitted': ['12:39 PM UTC'],
    'page_uuid': ['344a0d87-71af-4a56-a960-49f231a23a51'],
    'email': ['john.test@samplemail.com'],
    'page_name': ['PIATTAFORMA SEA [SEARCH] Bing Short'],
    'date_submitted': ['2022-01-24'],
    'telefono': ['+4912341234'],
    'gclid': ['ed5ed86c-05dd-45b8-9b6d-59d67c8fab1d'],
    'privacy_policy': ['Dichiaro di aver preso visione della <a href="https://homesolutions.tkelevator.com/it-it/privacy-policy/"> privacy policy</a> di TK Home Solutions S.r.l. a Socio Unico.'],
    'nome_e_cognome': ['John Test'],
    'utm_source': ['google'],
    'address': ['Samplestreet 100'],
    'zip_code': ['01234'],
    'città': ['Samplecity'],
    'utm_medium': ['cpc'],
    'ip_address': ['109.107.111.45'],
    'page_url': ['http://piattaforme.tkelevator.com/bing-short/'],
    'variant': ['c']
}

HEADERS = {
    'Content-Type': 'text/xml',
    'Authorization': 'Basic YXBpVXNlcjphcGlVc2VyMTIzIw=='
}


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
    unbounce_data = json.loads(request.POST['data.json'])
    date = parseDate(unbounce_data['date_submitted'][0], unbounce_data['time_submitted'][0][:8])
    data = {
        'bought_at': date.strftime('%Y-%m-%dT%H:%M:%SZ'),
        'bought_at_unix': date.replace(tzinfo=timezone.utc).timestamp(),
        'offer_contact': {
            'first_name': unbounce_data['name__vorname'],
            'address': unbounce_data['straße__nr'],
            'zip_code': unbounce_data['plz_'],
            'city': unbounce_data['ort_'],
            'country': 'Germany',
            'country_code': 'de',
            'email': unbounce_data['email'],
            'phone': unbounce_data['telefon'],
        },
    }

    if unbounce_data.get('gclid'):
        data['lead_id'] = unbounce_data['gclid']

    if unbounce_data.get('lead_source'):
        data.update({'lead_source_code': unbounce_data['lead_source']})

    return send_lead_to_api(data)


@csrf_exempt
def unbounce_lead_italy(request):
    unbounce_data = json.loads(request.POST['data.json'])
    date = parseDate(unbounce_data['date_submitted'][0], unbounce_data['time_submitted'][0][:8])
    data = {
        'bought_at': date.strftime('%Y-%m-%dT%H:%M:%SZ'),
        'bought_at_unix': date.replace(tzinfo=timezone.utc).timestamp(),
        'offer_contact': {
            'country': 'Italy',
            'country_code': 'it',
            'email': unbounce_data['email'],
            'phone': unbounce_data['telefono'],
        },
    }

    if unbounce_data.get('gclid'):
        data['lead_id'] = unbounce_data['gclid']

    if unbounce_data.get('lead_source'):
        data['lead_source_code'] = unbounce_data['lead_source']

    if unbounce_data.get('nome_e_cognome'):
        data['offer_contact']['first_name'] = unbounce_data['nome_e_cognome']

    elif unbounce_data.get('nome'):
        data['offer_contact']['first_name'] = unbounce_data['nome']

    if unbounce_data.get('città'):
        data['offer_contact']['city'] = unbounce_data['città']

    if unbounce_data.get('indirizzo'):
        data['offer_contact']['address'] = unbounce_data['indirizzo']

    if unbounce_data.get('codice_postale'):
        data['offer_contact']['zip_code'] = unbounce_data['codice_postale']

    return send_lead_to_api_test(data)


@csrf_exempt
def unbounce_lead_netherlands(request):
    unbounce_data = json.loads(request.POST['data.json'])
    date = parseDate(unbounce_data['date_submitted'][0], unbounce_data['time_submitted'][0][:8])
    data = {
        'bought_at': date.strftime('%Y-%m-%dT%H:%M:%SZ'),
        'bought_at_unix': date.replace(tzinfo=timezone.utc).timestamp(),
        'offer_contact': {
            'country': 'Netherlands',
            'country_code': 'nl',
        },
    }

    if unbounce_data.get('email'):
        data['offer_contact']['email'] = unbounce_data['email']

    if unbounce_data.get('emailadres'):
        data['offer_contact']['email'] = unbounce_data['emailadres']

    if unbounce_data.get('telefoon'):
        data['offer_contact']['phone'] = unbounce_data['telefoon']

    if unbounce_data.get('telefoonnummer'):
        data['offer_contact']['phone'] = unbounce_data['telefoonnummer']

    if unbounce_data.get('gclid'):
        data['lead_id'] = unbounce_data['gclid']

    if unbounce_data.get('voor_en_achternaam'):
        data['offer_contact']['first_name'] = unbounce_data['voor_en_achternaam']

    return send_lead_to_api_test(data)


@xframe_options_exempt
def thank_you(request, form_id):
    form_answered = FormAnswered.objects.get(pk=form_id)
    context = {'form_answered': form_answered}
    return render(request, 'core/thank-you.html', context)


def send_lead_to_api_test(data):
    xml = dict2xml(data, wrap='lead')
    headers = {'Content-Type': 'text/xml'}
    response = requests.post('https://asioso-hspre.tke-stage.com/save',
                             data=xml.encode(),
                             headers=headers,
                             auth=HTTPBasicAuth('apiUser', 'apiUser123#'))
    return HttpResponse(status=200)


def send_lead_to_api(data):
    xml = dict2xml(data, wrap='lead')
    headers = {'Content-Type': 'text/xml'}
    response = requests.post(settings.ASIOSO_API,
                             data=xml.encode(),
                             headers=headers,
                             auth=HTTPBasicAuth(settings.ASIOSO_USER, settings.ASIOSO_PASSWORD))
    return HttpResponse(status=200)


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[-1].strip()
    elif request.META.get('HTTP_X_REAL_IP'):
        ip = request.META.get('HTTP_X_REAL_IP')
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

