from lead_form.settings_dev import *

DEBUG = False

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'leadformbelgium',
        'USER': 'leadformbelgium',
        'PASSWORD': 'w495R5YfpVv7e8ics',
    }
}

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'storage/static')

STATICFILES_DIRS = [
                #    os.path.join(BASE_DIR, 'static'),
                        ]
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'storage/media')

RAVEN_CONFIG = {
            }
INSTALLED_APPS = INSTALLED_APPS + [
                ]
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

sentry_sdk.init(
        dsn="https://df5673cbc10eb3bb59b84cb4790e1191@o4507856253288448.ingest.us.sentry.io/4507856254337024",
        #dsn="https://18e3d3bca9f86a26512b92fedf820906@o4506615652679680.ingest.sentry.io/4506615663624192",
        integrations=[DjangoIntegration()],
        # Set traces_sample_rate to 1.0 to capture 100%
        # of transactions for performance monitoring.
        
        # We recommend adjusting this value in production.
        traces_sample_rate=0.1,

        # If you wish to associate users to errors (assuming you are using
        # django.contrib.auth) you may enable sending PII data.
        send_default_pii=True
)

ASIOSO_API = 'https://asioso-hs-prod.tke-stage.com/save'
ASIOSO_USER = 'hs_user'
ASIOSO_PASSWORD = 'HS_ApiRest_28.01.123#'

