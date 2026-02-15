from datetime import datetime
from django import template

register = template.Library()


@register.filter
def is_working_day(date):
    return True if date.weekday() <= 4 else False


@register.filter
def is_weekend(date):
    return True if date.weekday() > 4 else False


@register.filter
def is_different_month(date, month):
    if date.month != month:
        return True
    return False


@register.filter
def is_past(date):
    if date <= datetime.today().date():
        return True
    return False


