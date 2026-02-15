import calendar

from requests.auth import HTTPBasicAuth
from dict2xml import dict2xml
from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.http import JsonResponse
from core.forms import LeadForm, BookingLeadForm
from django.contrib.auth.decorators import login_required
from core.models import Form, FormAnswered, Answer,QuestionProgress
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.clickjacking import xframe_options_exempt
from core.utils import parse_date, WEEK_DAYS, MONTHS
from datetime import timezone, datetime
from decimal import Decimal, ROUND_HALF_UP
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

    context = {'form': form,'form_id':form_id}

    if request.POST:
        # Create the Lead
        if form.type == Form.STANDARD:
            lead_form = LeadForm(request.POST)
        else:
            data = request.POST.copy()
            dates = request.POST['dates'].split(',')
            data['date1'] = dates[0]
            data['date2'] = dates[1]
            data['date3'] = dates[2]
            lead_form = BookingLeadForm(data)

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

    if form.type == Form.BOOKING:
        today = datetime.today()
        month = calendar.Calendar(firstweekday=0)
        month = month.monthdatescalendar(year=int(today.year), month=int(today.month))

        context.update({
            'month': month,
            'months': MONTHS,
            'week_days': WEEK_DAYS,
            'month_number': today.month,
            'month_name': MONTHS[today.month-1],
            'year': today.year,
            'previous': False
        })

    return render(request, 'core/form.html', context)


@csrf_exempt
@xframe_options_exempt
def get_month_calendar(request):
    previous = True
    today = datetime.today()
    year = int(request.GET['year'])
    month_number = int(request.GET['month'])

    if year < today.year or year == today.year and month_number <= today.month:
        previous = False

    month = calendar.Calendar(firstweekday=0)
    month = month.monthdatescalendar(year=year, month=month_number)

    context = {
        'month': month,
        'months': MONTHS,
        'week_days': WEEK_DAYS,
        'month_number': month_number,
        'month_name': MONTHS[month_number-1],
        'year': year,
        'previous': previous
    }

    return render(request, 'core/block/month.html', context)


@csrf_exempt
def unbounce_lead(request):
    unbounce_data = json.loads(request.POST['data.json'])
    date = parse_date(unbounce_data['date_submitted'][0], unbounce_data['time_submitted'][0][:8])
    data = {
        'bought_at': date.strftime('%Y-%m-%dT%H:%M:%SZ'),
        'bought_at_unix': date.replace(tzinfo=timezone.utc).timestamp(),
        'offer_contact': {
            'country': 'Spain',
            'country_code': 'es',
            'phone': unbounce_data['teléfono'],
        },
    }

    if unbounce_data.get('gclid'):
        data['lead_id'] = unbounce_data['gclid']

    if unbounce_data.get('nombre_y_apellidos'):
        data['offer_contact']['first_name'] = unbounce_data['nombre_y_apellidos']

    if unbounce_data.get('email'):
        data['offer_contact']['email'] = unbounce_data['email']

    return send_lead_to_api(data)


@csrf_exempt
def save_progress_api(request, form_id):
    if request.method == 'POST':
        try:
            form = Form.objects.get(id=form_id)
        except Form.DoesNotExist:
            return JsonResponse({'error': 'Form not found'}, status=404)

        total_questions = form.questions.count()

        progress = QuestionProgress.objects.create(form=form)

            
        progress.answered_question_count = 0
        progress.total = total_questions
        progress.save()
      
        tracking_data = {
            'progress_session_id': progress.id,
            'answered_question_count': progress.answered_question_count,
            'total': progress.total,
          
        }
        return JsonResponse({'success': 'Progress saved','new_id':progress.id, 'progress_id':tracking_data })

from decimal import Decimal, ROUND_HALF_UP
from django.http import JsonResponse
from collections import defaultdict

@csrf_exempt
def get_all_progress_data(request):
    if request.method == 'GET':
        progress_data = list(QuestionProgress.objects.values())
        form_progress = {}

        for progress in progress_data:
            form_id = progress['form_id']
            total = Decimal(progress['total'])
            answered = Decimal(progress['answered_question_count'])
            if total > 0:
                progress['progress'] = (answered / total * 100).quantize(Decimal('0.00'), rounding=ROUND_HALF_UP)
            else:
                progress['progress'] = 0
            if total > 0:
                progress_percentage = (answered / total * 100).quantize(Decimal('0.00'), rounding=ROUND_HALF_UP)
            else:
                progress_percentage = 0
            
            form_progress.setdefault(form_id, [])
            form_progress[form_id].append(progress_percentage)
        
        overall_progress = {}
        result_data = []
        
        for form_id, progress_list in form_progress.items():
            overall_progress[form_id] = str(sum(progress_list) / len(progress_list))
            result_data.append({
                'form_id': form_id,
                'overall_progress': overall_progress[form_id]
            })
        
        response_data = {
            'progress_data': progress_data,
            'overall_progress': result_data
        }

        return JsonResponse(response_data)




@csrf_exempt
def increment_answered_question_count(request, progress_id):
    if request.method == 'POST':
        try:
            progress = QuestionProgress.objects.get(id=progress_id)
        except QuestionProgress.DoesNotExist:
            return JsonResponse({'error': 'QuestionProgress not found'}, status=404)

        progress.answered_question_count += 1
        progress.save()

        return JsonResponse({'success': 'Answered question count incremented', 'progress_id': progress.id})


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
    special_question = Answer.objects.filter(formanswered=form_answered, question__special=True).first()
    special_question2 = Answer.objects.filter(formanswered=form_answered, question__special2=True).first()
    context = {
        'form_answered': form_answered,
        'form': form_answered.form,
        'type': special_question,
        'location': special_question2
    }
    return render(request, 'core/thank-you.html', context)


@xframe_options_exempt
@login_required(login_url='/admin')
def progress_data(request):

    return render(request, 'core/progress.html')


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[-1].strip()
    elif request.META.get('HTTP_X_REAL_IP'):
        ip = request.META.get('HTTP_X_REAL_IP')
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


