from django.contrib import admin

# Register your models here.
from core.models import Lead, Answer, Form, Question, FormAnswered, FormContactPerson


@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    search_fields = ('first_name', 'last_name', 'email', 'phone', 'county')
    list_display = ('first_name', 'last_name', 'phone', 'county', 'email', 'gclid', 'created')
    list_filter = ('created', 'formanswered__form__subject')


@admin.register(Form)
class FormAdmin(admin.ModelAdmin):
    search_fields = ('name',)
    list_display = ('id', 'name', 'subtitle', 'subject', 'contact_form_title', 'style', 'order', 'created')
    list_filter = ('created', 'style',)
    filter_horizontal = ('questions', 'contact_people',)


class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 1


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    search_fields = ('name',)
    list_display = ('name', 'order', 'created')
    list_filter = ('created',)
    inlines = [AnswerInline]


@admin.register(FormAnswered)
class FormAnsweredAdmin(admin.ModelAdmin):
    search_fields = ('lead__first_name',)
    list_display = ('lead', 'form', 'total_points', 'accept_privacy_policy', 'ip_address', 'created')
    list_filter = ('created', 'accept_privacy_policy', 'form__subject')
    filter_horizontal = ('answers',)
    readonly_fields = ('accept_privacy_policy', 'ip_address')


@admin.register(FormContactPerson)
class FormContactPersonAdmin(admin.ModelAdmin):
    search_fields = ('first_name', 'last_name', 'phone', 'email',)
    list_display = ('email', 'first_name', 'last_name', 'email', 'phone')
