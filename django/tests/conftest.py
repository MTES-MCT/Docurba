import contextlib
from unittest.mock import patch

import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.core.handlers.wsgi import WSGIRequest
from django.test import Client
from django.utils import timezone
from pytest_django import DjangoDbBlocker
from rest_framework.test import APIClient
from supabase_auth import AuthResponse
from supabase_auth import Session as SupabaseAuthSession
from supabase_auth import User as SupabaseAuthUser

from docurba.users.models import Profile
from tests.users.factories import ProfileFactory


class SupabaseApiTestClient(APIClient):
    def request(self, **kwargs: dict) -> WSGIRequest:
        kwargs["HTTP_SUPABASE-AUTHORIZATION"] = "test-token"
        return super().request(**kwargs)


@pytest.fixture
def api_client() -> APIClient:
    return APIClient()


@pytest.fixture(name="api_client_with_auth")
def api_client_with_auth_factory() -> None:

    @contextlib.contextmanager
    def api_client_with_auth(profile: Profile) -> None:
        with patch("docurba.internal_api.auth.create_client") as create_client:
            supabase = create_client.return_value
            supabase_auth_user = SupabaseAuthUser(
                id=profile.user_id,
                email=profile.email,
                app_metadata={},
                user_metadata={},
                aud="",
                created_at=timezone.now(),
                is_anonymous=False,
                is_sso_user=False,
            )
            supabase_session = SupabaseAuthSession(
                access_token="aa.bb",  # noqa: S106
                refresh_token="",
                expires_in=11111,
                token_type="",
                user=supabase_auth_user,
            )
            supabase.auth.set_session.return_value = AuthResponse(
                session=supabase_session,
                user=supabase_auth_user,
            )
            supabase.auth.get_session.return_value = supabase_session
            yield SupabaseApiTestClient()

    return api_client_with_auth


@pytest.fixture(scope="session")
def admin_session_client(django_db_blocker: DjangoDbBlocker | None) -> Client:
    """Overide of the official pytest's admin_client fixture.

    Improve performance by sharing the admin client
    during the session.
    """
    client = Client()
    UserModel = get_user_model()  # noqa: N806
    email = "admin@test.com"

    with django_db_blocker.unblock():
        try:
            user = UserModel.objects.get(email=email)
        except UserModel.DoesNotExist:
            profile = ProfileFactory(email=email)
            data = {
                "email": email,
                "password": "password",
                "username": email,
                "profile_id": profile.user_id,
            }
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

    with django_db_blocker.unblock():
        write_group, _ = Group.objects.get_or_create(name="write")
        # `users` and `auth` apps have the same namecode but different app_label.
        permissions = [
            (
                "users",
                "change_supabaseuser",
            ),  # users/test_admin.py::TestUserAdmin::test_update_password
            (
                "core",
                "change_event",
            ),  # core/test_admin.py::TestEventChange::test_[un]archive
        ]
        for app_label, codename in permissions:
            permission = Permission.objects.get(
                content_type__app_label=app_label, codename=codename
            )
            write_group.permissions.add(permission)
        try:
            user = UserModel.objects.get(email=email)
        except UserModel.DoesNotExist:
            profile = ProfileFactory(email=email)
            data = {
                "email": email,
                "password": "password",
                "username": email,
                "profile_id": profile.user_id,
            }
            user = UserModel.objects.create_user(**data, is_staff=True)

        user.groups.add(write_group)
        client.force_login(user)

    return client
