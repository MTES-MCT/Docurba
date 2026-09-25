import pytest
from django.db import connection, transaction
from django.utils import timezone
from respx import MockRouter

from docurba.core.enums import ProjectSharingRoleType
from docurba.users import enums as users_enums
from docurba.utils.consumed_apis import pipedrive
from tests.core.factories import ProjectSharingFactory
from tests.utils.consumed_apis import pipedrive_mocks

from .factories import ProfileFactory, SupabaseUserFactory


@pytest.mark.django_db
class TestSupabaseUserModel:
    def test_update_password(self) -> None:
        user = SupabaseUserFactory()
        assert not user.encrypted_password
        password = "ARandomPassword"  # noqa: S105
        user.update_password(password=password)
        user.refresh_from_db()

        assert user.encrypted_password

        with connection.cursor() as cursor, transaction.atomic():
            cursor.execute(
                """
                    SELECT (encrypted_password = crypt(%s, encrypted_password)) AS encrypted_password FROM auth.users where id=%s;
                """,
                [password, user.id],
            )
            row = cursor.fetchone()
        assert row[0]


@pytest.mark.django_db
class TestProfile:
    def test_verify_ddt(self, respx_mock: MockRouter, mailoutbox: list | None) -> None:
        profile = ProfileFactory(
            verified=False,
            poste=users_enums.PosteType.DDT,
            side=users_enums.ProfileSideType.ETAT,
            departement__for_snapshot=True,
        )
        # find_organization_by_name
        respx_mock.get(
            pipedrive_mocks.SEARCH_ORGANIZATIONS_BY_NAME[0],
        ).respond(200, json=pipedrive_mocks.SEARCH_ORGANIZATIONS_BY_NAME[1])

        # get_organization_deals
        respx_mock.get(pipedrive_mocks.GET_DEAL_ORG_ID_1[0]).respond(
            200, json=pipedrive_mocks.GET_DEAL_ORG_ID_1[1]
        )
        # update_deal
        respx_mock.patch(pipedrive_mocks.PATCH_DEAL_ID_1[0]).respond(
            200, json=pipedrive_mocks.PATCH_DEAL_ID_1[1]
        )
        profile.verify()
        assert len(mailoutbox) == 1
        assert mailoutbox[0].template_id == "d-939bd4723dd04edcad17e6584b7641f3"
        # assert pipedrive called.
        assert respx_mock.calls.called
        profile.refresh_from_db()
        assert profile.verified is True

    def test_verify_dreal(
        self, respx_mock: MockRouter, mailoutbox: list | None
    ) -> None:
        profile = ProfileFactory(
            verified=False,
            poste=users_enums.PosteType.DREAL,
            side=users_enums.ProfileSideType.ETAT,
            departement__for_snapshot=True,
        )
        # find_organization_by_name
        respx_mock.get(
            pipedrive_mocks.SEARCH_ORGANIZATIONS_BY_NAME[0],
        ).respond(200, json=pipedrive_mocks.SEARCH_ORGANIZATIONS_BY_NAME[1])

        # get_organization_deals
        respx_mock.get(pipedrive_mocks.GET_DEAL_ORG_ID_1[0]).respond(
            200, json=pipedrive_mocks.GET_DEAL_ORG_ID_1[1]
        )
        # update_deal
        respx_mock.patch(pipedrive_mocks.PATCH_DEAL_ID_1[0]).respond(
            200, json=pipedrive_mocks.PATCH_DEAL_ID_1[1]
        )
        profile.verify()
        assert len(mailoutbox) == 1
        assert mailoutbox[0].template_id == "d-3d9f4b96863d4c6e8d4c9489f6d8eb6e"
        # assert pipedrive called.
        assert respx_mock.calls.called
        profile.refresh_from_db()
        assert profile.verified is True

    def test_verify_collectivite(
        self, respx_mock: MockRouter, mailoutbox: list | None
    ) -> None:
        profile = ProfileFactory(
            verified=False,
            side=users_enums.ProfileSideType.COLLECTIVITE,
            departement__for_snapshot=True,
        )
        profile.verify()
        assert len(mailoutbox) == 1
        assert mailoutbox[0].template_id == "d-0143010573f6497b86abbd4e4c96f46e"

        assert respx_mock.calls.called is False
        profile.refresh_from_db()
        assert profile.verified is True

    def test_verify_organization_not_found(
        self, respx_mock: MockRouter, mailoutbox: list | None
    ) -> None:
        profile = ProfileFactory(
            verified=False,
            poste=users_enums.PosteType.DDT,
            side=users_enums.ProfileSideType.ETAT,
            departement__for_snapshot=True,
        )
        # find_organization_by_name
        respx_mock.get(
            pipedrive_mocks.SEARCH_ORGANIZATIONS_BY_NAME[0],
        ).respond(
            200,
            json={
                "success": True,
                "data": {"items": []},
                "additional_data": {"next_cursor": None},
            },
        )

        with pytest.raises(pipedrive.PipedriveNotFoundError):
            profile.verify()
        assert len(mailoutbox) == 1
        # assert pipedrive called.
        assert respx_mock.calls.called
        profile.refresh_from_db()
        assert profile.verified is True


