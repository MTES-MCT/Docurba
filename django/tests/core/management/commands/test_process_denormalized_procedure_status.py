from datetime import date, datetime, timedelta
from io import StringIO

import pytest
from django.core.management import call_command
from django.utils import timezone
from freezegun import freeze_time

from docurba.core.enums import ProcedureStatusChoices
from docurba.core.models import Event, Procedure
from tests.core.factories import EventFactory, EventTypeFactory, ProcedureFactory


@pytest.mark.django_db
class TestProcessDenormalizedProcedureStatus:
    def _create_impactful_event(
        self,
        procedure: Procedure,
        impact: ProcedureStatusChoices,
        date_evenement: datetime | None = None,
    ) -> Event:
        _date_evenement = date_evenement or timezone.now()
        event_type = EventTypeFactory(
            name=f"Type {impact} {_date_evenement}", impact=impact
        )
        return EventFactory(
            procedure=procedure,
            event_type=event_type,
            date_evenement=_date_evenement,
        )

    def test_matching_statuses_not_exported(self) -> None:
        principale = ProcedureFactory(status="en projet")
        secondaire = ProcedureFactory(parente=principale, status=None)

        out = StringIO()
        call_command("process_denormalized_procedure_status", wet_run=False, stdout=out)

        assert out.getvalue() == "procedure_id,ancien_status,nouveau_status\n"

        principale.refresh_from_db()
        assert principale.status == "en projet"

        secondaire.refresh_from_db()
        assert secondaire.status is None


    def test_differing_status_exported_and_updated_with_wet_run(self) -> None:
        outdated_procedure = ProcedureFactory(status=ProcedureStatusChoices.OPPOSABLE)
        self._create_impactful_event(
            outdated_procedure,
            ProcedureStatusChoices.ANNULE,
        )
        # This procedure is not exported because its status is already up to date.
        ProcedureFactory(status="en projet")

        expected_csv = (
            "procedure_id,ancien_status,nouveau_status\n"
            f"{outdated_procedure.id},opposable,annule\n"
        )

        out = StringIO()
        call_command("process_denormalized_procedure_status", wet_run=False, stdout=out)

        assert expected_csv == out.getvalue()
        outdated_procedure.refresh_from_db()
        assert outdated_procedure.status == ProcedureStatusChoices.OPPOSABLE

        out = StringIO()
        call_command("process_denormalized_procedure_status", wet_run=True, stdout=out)

        assert expected_csv == out.getvalue()
        outdated_procedure.refresh_from_db()
        assert outdated_procedure.status == ProcedureStatusChoices.ANNULE

    def test_secondary_with_status_exported_and_nullified(self) -> None:
        principale = ProcedureFactory(status="en projet")
        # We are going through an update here to bypass the new validation rules in Procedure.clean
        secondaire = ProcedureFactory(parente=principale, status=None)
        Procedure.objects.filter(id=secondaire.id).update(
            status=ProcedureStatusChoices.OPPOSABLE
        )

        expected_csv = (
            "procedure_id,ancien_status,nouveau_status\n"
            f"{secondaire.id},{ProcedureStatusChoices.OPPOSABLE},\n"
        )

        out = StringIO()
        call_command("process_denormalized_procedure_status", wet_run=False, stdout=out)

        assert expected_csv == out.getvalue()

        secondaire.refresh_from_db()
        assert secondaire.status == ProcedureStatusChoices.OPPOSABLE

        out = StringIO()
        call_command("process_denormalized_procedure_status", wet_run=True, stdout=out)

        assert expected_csv == out.getvalue()

        secondaire.refresh_from_db()
        assert secondaire.status is None

    @freeze_time("2026-01-01")
    def test_future_event_taken_into_account(self) -> None:
        # The command does not use a date pivot: even a future event impacts
        # the computed status.
        procedure = ProcedureFactory(status=ProcedureStatusChoices.EN_COURS)
        self._create_impactful_event(
            procedure,
            ProcedureStatusChoices.OPPOSABLE,
            date_evenement=timezone.now() + timedelta(days=30),
        )

        expected_csv = (
            "procedure_id,ancien_status,nouveau_status\n"
            f"{procedure.id},en cours,opposable\n"
        )

        out = StringIO()
        call_command("process_denormalized_procedure_status", wet_run=False, stdout=out)

        assert out.getvalue() == expected_csv
        procedure.refresh_from_db()
        assert procedure.status == ProcedureStatusChoices.EN_COURS

        out = StringIO()
        call_command("process_denormalized_procedure_status", wet_run=True, stdout=out)

        assert out.getvalue() == expected_csv
        procedure.refresh_from_db()
        assert procedure.status == ProcedureStatusChoices.OPPOSABLE
