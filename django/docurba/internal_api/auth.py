from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpRequest
from rest_framework import authentication, exceptions
from supabase import Client, ClientOptions, create_client
from supabase_auth.errors import AuthApiError, AuthSessionMissingError, UserDoesntExist

from docurba.users.models import Profile


class SupabaseClient:
    def __init__(self) -> Client:
        self.client = create_client(
            settings.SUPABASE_URL,
            settings.SUPABASE_ANON_KEY,
            options=ClientOptions(persist_session=False),
        )


class SupabaseAuthentication(authentication.BaseAuthentication):
    def __init__(self) -> None:
        self.supabase_client = SupabaseClient().client

    def authenticate(self, request: HttpRequest):  # noqa: ANN201
        access_key = request.headers.get("Supabase-Authorization")
        if not access_key:
            return None

        try:
            self.supabase_client.auth.set_session(
                access_token=access_key, refresh_token=""
            )
            session = self.supabase_client.auth.get_session()

        except (
            AuthApiError,
            ObjectDoesNotExist,
            AuthSessionMissingError,
            UserDoesntExist,
        ) as exc:
            raise exceptions.AuthenticationFailed from exc

        profile_qs = Profile.objects.filter(user_id=session.user.id)
        if profile_qs.exists():
            profile = profile_qs.get()
            user = User(
                username=str(session.user.id),
                email=session.user.email,
                last_name=profile.lastname,
                first_name=profile.firstname,
                is_superuser=profile.is_admin,
                is_staff=profile.is_staff,
                date_joined=profile.created_at,
                last_login=session.user.last_sign_in_at,
            )
        else:
            user = User(
                username=str(session.user.id),
                email=session.user.email,
            )
        user.supabase_client = self.supabase_client
        return (user, None)
