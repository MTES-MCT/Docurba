# ruff: noqa: F405 F403
from config.settings.base import *  # NOSONAR (S2208)

STORAGES["staticfiles"]["BACKEND"] = (
    "django.contrib.staticfiles.storage.StaticFilesStorage"
)
SESSION_COOKIE_SECURE = False
SECURE_SSL_REDIRECT = False
CREATE_UNMANAGED_TABLES = True

DATABASES = {
    "default": {
        **env.db("TEST_DATABASE_URL"),
        "CONN_MAX_AGE": env.int("CONN_MAX_AGE", 0),
        "CONN_HEALTH_CHECK": True,
        "TEST": {
            "MIRROR": "default",
        },
    },
}
