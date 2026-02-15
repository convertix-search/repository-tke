from lead_form.settings_dev import *

DEBUG = False

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'leadformfrance',
        'USER': 'leadformfrance',
        'PASSWORD': 'w495R5YfpVv7e8csa',
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
    dsn="https://4c09e9cd74ca4c1c9cfaf5c82720bb23@o983718.ingest.sentry.io/6119367",
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
