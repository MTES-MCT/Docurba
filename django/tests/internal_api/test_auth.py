from unittest.mock import MagicMock, patch

import pytest
from faker import Faker
from pytest_django import DjangoAssertNumQueries
from rest_framework import exceptions
from rest_framework.test import APIRequestFactory

from docurba.internal_api.auth import SupabaseAuthentication
from tests.users.factories import ProfileFactory, SessionFactory, UserFactory

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
        session = SessionFactory(user=profile.user)

        supabase = create_client.return_value
        supabase.auth.get_claims.return_value = {
            "claims": {"session_id": session.id, "email": session.user.email}
        }

        factory = APIRequestFactory()
        request = factory.get("/", headers={"Supabase-Authorization": "test-token"})

        backend = SupabaseAuthentication()
        with django_assert_num_queries(1):
            (user, auth) = backend.authenticate(request)
            assert user.username == session.user.id
            assert user.email == session.user.email
            assert user.last_login == session.user.last_sign_in_at
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
        session = SessionFactory()

        supabase = create_client.return_value
        supabase.auth.get_claims.return_value = {
            "claims": {"session_id": session.id, "email": session.user.email}
        }

        factory = APIRequestFactory()
        request = factory.get("/", headers={"Supabase-Authorization": "test-token"})

        backend = SupabaseAuthentication()
        with django_assert_num_queries(1):
            (user, auth) = backend.authenticate(request)
            assert user.username == session.user.id
            assert user.email == session.user.email
            assert user.last_login == session.user.last_sign_in_at
            assert user.last_name == ""
            assert user.first_name == ""
            assert auth is None

    def test_invalid_session_and_email(
        self,
        create_client: MagicMock,
        django_assert_num_queries: DjangoAssertNumQueries,
    ) -> None:
        supabase = create_client.return_value
        supabase.auth.get_claims.return_value = {
            "claims": {"session_id": fake.uuid4(), "email": fake.email()}
        }

        factory = APIRequestFactory()
        request = factory.get("/", headers={"Supabase-Authorization": "test-token"})

        backend = SupabaseAuthentication()
        with (
            django_assert_num_queries(1),
            pytest.raises(exceptions.AuthenticationFailed),
        ):
            backend.authenticate(request)

    def test_valid_session_with_invalid_email(
        self,
        create_client: MagicMock,
        django_assert_num_queries: DjangoAssertNumQueries,
    ) -> None:
        session = SessionFactory()

        supabase = create_client.return_value
        supabase.auth.get_claims.return_value = {
            "claims": {"session_id": session.id, "email": fake.email()}
        }

        factory = APIRequestFactory()
        request = factory.get("/", headers={"Supabase-Authorization": "test-token"})

        backend = SupabaseAuthentication()
        with (
            django_assert_num_queries(1),
            pytest.raises(exceptions.AuthenticationFailed),
        ):
            backend.authenticate(request)

    def test_valid_email_with_invalid_session(
        self,
        create_client: MagicMock,
        django_assert_num_queries: DjangoAssertNumQueries,
    ) -> None:
        user = UserFactory()

        supabase = create_client.return_value
        supabase.auth.get_claims.return_value = {
            "claims": {"session_id": fake.uuid4(), "email": user.email}
        }

        factory = APIRequestFactory()
        request = factory.get("/", headers={"Supabase-Authorization": "test-token"})

        backend = SupabaseAuthentication()
        with (
            django_assert_num_queries(1),
            pytest.raises(exceptions.AuthenticationFailed),
        ):
            backend.authenticate(request)
