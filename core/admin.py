from django.contrib import admin

# Register your models here.
from core.models import Lead, Answer, Form, Question, FormAnswered, FormContactPerson


@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    search_fields = ('first_name', 'last_name', 'email', 'phone')
    list_display = ('first_name', 'last_name', 'phone', 'email', 'get_form_answered_id', 'gclid', 'msclkid', 'created')
    list_filter = ('created', 'formanswered__form__subject')

    def get_form_answered_id(self, obj):
        form_answered = FormAnswered.objects.filter(lead=obj).first()  # Get the first related FormAnswered entry
        return form_answered.form.id if form_answered else 'No Form Answered'
    
    get_form_answered_id.short_description = 'Configuration ID'


@admin.register(Form)
class FormAdmin(admin.ModelAdmin):
    search_fields = ('name',)
    list_display = ('id', 'name', 'subtitle', 'subject', 'contact_form_title',
                    'product_type', 'type', 'language', 'order', 'created')
    list_filter = ('created', 'product_type', 'language', 'type',)
    filter_horizontal = ('questions', 'contact_people',)


class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 1


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    search_fields = ('name',)
    list_display = ('name', 'language', 'order', 'created')
    list_filter = ('created', 'language',)
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
