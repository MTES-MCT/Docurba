from unittest import mock

import pytest
from django.contrib import messages
from django.test import Client
from django.urls import reverse
from pytest_django.asserts import assertContains, assertMessages
from respx import MockRouter

from docurba.users import enums as users_enums
from docurba.users.models import Profile, User
from tests.users.factories import ProfileFactory, SupabaseUserFactory


@pytest.mark.django_db
class TestProfileAdmin:
    def test_change_page(self, admin_session_client: Client) -> None:
        profile = ProfileFactory()

        url = reverse("admin:users_profile_change", kwargs={"object_id": profile.pk})
        response = admin_session_client.get(url)
        assert response.status_code == 200


@pytest.mark.django_db
class TestprofileAdminVerify:
    def _post_data(self, profile: Profile) -> dict:
        return {
            "CHANGE_FORM-action": "verify",
            "CHANGE_FORM-select_across": 0,
            "index": 0,
            "_selected_action": str(profile.user_id),
            "verified": "on",
            "firstname": profile.firstname,
            "lastname": profile.lastname,
            "side": "etat",
            "poste": "ddt",
            "other_poste": "chef_unite",
            "collectivite": "",
            "departement": "30",
            "region": "76",
            "departements": "",
            "tel": "",
            "successfully_logged_once": "on",
            "optin": "on",
            "must_update_password": "on",
        }

    @pytest.mark.parametrize("status_code", [408, 409, 429, 503])
    def test_verify__pipedrive_service_unavailable(
        self,
        respx_mock: MockRouter,
        staff_session_client: Client,
        status_code: str,
    ) -> None:
        profile = ProfileFactory(
            verified=False,
            poste=users_enums.PosteType.DDT,
            side=users_enums.ProfileSideType.ETAT,
            departement__code_insee="13",
        )
        post_data = self._post_data(profile=profile)
        respx_mock.get(
            "https://fake-pipedrive.fr/organizations/search?term=DDT+13&fields=name",
        ).respond(
            status_code,
            json={},
        )
        with (
            mock.patch("tenacity.nap.time.sleep", mock.MagicMock()),
        ):
            response = staff_session_client.post(
                reverse("admin:users_profile_change", kwargs={"object_id": profile.pk}),
                post_data,
            )
        assert messages.Message(
            messages.ERROR,
            "Pipedrive est injoignable. Merci de réessayer dans quelques minutes.",
        ) in list(messages.get_messages(response.wsgi_request))
        assert response.status_code == 302
        profile.refresh_from_db()
        assert profile.verified is True

    def test_verify__pipedrive_not_found(
        self,
        respx_mock: MockRouter,
        staff_session_client: Client,
    ) -> None:
        profile = ProfileFactory(
            verified=False,
            poste=users_enums.PosteType.DDT,
            side=users_enums.ProfileSideType.ETAT,
            departement__code_insee="13",
        )
        post_data = self._post_data(profile=profile)
        respx_mock.get(
            "https://fake-pipedrive.fr/organizations/search?term=DDT+13&fields=name",
        ).respond(
            404,
            json={"success": False, "error": "Deal not found", "code": "ERR_NOT_FOUND"},
        )
        with (
            mock.patch("tenacity.nap.time.sleep", mock.MagicMock()),
        ):
            response = staff_session_client.post(
                reverse("admin:users_profile_change", kwargs={"object_id": profile.pk}),
                post_data,
            )
        assertMessages(
            response,
            [
                messages.Message(
                    messages.ERROR,
                    "Information manquante dans Pipedrive. Détails de l'erreur : « Deal not found ».",
                )
            ],
        )
        assert response.status_code == 302
        profile.refresh_from_db()
        assert profile.verified is True

    def test_verify__pipedrive_field_validation_error(
        self,
        respx_mock: MockRouter,
        staff_session_client: Client,
    ) -> None:
        profile = ProfileFactory(
            verified=False,
            poste=users_enums.PosteType.DDT,
            side=users_enums.ProfileSideType.ETAT,
            departement__code_insee="13",
        )
        post_data = self._post_data(profile=profile)
        respx_mock.get(
            "https://fake-pipedrive.fr/organizations/search?term=DDT+13&fields=name",
        ).respond(
            400,
            json={
                "success": False,
                "error": "Validation failed: owner_id: User not found or not accessible.",
                "code": "ERR_SCHEMA_VALIDATION_FAILED",
            },
        )
        with (
            mock.patch("tenacity.nap.time.sleep", mock.MagicMock()),
        ):
            response = staff_session_client.post(
                reverse("admin:users_profile_change", kwargs={"object_id": profile.pk}),
                post_data,
            )
        assertMessages(
            response,
            [
                messages.Message(
                    messages.ERROR,
                    "Mauvais paramètres envoyés à Pipedrive. Détails de l'erreur : « Validation failed: owner_id: User not found or not accessible. ».",
                )
            ],
        )
        assert response.status_code == 302
        profile.refresh_from_db()
        assert profile.verified is True

    def test_verify__pipedrive_http_error(
        self,
        respx_mock: MockRouter,
        staff_session_client: Client,
    ) -> None:
        profile = ProfileFactory(
            verified=False,
            poste=users_enums.PosteType.DDT,
            side=users_enums.ProfileSideType.ETAT,
            departement__code_insee="13",
        )
        post_data = self._post_data(profile=profile)
        respx_mock.get(
            "https://fake-pipedrive.fr/organizations/search?term=DDT+13&fields=name",
        ).respond(
            500,
            json={},
        )
        with (
            mock.patch("tenacity.nap.time.sleep", mock.MagicMock()),
        ):
            response = staff_session_client.post(
                reverse("admin:users_profile_change", kwargs={"object_id": profile.pk}),
                post_data,
            )
        assertMessages(
            response,
            [
                messages.Message(
                    messages.ERROR,
                    "Autre erreur Pipedrive",
                )
            ],
        )
        assert response.status_code == 302
        profile.refresh_from_db()
        assert profile.verified is True


@pytest.mark.django_db
class TestSupabaseUserAdmin:
    def test_change_page(self, admin_session_client: Client) -> None:
        user = SupabaseUserFactory()

        url = reverse("admin:users_supabaseuser_change", kwargs={"object_id": user.pk})
        response = admin_session_client.get(url)
        assert response.status_code == 200

    def test_update_password(self, staff_session_client: Client) -> None:
        user = SupabaseUserFactory()

        url = reverse("admin:users_supabaseuser_change", kwargs={"object_id": user.pk})
        response = staff_session_client.get(url)

        assertContains(response, "Créer un mot de passe par défaut")

        response = staff_session_client.post(
            url,
            data={"_update_user_password": "Créer+un+mot+de+passe+par+défaut"},
            follow=True,
        )
        assertContains(response, "Nouveau mot de passe :")

    # Make sure you remove the test database first
    # because the Django user is not recreated between
    # tests.
    def test_staff_session_client(self, staff_session_client: Client) -> None:
        django_user = User.objects.get(pk=staff_session_client.session["_auth_user_id"])
        assert (
            django_user.profile_id
            == Profile.objects.get(email=django_user.email).user_id
        )

    def test_admin_session_client(self, admin_session_client: Client) -> None:
        django_user = User.objects.get(pk=admin_session_client.session["_auth_user_id"])
        assert (
            django_user.profile_id
            == Profile.objects.get(email=django_user.email).user_id
        )
