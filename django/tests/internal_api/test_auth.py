from unittest.mock import MagicMock, patch

import pytest
from django.utils import timezone
from faker import Faker
from pytest_django import DjangoAssertNumQueries
from rest_framework import exceptions
from rest_framework.test import APIRequestFactory
from supabase import AuthSessionMissingError
from supabase_auth import AuthResponse
from supabase_auth import Session as SupabaseAuthSession
from supabase_auth import User as SupabaseAuthUser

from docurba.internal_api.auth import SupabaseAuthentication
from tests.users.factories import ProfileFactory, SupabaseUserFactory

fake = Faker()


@pytest.mark.django_db
@patch("docurba.internal_api.auth.create_client")
class TestSupabaseAuthentication:
    def test_valid_with_profile(
        self,
        create_client: MagicMock,
        django_assert_num_queries: DjangoAssertNumQueries,
    ) -> None:
        profile = ProfileFactory(is_admin=False, is_staff=True)
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

        factory = APIRequestFactory()
        request = factory.get("/", headers={"Supabase-Authorization": "test-token"})

        backend = SupabaseAuthentication()
        with django_assert_num_queries(2):
            (user, auth) = backend.authenticate(request)
            assert user.username == profile.user.id
            assert user.email == profile.user.email
            assert user.last_login == profile.user.last_sign_in_at
            assert user.last_name == profile.lastname
            assert user.first_name == profile.firstname
            assert user.date_joined == profile.created_at
            assert not user.is_superuser
            assert user.is_staff
            assert auth is None

    def test_valid_without_profile(
        self,
        create_client: MagicMock,
        django_assert_num_queries: DjangoAssertNumQueries,
    ) -> None:
        logged_in_user = SupabaseUserFactory()
        supabase = create_client.return_value
        supabase_auth_user = SupabaseAuthUser(
            id=logged_in_user.id,
            email=logged_in_user.email,
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

        factory = APIRequestFactory()
        request = factory.get("/", headers={"Supabase-Authorization": "test-token"})

        backend = SupabaseAuthentication()
        with django_assert_num_queries(1):
            (user, auth) = backend.authenticate(request)
            assert user.username == logged_in_user.id
            assert user.email == logged_in_user.email
            assert user.last_login == logged_in_user.last_sign_in_at
            assert user.last_name == ""
            assert user.first_name == ""
            assert auth is None

    def test_invalid_session_and_email(
        self,
        create_client: MagicMock,
        django_assert_num_queries: DjangoAssertNumQueries,
    ) -> None:
        supabase = create_client.return_value
        supabase.auth.set_session.side_effect = AuthSessionMissingError()
        supabase.auth.get_session.return_value = None

        factory = APIRequestFactory()
        request = factory.get("/", headers={"Supabase-Authorization": "test-token"})

        backend = SupabaseAuthentication()
        with (
            django_assert_num_queries(0),
            pytest.raises(exceptions.AuthenticationFailed),
        ):
            backend.authenticate(request)
