# Overrides
from .settings import *  # noqa: F401

SECRET_KEY = 'lksdf98wrhkjs88dsf8-324ksdm'

DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'gtd',
        'USER': 'you',
        'PASSWORD': '',
        'HOST': '127.0.0.1',
        'PORT': '',
    },
}

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# TODO-specific settings
TICKET_STAFF_ONLY = False
TICKET_DEFAULT_LIST_SLUG = 'tickets'
TICKET_DEFAULT_ASSIGNEE = None
TICKET_PUBLIC_SUBMIT_REDIRECT = '/'