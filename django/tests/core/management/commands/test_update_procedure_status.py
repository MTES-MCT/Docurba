from datetime import date
from io import StringIO

import pytest
from django.core.management import call_command
from pytest_django import DjangoAssertNumQueries

from docurba.core.enums import ProcedureStatusChoices
from docurba.core.models import Event, Procedure
from tests.core.factories import EventFactory, EventTypeFactory, ProcedureFactory


@pytest.mark.django_db
class TestUpdateProcedureStatus:
    def _create_impactful_event(
        self,
        procedure: Procedure,
        impact: ProcedureStatusChoices,
        *,
        date_evenement: date,
    ) -> Event:
        event_type = EventTypeFactory(
            name=f"Type {impact} {date_evenement}", impact=impact
        )
        return EventFactory(
            procedure=procedure,
            event_type=event_type,
            date_evenement=date_evenement,
        )

    def test_matching_statuses_not_exported(self) -> None:
        procedure = ProcedureFactory(status=ProcedureStatusChoices.EN_COURS)

        out = StringIO()
        call_command("update_procedure_status", wet_run=False, stdout=out)

        assert out.getvalue() == "procedure_id,ancien_status,nouveau_status\n"

        procedure.refresh_from_db()
        assert procedure.status == ProcedureStatusChoices.EN_COURS

    def test_differing_status_exported_and_updated_with_wet_run(self) -> None:
        outdated_procedure = ProcedureFactory(status=ProcedureStatusChoices.OPPOSABLE)
        self._create_impactful_event(
            outdated_procedure,
            ProcedureStatusChoices.ANNULE,
            date_evenement=date(2024, 6, 1),
        )
        # This procedure is not exported because its status is already up to date.
        ProcedureFactory(status=ProcedureStatusChoices.EN_COURS)

        expected_csv = (
            "procedure_id,ancien_status,nouveau_status\n"
            f"{outdated_procedure.id},opposable,annule\n"
        )

        out = StringIO()
        call_command("update_procedure_status", wet_run=False, stdout=out)

        assert expected_csv == out.getvalue()
        outdated_procedure.refresh_from_db()
        assert outdated_procedure.status == ProcedureStatusChoices.OPPOSABLE

        out = StringIO()
        call_command("update_procedure_status", wet_run=True, stdout=out)

        assert expected_csv == out.getvalue()
        outdated_procedure.refresh_from_db()
        assert outdated_procedure.status == ProcedureStatusChoices.ANNULE

    def test_secondary_procedure_ignored(self) -> None:
        # Secondary procedures have no status and are ignored by the command,
        # even with an impactful event.
        procedure = ProcedureFactory(
            status=None,
            with_parente=True,
            parente__status=ProcedureStatusChoices.EN_COURS,
        )
        self._create_impactful_event(
            procedure,
            ProcedureStatusChoices.ANNULE,
            date_evenement=date(2024, 6, 1),
        )

        out = StringIO()
        call_command("update_procedure_status", wet_run=True, stdout=out)

        assert out.getvalue() == "procedure_id,ancien_status,nouveau_status\n"
        procedure.refresh_from_db()
        assert procedure.status is None

    def test_future_event_taken_into_account(self) -> None:
        # The command does not use a date pivot: even a future event impacts
        # the computed status.
        procedure = ProcedureFactory(status=ProcedureStatusChoices.EN_COURS)
        self._create_impactful_event(
            procedure,
            ProcedureStatusChoices.OPPOSABLE,
            date_evenement=date(2999, 12, 1),
        )

        expected_csv = (
            "procedure_id,ancien_status,nouveau_status\n"
            f"{procedure.id},en cours,opposable\n"
        )

        out = StringIO()
        call_command("update_procedure_status", wet_run=False, stdout=out)

        assert out.getvalue() == expected_csv
        procedure.refresh_from_db()
        assert procedure.status == ProcedureStatusChoices.EN_COURS

        out = StringIO()
        call_command("update_procedure_status", wet_run=True, stdout=out)

        assert out.getvalue() == expected_csv
        procedure.refresh_from_db()
        assert procedure.status == ProcedureStatusChoices.OPPOSABLE

    def test_wet_run_updates_in_a_single_bulk(
        self, django_assert_num_queries: DjangoAssertNumQueries
    ) -> None:
        procedures = [
            ProcedureFactory(status=ProcedureStatusChoices.OPPOSABLE) for _ in range(3)
        ]
        for index, procedure in enumerate(procedures):
            self._create_impactful_event(
                procedure,
                ProcedureStatusChoices.ANNULE,
                date_evenement=date(2024, 6, 1 + index),
            )

        out = StringIO()
        # 1 query for procedures + 1 for the prefetch + a single UPDATE.
        with django_assert_num_queries(3):
            call_command("update_procedure_status", wet_run=True, stdout=out)

        for procedure in procedures:
            procedure.refresh_from_db()
            assert procedure.status == ProcedureStatusChoices.ANNULE
