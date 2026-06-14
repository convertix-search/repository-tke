from django.template.loader import render_to_string
from django.core.mail import EmailMessage
import datetime
import sentry_sdk


def send_email(subject, _from, to, template, context, cc=None, bcc=None, reply_to=None):
    try:
        email_rendered = render_to_string(template, context)
        email = EmailMessage(subject, email_rendered, from_email=_from, to=to, cc=cc, bcc=bcc, reply_to=reply_to,)
        email.content_subtype = 'html'
        email.send(fail_silently=False)
        return True
    except Exception as exc:
        with sentry_sdk.push_scope() as scope:
            scope.set_tag('component', 'email')
            scope.set_extra('subject', subject)
            scope.set_extra('from', _from)
            scope.set_extra('to', to)
            scope.set_extra('template', template)
            sentry_sdk.capture_exception(exc)
        return False


def parse_date(date, time):
    time = convert24(time)
    date = date + 'T' + time[:5]
    date = datetime.datetime.strptime(date, '%Y-%m-%dT%H:%M')
    return date


def convert24(str1):
    # Checking if last two elements of time
    # is AM and first two elements are 12
    if str1[-2:] == "AM" and str1[:2] == "12":
        return "00" + str1[2:-2]

    # remove the AM
    elif str1[-2:] == "AM":
        return str1[:-2]

    # Checking if last two elements of time
    # is PM and first two elements are 12
    elif str1[-2:] == "PM" and str1[:2] == "12":
        return str1[:-2]

    else:

        # add 12 to hours and remove PM
        return str(int(str1[:2]) + 12) + str1[2:8]
