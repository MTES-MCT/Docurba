import pytest
from django.core.management import call_command
from django.utils import timezone

from docurba.core.models import Event, Procedure, Project, ProjectSharing
from docurba.users.models import Profile
from tests.core.factories import (
    EventFactory,
    ProcedureFactory,
    ProjectFactory,
    ProjectSharingFactory,
)
from tests.users.factories import ProfileFactory

pytestmark = pytest.mark.django_db


def _create_source_owned_objects(
    source_profile: Profile,
) -> dict[str, object]:
    """Create one instance for each field the command can transfer."""
    return {
        "project": ProjectFactory(owner=source_profile),
        "procedure": ProcedureFactory(
            owner=source_profile,
            last_updated_by=source_profile,
        ),
        "event": EventFactory(
            profile=source_profile,
            archived_by=source_profile,
            archived_at=timezone.now(),
        ),
        "project_sharing": ProjectSharingFactory(
            shared_by=source_profile,
            user_email=source_profile.email,
        ),
    }


class TestTransferOwnershipForProfile:
    def test_dry_run_lists_objects_without_updating(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        source_profile = ProfileFactory(email="source@example.com")
        destination_profile = ProfileFactory(email="destination@example.com")

        objects = _create_source_owned_objects(source_profile)

        call_command(
            "transfer_ownership_for_profile",
            source_profile.email,
            destination_profile.email,
        )

        output = capsys.readouterr().out
        assert f"Previous owner : {source_profile.email}" in output
        assert f"New owner : {destination_profile.email}" in output
        for obj in objects.values():
            assert str(obj.pk) in output

        # Nothing should have changed in the database.
        assert Project.objects.filter(owner_id=source_profile.user_id).count() == 1
        assert Procedure.objects.filter(owner_id=source_profile.user_id).count() == 1
        assert (
            Procedure.objects.filter(last_updated_by_id=source_profile.user_id).count()
            == 1
        )
        assert Event.objects.filter(profile_id=source_profile.user_id).count() == 1
        assert Event.objects.filter(archived_by_id=source_profile.user_id).count() == 1
        assert (
            ProjectSharing.objects.filter(shared_by_id=source_profile.user_id).count()
            == 1
        )
        assert (
            ProjectSharing.objects.filter(user_email=source_profile.email).count() == 1
        )

    def test_wet_run_transfers_ownership_for_all_fields(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        source_profile = ProfileFactory(email="source@example.com")
        destination_profile = ProfileFactory(email="destination@example.com")

        objects = _create_source_owned_objects(source_profile)

        call_command(
            "transfer_ownership_for_profile",
            source_profile.email,
            destination_profile.email,
            "--wet-run",
        )

        output = capsys.readouterr().out
        for obj in objects.values():
            assert str(obj.pk) in output

        for obj in objects.values():
            obj.refresh_from_db()

        assert str(objects["project"].owner_id) == destination_profile.user_id
        assert str(objects["procedure"].owner_id) == destination_profile.user_id
        assert (
            str(objects["procedure"].last_updated_by_id) == destination_profile.user_id
        )
        assert str(objects["event"].profile_id) == destination_profile.user_id
        assert str(objects["event"].archived_by_id) == destination_profile.user_id
        assert (
            str(objects["project_sharing"].shared_by_id) == destination_profile.user_id
        )
        assert objects["project_sharing"].user_email == destination_profile.email

    def test_wet_run_only_updates_source_objects(
        self,
    ) -> None:
        source_profile = ProfileFactory(email="source@example.com")
        destination_profile = ProfileFactory(email="destination@example.com")
        other_profile = ProfileFactory(email="other@example.com")
        untouched_project = ProjectFactory(owner=other_profile)
        untouched_procedure = ProcedureFactory(
            owner=other_profile,
            last_updated_by=other_profile,
        )
        untouched_event = EventFactory(
            profile=other_profile,
            archived_by=other_profile,
            archived_at=timezone.now(),
        )
        untouched_sharing = ProjectSharingFactory(
            shared_by=other_profile,
            user_email="untouched@example.com",
        )

        _create_source_owned_objects(source_profile)

        call_command(
            "transfer_ownership_for_profile",
            source_profile.email,
            destination_profile.email,
            "--wet-run",
        )

        other_profile.refresh_from_db()
        untouched_project.refresh_from_db()
        untouched_procedure.refresh_from_db()
        untouched_event.refresh_from_db()
        untouched_sharing.refresh_from_db()

        assert untouched_project.owner_id == other_profile.user_id
        assert untouched_procedure.owner_id == other_profile.user_id
        assert untouched_procedure.last_updated_by_id == other_profile.user_id
        assert untouched_event.profile_id == other_profile.user_id
        assert untouched_event.archived_by_id == other_profile.user_id
        assert untouched_sharing.shared_by_id == other_profile.user_id
        assert untouched_sharing.user_email == "untouched@example.com"

    def test_missing_source_profile_raises_error(
        self,
    ) -> None:
        destination_profile = ProfileFactory(email="destination@example.com")
        with pytest.raises(Profile.DoesNotExist):
            call_command(
                "transfer_ownership_for_profile",
                "unknown@example.com",
                destination_profile.email,
            )

    def test_missing_destination_profile_raises_error(
        self,
    ) -> None:
        source_profile = ProfileFactory(email="source@example.com")
        with pytest.raises(Profile.DoesNotExist):
            call_command(
                "transfer_ownership_for_profile",
                source_profile.email,
                "unknown@example.com",
            )
