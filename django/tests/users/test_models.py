import pytest
from django.db import connection, transaction
from django.utils import timezone

from docurba.core.enums import ProjectSharingRoleType
from docurba.users.enums import PosteType
from tests.core.factories import ProjectSharingFactory

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

        profile = ProfileFactory(poste=PosteType.DDT)
        message = profile.verified_etat_user_email()
        assert message.template_id == "d-939bd4723dd04edcad17e6584b7641f3"
        assert message.dynamic_template_data["shared_procedure_url"] is False

        profile = ProfileFactory(poste=PosteType.REGION)
        message = profile.verified_etat_user_email()
        assert message.template_id == "d-3d9f4b96863d4c6e8d4c9489f6d8eb6e"
        assert message.dynamic_template_data["shared_procedure_url"] is False

        profile = ProfileFactory()
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

        profile = ProfileFactory(departement__for_snapshot=True)
        message = profile.verified_etat_user_email()
        assert message.dynamic_template_data["departement"] == "Gard"
        assert message.dynamic_template_data["regionName"] == "Occitanie"
        assert message.dynamic_template_data["region"] == "76"
