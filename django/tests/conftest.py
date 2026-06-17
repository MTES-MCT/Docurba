import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
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


@pytest.fixture(scope="session")
def staff_session_client(django_db_blocker: DjangoDbBlocker | None) -> Client:
    """Overide of the official pytest's admin_client fixture.

    Create a staff user that has the same permissions as our Docurba staff members.
    Note that the group with write access exists in production but its permissions are wider.
    As we can't synchronize perms between environments for the moment,
    let's only add permissions used in tests.
    """
    client = Client()
    UserModel = get_user_model()  # noqa: N806
    email = "staff@test.com"
    data = {
        "email": email,
        "password": "password",
        "username": email,
    }

    with django_db_blocker.unblock():
        write_group, _ = Group.objects.get_or_create(name="write")
        # `users` and `auth` apps have the same namecode but different app_label.
        permissions = [
            (
                "users",
                "change_user",
            ),  # users/test_admin.py::TestUserAdmin::test_update_password
        ]
        for app_label, codename in permissions:
            permission = Permission.objects.get(
                content_type__app_label=app_label, codename=codename
            )
            write_group.permissions.add(permission)
        try:
            user = UserModel.objects.get(email=email)
        except UserModel.DoesNotExist:
            user = UserModel.objects.create_user(**data, is_staff=True)

        user.groups.add(write_group)
        client.force_login(user)

    return client
