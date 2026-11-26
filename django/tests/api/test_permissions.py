from unittest.mock import MagicMock, patch

import pytest
from django.urls import reverse
from django.utils import timezone
from faker import Faker
from supabase_auth import AuthResponse
from supabase_auth import Session as SupabaseAuthSession
from supabase_auth import User as SupabaseAuthUser

from tests.conftest import SupabaseApiTestClient
from tests.users.factories import ProfileFactory

fake = Faker()


@pytest.mark.django_db
@patch("docurba.api.auth.create_client")
class TestApiPermissions:
    def test_authenticated_not_verified(
        self,
        create_client: MagicMock,
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

        api_client = SupabaseApiTestClient(profile)
        response = api_client.get(reverse("internal_api:procedures-list"))
        assert response.status_code == 403

    def test_authenticated_and_verified(
        self,
        create_client: MagicMock,
    ) -> None:
        profile = ProfileFactory(is_admin=False, is_staff=False, verified=True)
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

        api_client = SupabaseApiTestClient(profile)
        response = api_client.get(reverse("internal_api:procedures-list"))
        assert response.status_code == 200
