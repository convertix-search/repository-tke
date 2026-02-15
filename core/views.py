from requests.auth import HTTPBasicAuth
from dict2xml import dict2xml
from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render, redirect

from core.forms import LeadForm
from core.models import Form, FormAnswered, Answer
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.clickjacking import xframe_options_exempt
from core.utils import parse_date
from datetime import timezone

import requests
import json


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


@xframe_options_exempt
def thank_you(request, form_id):
    form_answered = FormAnswered.objects.get(pk=form_id)
    special_question = Answer.objects.filter(formanswered=form_answered, question__special=True).first()
    special_question2 = Answer.objects.filter(formanswered=form_answered, question__special2=True).first()
    context = {
        'form_answered': form_answered,
        'type': special_question,
        'location': special_question2,
        'form': form_answered.form
    }
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