@pytest.mark.django_db
class TestProfileEmails:
    def test_verified_collectivite_user_email(
        self, caplog: pytest.LogCaptureFixture
    ) -> None:
        profile = ProfileFactory(collectivite=None, for_snapshot=True)
        message = profile.verified_collectivite_user_email()
        assert message is False
        assert (
            caplog.messages[0]
            == "User 1cd65b57-7027-4aa5-8d19-5e1baf8d6f09 should have a collectivite"
        )

        profile = ProfileFactory()
        ProjectSharingFactory(
            user_email=profile.email,
            project__with_procedure=True,
            project__with_procedure__is_principale=True,
            project__with_procedure__for_snapshot=True,
            role=ProjectSharingRoleType.WRITE_FRISE,
            created_at=timezone.now(),
        )
        message = profile.verified_collectivite_user_email()
        assert (
            message.dynamic_template_data["shared_procedure_url"]
            == "http://localhost:8000/frise/1cd65b57-7027-4aa5-8d19-5e1baf8d6f09"
        )

        profile = ProfileFactory(collectivite__for_snapshot=True)
        message = profile.verified_collectivite_user_email()
        assert (
            message.dynamic_template_data["collectivite_name"]
            == "Syndicat mixte d'équipement de la commune de Beaucaire"
        )

    def test_verified_etat_user_email(self, caplog: pytest.LogCaptureFixture) -> None:
        profile = ProfileFactory(for_snapshot=True, departement=None)
        message = profile.verified_etat_user_email()
        assert message is False
        assert (
            caplog.messages[0]
            == "User 1cd65b57-7027-4aa5-8d19-5e1baf8d6f09 should have a departement"
        )

        profile = ProfileFactory(
            poste=users_enums.PosteType.REGION, departement__for_snapshot=True
        )
        message = profile.verified_etat_user_email()
        assert message.template_id == "d-3d9f4b96863d4c6e8d4c9489f6d8eb6e"
        assert (
            message.dynamic_template_data["go_to_docurba_url"]
            == "http://localhost:8000/trames/region-76?mtm_campaign=sendgrid&mtm_kwd=tdbdreal"
        )
        assert message.dynamic_template_data["regionName"] == "Occitanie"

        # DDT without a shared procedure.
        profile = ProfileFactory(
            poste=users_enums.PosteType.DDT, departement__for_snapshot=True
        )
        message = profile.verified_etat_user_email()
        assert message.template_id == "d-939bd4723dd04edcad17e6584b7641f3"
        assert message.dynamic_template_data["shared_procedure_url"] is False
        assert message.dynamic_template_data["departement"] == "Gard"
        assert (
            message.dynamic_template_data["go_to_docurba_url"]
            == "http://localhost:8000/ddt/30/collectivites?mtm_campaign=sendgrid&mtm_kwd=tdbddt"
        )

        # DDT with a shared procedure
        profile = ProfileFactory(poste=users_enums.PosteType.DDT)
        ProjectSharingFactory(
            user_email=profile.email,
            project__with_procedure=True,
            project__with_procedure__is_principale=True,
            project__with_procedure__for_snapshot=True,
            role=ProjectSharingRoleType.WRITE_FRISE,
            created_at=timezone.now(),
        )
        message = profile.verified_etat_user_email()
        assert (
            message.dynamic_template_data["shared_procedure_url"]
            == "http://localhost:8000/frise/1cd65b57-7027-4aa5-8d19-5e1baf8d6f09"
        )
