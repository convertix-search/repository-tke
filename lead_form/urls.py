"""lead_form URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import path

from core import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('forms/<int:form_id>/thank-you/', views.thank_you, name='thank_you'),
    path('questions-progress/<int:form_id>', views.save_progress_api, name='save_progress'),
    path('progress-add/<int:progress_id>', views.increment_answered_question_count, name='update_progress'),
    path('progress-data/', views.get_all_progress_data, name='progress-data'),
    path('admin/progress-view/', views.progress_data, name='progress-data-get'),
    path('unbounce-lead/', views.unbounce_lead, name='unbounce_lead'),
    path('calendar/', views.get_month_calendar, name='get_month_calendar'),
    path('', views.index, name='index'),
]

urlpatterns += staticfiles_urlpatterns()
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
