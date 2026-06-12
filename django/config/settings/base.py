from pathlib import Path

import sentry_sdk
from environ import Env

env = Env()
env.smart_cast = False

#########################################
############ Django settings ############
#########################################

BASE_DIR = Path(__file__).resolve().parent.parent.parent
APPS_DIR = BASE_DIR / "docurba"
EXPORTS_DIR = env.str("SCRIPT_EXPORT_PATH", default=f"{BASE_DIR}/exports")

SECRET_KEY = env.str("SECRET_KEY", default="local_secret_key")
DEBUG = False
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=[])

# Application definition

INSTALLED_APPS = [
    # Must be above django.contrib.admin
    "pghistory.admin",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.postgres",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "django_filters",
    "pgtrigger",
    "pghistory",
    "docurba.core",
    "docurba.surveys",
    "docurba.users",
    "docurba.internal_api",
    "docurba.history",
]

MIDDLEWARE = [
    "django_datadog_logger.middleware.request_id.RequestIdMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django.middleware.gzip.GZipMiddleware",
    # https://django-pghistory.readthedocs.io/en/3.9.2/module/#pghistory.middleware.HistoryMiddleware
    "pghistory.middleware.HistoryMiddleware",
    # Final logger
    "django_datadog_logger.middleware.error_log.ErrorLoggingMiddleware",
    "django_datadog_logger.middleware.request_log.RequestLoggingMiddleware",
]

ROOT_URLCONF = "config.urls"
STORAGES = {
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.ManifestStaticFilesStorage",
    },
}

# Both Supabase and Scalingo expose database configuration as a single environment variable:
# its connection URL.
# See https://doc.scalingo.com/databases/postgresql/shared-resources/getting-started/connecting
# In test, the `DATABASE_URL` is not set because we create another database to mirror the production schema.
# But DATABASE_URL still needs a defaut value because base settings are imported first before being overriden.

DATABASES = {
    "default": {
        **env.db(
            "DATABASE_URL",
            default="postgresql://postgres:postgres@127.0.0.1:54322/postgres",
        ),
        "CONN_MAX_AGE": env.int("CONN_MAX_AGE", 0),
        "CONN_HEALTH_CHECK": True,
    }
}

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"


# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = "fr-fr"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "static" / "collected"
WHITENOISE_KEEP_ONLY_HASHED_FILES = True

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
INTERNAL_IPS = ["127.0.0.1"]

CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = (
    "HTTP_X_FORWARDED_PROTO",
    "https",
)  # see https://docs.djangoproject.com/en/6.0/ref/settings/#std-setting-SECURE_PROXY_SSL_HEADER
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "json": {"()": "django_datadog_logger.formatters.datadog.DataDogJSONFormatter"},
    },
    "handlers": {
        "console": {"class": "logging.StreamHandler", "formatter": "json"},
        "null": {"class": "logging.NullHandler"},
    },
    "loggers": {
        "": {"handlers": ["console"], "level": "INFO"},
    },
}

#####################################################
############ External libraries settings ############
#####################################################
sentry_sdk.init(
    dsn=env.str("SENTRY_DSN", default=""),
    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for tracing.
    traces_sample_rate=1.0,
    # To set a uniform sample rate
    # Set profiles_sample_rate to 1.0 to profile 100%
    # of sampled transactions.
    # We recommend adjusting this value in production.
    profiles_sample_rate=1.0,
)
PGHISTORY_ADMIN_MODEL = "history.Change"

##########################################
############ Docurba settings ############
##########################################

UPSTREAM_NUXT = env.str("UPSTREAM_NUXT", default="http://localhost:3000")
NUXT3_API_URL = env.str("NUXT3_API_URL", default="http://localhost:4000")
CREATE_UNMANAGED_TABLES = False
REST_FRAMEWORK = {
    "DEFAULT_FILTER_BACKENDS": ("django_filters.rest_framework.DjangoFilterBackend",),
    "DEFAULT_PAGINATION_CLASS": "docurba.internal_api.paginators.DocurbaPagination",
    "PAGE_SIZE": 200,
}

##########################################
############ Supabase settings ############
##########################################

SUPABASE_URL = env.str("SUPABASE_URL", default="http://127.0.0.1:54321")
SUPABASE_ANON_KEY = env.str("SUPABASE_ANON_KEY", default="")
