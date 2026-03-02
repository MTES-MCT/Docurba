# ruff: noqa: F405 F403
from core.settings.base import *  # NOSONAR (S2208)

# Django settings
# ---------------
DEBUG = True

INSTALLED_APPS.extend(
    [
        "django_browser_reload",
        "django_extensions",
        "debug_toolbar",
    ]
)

# https://whitenoise.readthedocs.io/en/stable/django.html
INSTALLED_APPS.insert(
    INSTALLED_APPS.index("django.contrib.staticfiles") - 1,
    "whitenoise.runserver_nostatic",
)

MIDDLEWARE += [
    "debug_toolbar.middleware.DebugToolbarMiddleware",
    "django_browser_reload.middleware.BrowserReloadMiddleware",
]

TEMPLATES[0]["OPTIONS"]["context_processors"].append(
    "django.template.context_processors.debug"
)

SILKY_ENABLED = env.str("SILK_PROFILE_ENABLED", default="False")

if SILKY_ENABLED == "True":
    SILKY_PYTHON_PROFILER = True
    SILKY_PYTHON_PROFILER_BINARY = True
    INSTALLED_APPS.append("silk")
    MIDDLEWARE.append("silk.middleware.SilkyMiddleware")


# Don't use json formatter in dev
del LOGGING["handlers"]["console"]["formatter"]

SESSION_COOKIE_SECURE = False
SECURE_SSL_REDIRECT = False
