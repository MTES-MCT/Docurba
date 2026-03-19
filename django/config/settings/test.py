# ruff: noqa: F405 F403
from environ import Env

from config.settings.base import *  # NOSONAR (S2208)

env = Env()

STORAGES["staticfiles"]["BACKEND"] = (
    "django.contrib.staticfiles.storage.StaticFilesStorage"
)
SESSION_COOKIE_SECURE = False
SECURE_SSL_REDIRECT = False
CREATE_UNMANAGED_TABLES = True

DATABASES["default"]["HOST"] = env.str("PGHOST", "127.0.0.1")  # noqa: F405
DATABASES["default"]["PORT"] = env.str("PGPORT", "54322")  # noqa: F405
DATABASES["default"]["NAME"] = env.str("PGDATABASE", "test_postgres")  # noqa: F405
DATABASES["default"]["USER"] = env.str("PGUSER", "postgres")  # noqa: F405
DATABASES["default"]["PASSWORD"] = env.str("PGPASSWORD", "postgres")  # noqa: F405
