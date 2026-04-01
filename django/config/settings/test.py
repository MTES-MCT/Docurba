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
        "ENGINE": "django.db.backends.postgresql",
        "NAME": env.str("TEST_PGDATABASE", "test_postgres"),
        "USER": env.str("TEST_PGUSER", "postgres"),
        "CONN_MAX_AGE": 3600,
        "PASSWORD": env.str("TEST_PGPASSWORD", "postgres"),
        "HOST": env.str("TEST_PGHOST", "127.0.0.1"),
        "PORT": env.str("TEST_PGPORT", "5431"),
        "TEST": {
            "MIRROR": "default",  # ✅ Forces Django to use the existing database
        },
    },
}
