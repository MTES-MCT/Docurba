import pytest
from django.contrib.auth import get_user_model
from django.test import Client
from pytest_django import DjangoDbBlocker
from rest_framework.test import APIClient


@pytest.fixture
def api_client() -> APIClient:
    return APIClient()


@pytest.fixture(scope="session")
def admin_session_client(django_db_blocker: DjangoDbBlocker | None) -> Client:
    """Overide of the official pytest's admin_client fixture.

    Improve performance by sharing the admin client
    during the session.
    """
    client = Client()
    UserModel = get_user_model()  # noqa: N806
    email = "admin@test.com"
    data = {
        "email": email,
        "password": "password",
        "username": email,
    }

    with django_db_blocker.unblock():
        try:
            user = UserModel.objects.get(email=email)
        except UserModel.DoesNotExist:
            user = UserModel.objects.create_superuser(**data)
        client.force_login(user)

    return client
