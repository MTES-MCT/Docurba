# ruff: noqa: F405 F403
from config.settings.base import *  # NOSONAR (S2208)

STORAGES["staticfiles"]["BACKEND"] = (
    "django.contrib.staticfiles.storage.StaticFilesStorage"
)
SESSION_COOKIE_SECURE = False
SECURE_SSL_REDIRECT = False
