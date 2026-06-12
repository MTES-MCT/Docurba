# ruff: noqa: F405 F403
from config.settings.base import *  # NOSONAR (S2208)

APPS_DIR = str(APPS_DIR)

STORAGES["staticfiles"]["BACKEND"] = (
    "django.contrib.staticfiles.storage.StaticFilesStorage"
)
SESSION_COOKIE_SECURE = False
SECURE_SSL_REDIRECT = False
CREATE_UNMANAGED_TABLES = True

DATABASES = {
    "default": {
        **env.db(
            "TEST_DATABASE_URL",
            default="postgresql://postgres:postgres@127.0.0.1:5432/test_docurba",
        ),
        "CONN_MAX_AGE": env.int("CONN_MAX_AGE", 0),
        "CONN_HEALTH_CHECK": True,
        "TEST": {
            "MIRROR": "default",
        },
    },
}

NUXT3_API_URL = "http://fake-nuxt3.com"
ASSERT_SNAPSHOT_QUERIES_EXTRA_PACKAGES_ALLOWLIST = [
    ("django/db/models/query.py", "count")
]
if env.str("DEBUG_SQL_SNAPSHOT", default=None):
    # Mandatory to have detailed stacktrace inside templates
    TEMPLATES[0]["OPTIONS"]["debug"] = True
