import pytest
from django.test import Client
from django.urls import reverse
from pytest_django.asserts import assertContains

from docurba.users.enums import PosteType
from docurba.users.models import Profile, User
from tests.users.factories import ProfileFactory, SupabaseUserFactory


@pytest.mark.django_db
class TestProfileAdmin:
    def test_change_page(self, admin_session_client: Client) -> None:
        profile = ProfileFactory()

        url = reverse("admin:users_profile_change", kwargs={"object_id": profile.pk})
        response = admin_session_client.get(url)
        assert response.status_code == 200

    def test_verify(self, respx_mock, staff_session_client: Client, mailoutbox) -> None:
        profile = ProfileFactory(
            verified=False, poste=PosteType.DDT, departement__for_snapshot=True
        )
        organization_name = f"DDT {profile.departement}"
        # find_organization_by_name
        organization_mock = respx_mock.get(
            "https://fake-pipedrive.fr/organizations/search?term=DDT+30+-+Gard&fields=name",
        ).respond(
            200,
            json={
                "success": True,
                "data": {
                    "items": [
                        {
                            "result_score": 0.35513002,
                            "item": {
                                "id": 1,
                                "type": "organization",
                                "name": organization_name,
                                "address": None,
                                "visible_to": 3,
                                "owner": {"id": 123456789},
                                "custom_fields": ["AuRA"],
                                "notes": ["Some personal notes"],
                            },
                        }
                    ]
                },
                "additional_data": {"next_cursor": None},
            },
        )

        # get_organization_deals
        organization_dealds_mocks = respx_mock.get(
            "https://fake-pipedrive.fr/deals?org_id=1",
        ).respond(
            200,
            json={
                "success": True,
                "data": [
                    {
                        "id": 51,
                        "title": "🌐 📝 01 Ain",
                        "creator_user_id": 123456789,
                        "value": 0.0,
                        "person_id": 1111,
                        "org_id": 1,
                        "stage_id": 77,
                        "currency": "EUR",
                        "add_time": "2024-08-18T13:39:22Z",
                        "update_time": "2026-07-01T16:28:13Z",
                        "status": "open",
                        "probability": None,
                        "lost_reason": None,
                        "visible_to": 3,
                        "close_time": None,
                        "pipeline_id": 8,
                        "won_time": None,
                        "lost_time": None,
                        "stage_change_time": "2025-10-16T14:06:23Z",
                        "local_won_date": None,
                        "local_lost_date": None,
                        "local_close_date": None,
                        "expected_close_date": None,
                        "custom_fields": {
                            "62964f49dba625be71f3a403652d37c8fa1b93f6": None,
                            "51228cc35804435b6db33c9860c9445bee15b206": None,
                        },
                        "owner_id": 123456789,
                        "label_ids": [],
                        "is_deleted": False,
                        "origin": "ManuallyCreated",
                        "origin_id": None,
                        "channel": None,
                        "channel_id": None,
                        "acv": None,
                        "arr": None,
                        "mrr": None,
                        "is_archived": False,
                        "archive_time": None,
                    }
                ],
                "additional_data": {"next_cursor": None},
            },
        )
        # update_deal
        update_deal_mock = respx_mock.patch(
            "https://fake-pipedrive.fr/deals/1",
        ).respond(
            200,
            json={
                "success": True,
                "data": {
                    "id": 1,
                    "title": "DDT Test",
                    "creator_user_id": 34070131,
                    "value": 0.0,
                    "person_id": 1,
                    "org_id": 1,
                    "stage_id": 3,
                    "currency": "EUR",
                    "add_time": "2026-09-25T09:36:04Z",
                    "update_time": "2026-09-25T09:42:23Z",
                    "status": "open",
                    "probability": None,
                    "lost_reason": None,
                    "visible_to": 3,
                    "close_time": None,
                    "pipeline_id": 1,
                    "won_time": None,
                    "lost_time": None,
                    "stage_change_time": "2026-09-25T09:42:23Z",
                    "local_won_date": None,
                    "local_lost_date": None,
                    "local_close_date": None,
                    "expected_close_date": None,
                    "custom_fields": None,
                    "owner_id": 34070131,
                    "label_ids": [],
                    "is_deleted": False,
                    "origin": "ManuallyCreated",
                    "origin_id": None,
                    "channel": None,
                    "channel_id": None,
                    "is_archived": None,
                    "archive_time": None,
                },
            },
        )
        ############################################
        ######### TODO; move mocks elsewhere
        post_data = {
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
        response = staff_session_client.post(
            reverse("admin:users_profile_change", kwargs={"object_id": profile.pk}),
            post_data,
        )
        assert response.status_code == 302
        assert len(mailoutbox) == 1
        # assert pipedrive called.
        assert respx_mock.calls.called
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
