from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpRequest
from rest_framework import authentication, exceptions
from supabase import AuthApiError, Client, ClientOptions, create_client

from docurba.users.models import Session


class SupabaseAuthentication(authentication.BaseAuthentication):
    def __init__(self) -> None:
        self.supabase_client: Client = create_client(
            settings.SUPABASE_URL,
            settings.SUPABASE_ANON_KEY,
            options=ClientOptions(persist_session=False),
        )

    def authenticate(self, request: HttpRequest):  # noqa: ANN201
        access_key = request.headers.get("Supabase-Authorization")
        if not access_key:
            return None

        try:
            response = self.supabase_client.auth.get_claims(access_key)
            session_id = response["claims"]["session_id"]
            email = response["claims"]["email"]

            session = Session.objects.select_related("user__profile").get(
                pk=session_id, user__email=email
            )

        except (AuthApiError, ObjectDoesNotExist) as exc:
            raise exceptions.AuthenticationFailed from exc

        if hasattr(session.user, "profile"):
            user = User(
                username=str(session.user.id),
                email=session.user.email,
                last_name=session.user.profile.lastname,
                first_name=session.user.profile.firstname,
                is_superuser=session.user.profile.is_admin,
                is_staff=session.user.profile.is_staff,
                date_joined=session.user.profile.created_at,
                last_login=session.user.last_sign_in_at,
            )
        else:
            user = User(
                username=str(session.user.id),
                email=session.user.email,
            )
        return (user, None)
