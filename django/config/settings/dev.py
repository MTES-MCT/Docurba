from corsheaders.defaults import default_headers

# ruff: noqa: F405 F403
from config.settings.base import *  # NOSONAR (S2208)

# Django settings
# ---------------
DEBUG = True

INSTALLED_APPS.extend(
    [
        "django_browser_reload",
        "django_extensions",
        "debug_toolbar",
        "corsheaders",
    ]
)

MIDDLEWARE += [
    "debug_toolbar.middleware.DebugToolbarMiddleware",
    "django_browser_reload.middleware.BrowserReloadMiddleware",
]

MIDDLEWARE.insert(
    MIDDLEWARE.index("django.middleware.security.SecurityMiddleware") + 1,
    "corsheaders.middleware.CorsMiddleware",
)

TEMPLATES[0]["OPTIONS"]["context_processors"].append(
    "django.template.context_processors.debug"
)

# Don't use json formatter in dev
del LOGGING["handlers"]["console"]["formatter"]

DEBUG_SQL = env.bool("DEBUG_SQL", default=False)
if DEBUG_SQL:
    LOGGING["loggers"]["django.db.backends"] = {
        "level": "DEBUG",
        "handlers": ["console"],
    }

SESSION_COOKIE_SECURE = False
SECURE_SSL_REDIRECT = False

CORS_ALLOWED_ORIGINS = ["http://localhost:3000"]
CORS_ALLOW_HEADERS = [
    *default_headers,
    "supabase-authorization",
]
