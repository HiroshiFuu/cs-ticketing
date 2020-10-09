# Overrides
from .settings import *  # noqa: F401

SECRET_KEY = 'lksdf98wrhkjs88dsf8-324ksdm'

DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'local.sqlite3',
    }
}

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
EMAIL_FILE_PATH = os.path.join(BASE_DIR, 'sent_emails')
print('EMAIL_FILE_PATH', EMAIL_FILE_PATH)

# TODO-specific settings
TICKET_STAFF_ONLY = True
TICKET_DEFAULT_ASSIGNEE = None
TICKET_PUBLIC_SUBMIT_REDIRECT = 'ticket:mine'
# TICKET_ALLOW_FILE_ATTACHMENTS = True
# TICKET_LIMIT_FILE_ATTACHMENTS = [".jpg", ".gif", ".png", ".csv", ".pdf"]
# TICKET_MAXIMUM_ATTACHMENT_SIZE = 5000000  # In bytes