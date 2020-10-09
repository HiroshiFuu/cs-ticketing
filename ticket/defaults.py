# If a documented cs-support-ticket option is NOT configured in settings, use these values.
from django.conf import settings

hash = {
    "TICKET_ALLOW_FILE_ATTACHMENTS": True,
    "TICKET_COMMENT_CLASSES": [],
    "TICKET_DEFAULT_ASSIGNEE": None,
    "TICKET_LIMIT_FILE_ATTACHMENTS": [".jpg", ".gif", ".png", ".csv", ".pdf", ".zip"],
    "TICKET_MAXIMUM_ATTACHMENT_SIZE": 5000000,
    "TICKET_PUBLIC_SUBMIT_REDIRECT": "/",
    "TICKET_STAFF_ONLY": True,
}

# These intentionally have no defaults (user MUST set a value if their features are used):
# TICKET_DEFAULT_LIST_SLUG
# TICKET_MAIL_BACKENDS
# TICKET_MAIL_TRACKERS


def defaults(key: str):
    """Try to get a setting from project settings.
    If empty or doesn't exist, fall back to a value from defaults hash."""

    if hasattr(settings, key):
        val = getattr(settings, key)
    else:
        val = hash.get(key)
    return val
