import logging

from django.conf import settings
from django.utils import translation
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.clickjacking import xframe_options_exempt
from django.utils.datastructures import MultiValueDictKeyError

from requests.auth import HTTPBasicAuth
from dict2xml import dict2xml
from datetime import timezone

import sentry_sdk

from core.forms import LeadForm
from core.models import Form, FormAnswered
from core.utils import parse_date

import json
import requests


@csrf_exempt
@xframe_options_exempt
def index(request):
    form_id = request.GET.get('form_id')
    if form_id:
        try:
            form = Form.objects.get(pk=form_id)
        except ValueError:
            form = Form.objects.all().first()
        except Form.DoesNotExist:
            form = Form.objects.all().first()
    else:
        form = Form.objects.all().first()

    context = {'form': form}

    translation.activate(form.language)
    request.LANGUAGE_CODE = translation.get_language()

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
def unbounce_lead_fr(request):
    unbounce_data = json.loads(request.POST['data.json'])
    date = parse_date(unbounce_data['date_submitted'][0], unbounce_data['time_submitted'][0][:8])
    data = {
        'bought_at': date.strftime('%Y-%m-%dT%H:%M:%SZ'),
        'bought_at_unix': date.replace(tzinfo=timezone.utc).timestamp(),
        'offer_contact': {
            'country': 'Belgium',
            'country_code': 'fr_be',
            'email': unbounce_data['email'],
            'phone': unbounce_data['numéro_de_téléphone'],
        },
    }

    if unbounce_data.get('gclid'):
        data['lead_id'] = unbounce_data['gclid']

    if unbounce_data.get('prénom_et_nom'):
        data['offer_contact']['first_name'] = unbounce_data['prénom_et_nom']
    elif unbounce_data.get('prénom'):
        data['offer_contact']['first_name'] = unbounce_data['prénom']

        if unbounce_data.get('nom'):
            data['offer_contact']['last_name'] = unbounce_data['nom']

    if unbounce_data.get('code_postal_et_ville'):
        data['offer_contact']['city'] = unbounce_data['code_postal_et_ville']

    if unbounce_data.get('rue_et_numéro'):
        data['offer_contact']['address'] = unbounce_data['rue_et_numéro']

    if unbounce_data.get('code_postal'):
        data['offer_contact']['zip_code'] = unbounce_data['code_postal']

    return send_lead_to_api(data)


@csrf_exempt
def unbounce_lead_nl(request):
    
    unbounce_data = {}
    try:        
        unbounce_data = json.loads(request.POST['data.json'])        
    except MultiValueDictKeyError as e:
        unbounce_data = json.loads(request.POST['Data.json'])    
        
    date = parse_date(unbounce_data['date_submitted'][0], unbounce_data['time_submitted'][0][:8])
    data = {
        'bought_at': date.strftime('%Y-%m-%dT%H:%M:%SZ'),
        'bought_at_unix': date.replace(tzinfo=timezone.utc).timestamp(),
        'offer_contact': {
            'country': 'Belgium',
            'country_code': 'nl_be',
            'email': unbounce_data.get('email', ''),
            'phone': unbounce_data.get('telefoonnummer', ''),
        },
    }

    if unbounce_data.get('gclid'):
        data['lead_id'] = unbounce_data['gclid']

    if unbounce_data.get('voor_en_achternaam'):
        data['offer_contact']['first_name'] = unbounce_data['voor_en_achternaam']
    elif unbounce_data.get('voornaam'):
        data['offer_contact']['first_name'] = unbounce_data['voornaam']
        if unbounce_data.get('achternaam'):
            data['offer_contact']['last_name'] = unbounce_data['achternaam']

    if unbounce_data.get('straat_en_huisnummer'):
        data['offer_contact']['address'] = unbounce_data['straat_en_huisnummer']

    if unbounce_data.get('postcode_en_stad'):
        data['offer_contact']['city'] = unbounce_data['postcode_en_stad']

    if unbounce_data.get('postcode'):
        data['offer_contact']['zip_code'] = unbounce_data['postcode']

    return send_lead_to_api(data)


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
    context = {'form_answered': form_answered, 'form': form_answered.form}
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

