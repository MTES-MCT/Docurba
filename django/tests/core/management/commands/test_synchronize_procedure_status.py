from datetime import timedelta
from io import StringIO

import pytest
from django.core.management import call_command
from django.utils import timezone

from docurba.core.enums import ProcedureStatusChoices
from docurba.core.models import Procedure
from tests.core.factories import EventFactory, ProcedureFactory


@pytest.mark.django_db
class TestSynchronizeProcedureStatus:
    def test_secondary_returns_none(self) -> None:
        ProcedureFactory(with_parente=True)

        out = StringIO()
        call_command("synchronize_procedure_status", wet_run=False, stdout=out)

        assert out.getvalue() == "procedure_id,ancien_status,nouveau_status\n"

    def test_without_event_returns_en_projet(self) -> None:
        ProcedureFactory()

        out = StringIO()
        call_command("synchronize_procedure_status", wet_run=False, stdout=out)

        assert out.getvalue() == "procedure_id,ancien_status,nouveau_status\n"

    def test_status_from_most_recent_impactful_event(self) -> None:
        now = timezone.now()
        procedure = ProcedureFactory()
        EventFactory(
            procedure=procedure,
            event_type__impact=ProcedureStatusChoices.ABANDON,
            date_evenement=now - timedelta(days=30),
        )
        EventFactory(
            procedure=procedure,
            event_type__impact=ProcedureStatusChoices.OPPOSABLE,
            date_evenement=now,
        )

        out = StringIO()
        call_command("synchronize_procedure_status", wet_run=False, stdout=out)

        assert out.getvalue() == (
            f"procedure_id,ancien_status,nouveau_status\n{procedure.id},en projet,opposable\n"
        )

    def test_archived_event_ignored(self) -> None:
        procedure = ProcedureFactory()
        EventFactory(
            procedure=procedure,
            event_type__impact=ProcedureStatusChoices.OPPOSABLE,
            archived=True,
        )
        EventFactory(
            procedure=procedure,
            event_type__impact=ProcedureStatusChoices.ANNULE,
        )

        out = StringIO()
        call_command("synchronize_procedure_status", wet_run=False, stdout=out)

        assert out.getvalue() == (
            f"procedure_id,ancien_status,nouveau_status\n{procedure.id},en projet,annule\n"
        )

    def test_invalid_event_ignored(self) -> None:
        procedure = ProcedureFactory()
        EventFactory(
            procedure=procedure,
            event_type__impact=ProcedureStatusChoices.OPPOSABLE,
            is_valid=False,
        )
        EventFactory(
            procedure=procedure,
            event_type__impact=ProcedureStatusChoices.ANNULE,
        )

        out = StringIO()
        call_command("synchronize_procedure_status", wet_run=False, stdout=out)

        assert out.getvalue() == (
            f"procedure_id,ancien_status,nouveau_status\n{procedure.id},en projet,annule\n"
        )

    def test_event_without_type_or_type_not_impactful_ignored(self) -> None:
        procedure = ProcedureFactory()
        # Event type not set.
        EventFactory(
            procedure=procedure,
            event_type=None,
        )
        # Event type without impact.
        EventFactory(
            procedure=procedure,
            event_type__impact="",
        )
        EventFactory(
            procedure=procedure,
            event_type__impact=ProcedureStatusChoices.ANNULE,
        )

        out = StringIO()
        call_command("synchronize_procedure_status", wet_run=False, stdout=out)

        assert out.getvalue() == (
            f"procedure_id,ancien_status,nouveau_status\n{procedure.id},en projet,annule\n"
        )

    def test_event_without_date_ignored(self) -> None:
        procedure = ProcedureFactory()
        # Events without a date (historical data) are ignored.
        EventFactory(
            procedure=procedure,
            event_type__impact=ProcedureStatusChoices.OPPOSABLE,
            date_evenement=None,
        )
        EventFactory(
            procedure=procedure,
            event_type__impact=ProcedureStatusChoices.ANNULE,
        )

        out = StringIO()
        call_command("synchronize_procedure_status", wet_run=False, stdout=out)

        assert out.getvalue() == (
            f"procedure_id,ancien_status,nouveau_status\n{procedure.id},en projet,annule\n"
        )

    def test_matching_statuses_not_exported(self) -> None:
        principale = ProcedureFactory()
        secondaire = ProcedureFactory(parente=principale, status=None)

        out = StringIO()
        call_command("synchronize_procedure_status", wet_run=False, stdout=out)

        assert out.getvalue() == "procedure_id,ancien_status,nouveau_status\n"

        principale.refresh_from_db()
        assert principale.status == ProcedureStatusChoices.EN_PROJET

        secondaire.refresh_from_db()
        assert secondaire.status is None

    def test_differing_status_exported_and_updated_with_wet_run(self) -> None:
        outdated_procedure = ProcedureFactory(status=ProcedureStatusChoices.OPPOSABLE)
        EventFactory(
            procedure=outdated_procedure,
            event_type__impact=ProcedureStatusChoices.ANNULE,
        )
        # This procedure is not exported because its status is already up to date.
        ProcedureFactory(status=ProcedureStatusChoices.EN_PROJET)

        expected_csv = (
            "procedure_id,ancien_status,nouveau_status\n"
            f"{outdated_procedure.id},opposable,annule\n"
        )

        out = StringIO()
        call_command("synchronize_procedure_status", wet_run=False, stdout=out)

        assert expected_csv == out.getvalue()
        outdated_procedure.refresh_from_db()
        assert outdated_procedure.status == ProcedureStatusChoices.OPPOSABLE

        out = StringIO()
        call_command("synchronize_procedure_status", wet_run=True, stdout=out)

        assert expected_csv == out.getvalue()
        outdated_procedure.refresh_from_db()
        assert outdated_procedure.status == ProcedureStatusChoices.ANNULE

    def test_secondary_with_status_exported_and_nullified(self) -> None:
        # We are going through an update here to bypass the new validation rules in Procedure.clean
        secondaire = ProcedureFactory(with_parente=True, status=None)
        Procedure.objects.filter(id=secondaire.id).update(
            status=ProcedureStatusChoices.OPPOSABLE
        )

        expected_csv = (
            "procedure_id,ancien_status,nouveau_status\n"
            f"{secondaire.id},{ProcedureStatusChoices.OPPOSABLE},\n"
        )

        out = StringIO()
        call_command("synchronize_procedure_status", wet_run=False, stdout=out)

        assert expected_csv == out.getvalue()

        secondaire.refresh_from_db()
        assert secondaire.status == ProcedureStatusChoices.OPPOSABLE

        out = StringIO()
        call_command("synchronize_procedure_status", wet_run=True, stdout=out)

        assert expected_csv == out.getvalue()

        secondaire.refresh_from_db()
        assert secondaire.status is None

    def test_future_event_not_taken_into_account(self) -> None:
        procedure = ProcedureFactory(status=ProcedureStatusChoices.EN_COURS)
        EventFactory(
            procedure=procedure,
            event_type__impact=ProcedureStatusChoices.OPPOSABLE,
            date_evenement=timezone.now() + timedelta(days=365),
        )

        expected_csv = (
            "procedure_id,ancien_status,nouveau_status\n"
            f"{procedure.id},en cours,en projet\n"
        )

        out = StringIO()
        call_command("synchronize_procedure_status", wet_run=False, stdout=out)

        assert out.getvalue() == expected_csv
        procedure.refresh_from_db()
        assert procedure.status == ProcedureStatusChoices.EN_COURS

        out = StringIO()
        call_command("synchronize_procedure_status", wet_run=True, stdout=out)

        assert out.getvalue() == expected_csv
        procedure.refresh_from_db()
        assert procedure.status == ProcedureStatusChoices.EN_PROJET

    def test_future_event_is_taken_into_account_with_posterior_future_date_pivot(
        self,
    ) -> None:
        procedure = ProcedureFactory(status=ProcedureStatusChoices.EN_COURS)
        EventFactory(
            procedure=procedure,
            event_type__impact=ProcedureStatusChoices.OPPOSABLE,
            date_evenement=timezone.now() + timedelta(days=365),
        )

        expected_csv = (
            "procedure_id,ancien_status,nouveau_status\n"
            f"{procedure.id},en cours,opposable\n"
        )

        date_pivot = (timezone.localdate() + timedelta(days=366)).isoformat()
        out = StringIO()
        call_command(
            "synchronize_procedure_status",
            date_pivot=date_pivot,
            wet_run=False,
            stdout=out,
        )

        assert out.getvalue() == expected_csv
        procedure.refresh_from_db()
        assert procedure.status == ProcedureStatusChoices.EN_COURS

        out = StringIO()
        call_command(
            "synchronize_procedure_status",
            date_pivot=date_pivot,
            wet_run=True,
            stdout=out,
        )

        assert out.getvalue() == expected_csv
        procedure.refresh_from_db()
        assert procedure.status == ProcedureStatusChoices.OPPOSABLE

    def test_events_are_not_taken_into_account_with_anterior_date_pivot(
        self,
    ) -> None:
        now = timezone.now()
        procedure = ProcedureFactory(status=ProcedureStatusChoices.EN_COURS)
        EventFactory(
            procedure=procedure,
            event_type__impact=ProcedureStatusChoices.OPPOSABLE,
            date_evenement=now - timedelta(days=365),
        )
        EventFactory(
            procedure=procedure,
            event_type__impact=ProcedureStatusChoices.APPROUVE,
            date_evenement=now,
        )
        EventFactory(
            procedure=procedure,
            event_type__impact=ProcedureStatusChoices.ABANDON,
            date_evenement=now + timedelta(days=365),
        )

        expected_csv = (
            "procedure_id,ancien_status,nouveau_status\n"
            f"{procedure.id},en cours,en projet\n"
        )

        date_pivot = (timezone.localdate() - timedelta(days=366)).isoformat()
        out = StringIO()
        call_command(
            "synchronize_procedure_status",
            date_pivot=date_pivot,
            wet_run=False,
            stdout=out,
        )

        assert out.getvalue() == expected_csv
        procedure.refresh_from_db()
        assert procedure.status == ProcedureStatusChoices.EN_COURS

        out = StringIO()
        call_command(
            "synchronize_procedure_status",
            date_pivot=date_pivot,
            wet_run=True,
            stdout=out,
        )

        assert out.getvalue() == expected_csv
        procedure.refresh_from_db()
        assert procedure.status == ProcedureStatusChoices.EN_PROJET
