import pytest
from pytest_django.fixtures import SettingsWrapper


@pytest.fixture(autouse=True)
def disable_whitenoise(settings: SettingsWrapper) -> None:
    # > During testing, ensure that staticfiles storage backend in the STORAGES setting
    # is set to something else like 'django.contrib.staticfiles.storage.StaticFilesStorage'
    # https://docs.djangoproject.com/en/6.0/ref/contrib/staticfiles/#django.contrib.staticfiles.storage.ManifestStaticFilesStorage.manifest_strict
    settings.STORAGES = {
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"
        }
    }
