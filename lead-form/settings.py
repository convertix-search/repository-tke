from lead_form.settings_dev import *

DEBUG = False

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'leadformunitedkingdom',
        'USER': 'leadformunitedkingdom',
        'PASSWORD': 'wb9aYR(5Y.fpaVv7e8cs',
    }
}

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'storage/static')

STATICFILES_DIRS = [
                #    os.path.join(BASE_DIR, 'static'),
                        ]
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'storage/media')

RAVEN_CONFIG = {}
INSTALLED_APPS = INSTALLED_APPS + [
                ]

import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

sentry_sdk.init(
    dsn="https://43a84498ed074086ac923f71366ae642@o983718.ingest.sentry.io/4503885332807680",

    integrations=[DjangoIntegration()],

    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for performance monitoring.
    # We recommend adjusting this value in production.
    traces_sample_rate=0,

    # If you wish to associate users to errors (assuming you are using
    # django.contrib.auth) you may enable sending PII data.
    send_default_pii=True
)

ASIOSO_API = 'https://asioso-hs-prod.tke-stage.com/save'
ASIOSO_USER = 'hs_user'
ASIOSO_PASSWORD = 'HS_ApiRest_28.01.123#'

