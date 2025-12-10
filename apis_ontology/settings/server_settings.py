import os
from apis_acdhch_default_settings.settings import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

APIS_BASE_URI = "https://nomansland-dev.acdh-ch-dev.oeaw.ac.at/"

ROOT_URLCONF = "apis_ontology.urls"
CSRF_TRUSTED_ORIGINS = [
    "https://nomansland.acdh-ch-dev.oeaw.ac.at",
    "https://nomansland-dev-main.acdh-ch-dev.oeaw.ac.at",
]

ADDITIONAL_APPS = [
    "django.contrib.postgres",
    "apis_core.collections",
    "apis_core.history",
    "django_interval",
    "apis_core.documentation",
    "apis_bibsonomy",
]

for app in ADDITIONAL_APPS:
    if app not in INSTALLED_APPS:
        INSTALLED_APPS.append(app)

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "[%(levelname)-8s %(asctime)s] %(name)-6s %(message)s",
            "datefmt": "%y-%m-%d %H:%M %Z",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "DEBUG",
    },
}

LOG_LIST_NOSTAFF_EXCLUDE_APP_LABELS = ["admin", "sessions", "auth"]

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    },
    "select2": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "TIMEOUT": 60 * 60 * 24,  # Timeout set to 1 day (in seconds)
    },
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

APIS_BIBSONOMY = [
    {
        "type": "zotero",
        "url": "https://api.zotero.org",
        "user": os.environ.get("APIS_BIBSONOMY_USER"),
        "API key": os.environ.get("APIS_BIBSONOMY_PASSWORD"),
        "group": "2801369",
    }
]

AUDITLOG_LOGENTRY_MODEL = os.environ.get("AUDITLOG_LOGENTRY_MODEL", "auditlog.LogEntry")
