from datetime import UTC, date, datetime, timedelta
from io import StringIO

import pytest
from django.core.management import call_command

from docurba.core.enums import ProcedureStatusChoices
from docurba.core.models import Event, Procedure
from tests.core.factories import EventFactory, EventTypeFactory, ProcedureFactory

CREATED_AT = datetime(2024, 6, 1, 12, 0, 0, tzinfo=UTC)


def _format_timestamp(value: datetime) -> str:
    # Mirrors the to_char(..., 'yyyy-mm-dd hh:mi:ss:us') format used by the command
    return f"{value:%Y-%m-%d} {value.hour:02d}:{value.minute:02d}:{value.second:02d}:{value.microsecond:06d}"


def _sorted_csv_lines(output: str) -> list[str]:
    # The command does not ORDER BY its output: compare lines, not order.
    return sorted(output.splitlines()[1:])


@pytest.mark.django_db
class TestUpdateEventCreatedAt:
    def _create_event(
        self,
        procedure: Procedure,
        *,
        impact: ProcedureStatusChoices | str,
        name: str,
        date_evenement: date,
        created_at: datetime = CREATED_AT,
        **kwargs: dict,
    ) -> Event:
        event_type = EventTypeFactory(name=name, impact=impact)
        return EventFactory(
            procedure=procedure,
            event_type=event_type,
            date_evenement=date_evenement,
            created_at=created_at,
            **kwargs,
        )

    def test_events_with_distinct_created_at_not_exported(self) -> None:
        procedure = ProcedureFactory()
        self._create_event(
            procedure,
            impact=ProcedureStatusChoices.EN_COURS,
            name="Type en cours distinct",
            date_evenement=date(2024, 6, 1),
        )
        self._create_event(
            procedure,
            impact=ProcedureStatusChoices.OPPOSABLE,
            name="Type opposable distinct",
            date_evenement=date(2024, 6, 2),
            created_at=CREATED_AT + timedelta(seconds=1),
        )

        out = StringIO()
        call_command("update_event_created_at", wet_run=False, stdout=out)

        assert out.getvalue() == "event_id,old_created_at,new_created_at\n"

    def test_duplicate_created_at_exported_and_updated_with_wet_run(self) -> None:
        procedure = ProcedureFactory()
        event_en_cours = self._create_event(
            procedure,
            impact=ProcedureStatusChoices.EN_COURS,
            name="Type en cours duplique",
            date_evenement=date(2024, 6, 1),
        )
        event_opposable = self._create_event(
            procedure,
            impact=ProcedureStatusChoices.OPPOSABLE,
            name="Type opposable duplique",
            date_evenement=date(2024, 6, 2),
        )

        expected_csv = (
            "event_id,old_created_at,new_created_at\n"
            f"{event_en_cours.id},{_format_timestamp(CREATED_AT)},{_format_timestamp(CREATED_AT + timedelta(milliseconds=1))}\n"
            f"{event_opposable.id},{_format_timestamp(CREATED_AT)},{_format_timestamp(CREATED_AT + timedelta(milliseconds=4, microseconds=1))}\n"
        )

        out = StringIO()
        call_command("update_event_created_at", wet_run=False, stdout=out)

        assert _sorted_csv_lines(out.getvalue()) == _sorted_csv_lines(expected_csv)
        event_en_cours.refresh_from_db()
        event_opposable.refresh_from_db()
        assert event_en_cours.created_at == CREATED_AT

        out = StringIO()
        call_command("update_event_created_at", wet_run=True, stdout=out)

        assert _sorted_csv_lines(out.getvalue()) == _sorted_csv_lines(expected_csv)
        event_en_cours.refresh_from_db()
        event_opposable.refresh_from_db()
        # The first event by (date_iso, from_sudocuh) gets the row weight of 0
        # microsecond; the impact weight is added in milliseconds.
        assert event_en_cours.created_at == CREATED_AT + timedelta(milliseconds=1)
        assert event_opposable.created_at == CREATED_AT + timedelta(
            milliseconds=4, microseconds=1
        )

    def test_impact_weight_takes_priority_over_row_weight(self) -> None:
        # Even with a worse (date_iso, from_sudocuh) position, the event with
        # the higher impact weight ends up with a later creation date because
        # milliseconds dominate microseconds.
        procedure = ProcedureFactory()
        event_caduc = self._create_event(
            procedure,
            impact=ProcedureStatusChoices.CADUC,
            name="Type caduc prioritaire",
            date_evenement=date(2024, 6, 1),
            from_sudocuh=100,
        )
        event_en_cours = self._create_event(
            procedure,
            impact=ProcedureStatusChoices.EN_COURS,
            name="Type en cours non prioritaire",
            date_evenement=date(2024, 6, 2),
            from_sudocuh=200,
        )

        out = StringIO()
        call_command("update_event_created_at", wet_run=True, stdout=out)

        event_caduc.refresh_from_db()
        event_en_cours.refresh_from_db()
        assert event_caduc.created_at == CREATED_AT + timedelta(milliseconds=7)
        assert event_en_cours.created_at == CREATED_AT + timedelta(
            milliseconds=1, microseconds=1
        )

    def test_event_without_impact_gets_zero_weight(self) -> None:
        procedure = ProcedureFactory()
        event_without_impact = self._create_event(
            procedure,
            impact="",
            name="Type sans impact A",
            date_evenement=date(2024, 6, 1),
            from_sudocuh=100,
        )
        event_en_cours = self._create_event(
            procedure,
            impact=ProcedureStatusChoices.EN_COURS,
            name="Type en cours avec impact",
            date_evenement=date(2024, 6, 2),
            from_sudocuh=200,
        )

        expected_csv = (
            "event_id,old_created_at,new_created_at\n"
            f"{event_en_cours.id},{_format_timestamp(CREATED_AT)},{_format_timestamp(CREATED_AT + timedelta(milliseconds=1, microseconds=1))}\n"
        )

        out = StringIO()
        call_command("update_event_created_at", wet_run=True, stdout=out)

        assert out.getvalue() == expected_csv

        event_without_impact.refresh_from_db()
        event_en_cours.refresh_from_db()
        # Row weight only: the first event keeps its original creation date.
        assert event_without_impact.created_at == CREATED_AT
        assert event_en_cours.created_at == CREATED_AT + timedelta(
            milliseconds=1, microseconds=1
        )

    def test_events_without_duplicate_are_not_updated(self) -> None:
        # Events without a duplicated created_at are still shifted by their
        # impact weight once their procedure is affected.
        procedure = ProcedureFactory()
        event_a = self._create_event(
            procedure,
            impact=ProcedureStatusChoices.EN_COURS,
            name="Type en cours groupe duplique",
            date_evenement=date(2024, 6, 1),
        )
        event_b = self._create_event(
            procedure,
            impact=ProcedureStatusChoices.OPPOSABLE,
            name="Type opposable groupe duplique",
            date_evenement=date(2024, 6, 2),
        )
        unique_created_at = CREATED_AT + timedelta(seconds=10)
        event_unique = self._create_event(
            procedure,
            impact=ProcedureStatusChoices.ANNULE,
            name="Type annule sans doublon",
            date_evenement=date(2024, 6, 3),
            created_at=unique_created_at,
        )

        out = StringIO()
        call_command("update_event_created_at", wet_run=True, stdout=out)

        event_a.refresh_from_db()
        event_b.refresh_from_db()
        event_unique.refresh_from_db()
        assert event_unique.created_at == unique_created_at
        assert len(_sorted_csv_lines(out.getvalue())) == 2
