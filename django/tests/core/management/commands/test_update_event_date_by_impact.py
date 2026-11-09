import csv
from datetime import datetime, timedelta
from io import StringIO
from uuid import uuid4

import pytest
from django.core.management import call_command
from django.utils import timezone
from freezegun import freeze_time

from docurba.core.enums import ProcedureStatusChoices
from docurba.core.models import Event, EventType, Procedure
from tests.core.factories import EventFactory, EventTypeFactory, ProcedureFactory


def parse_timestamp(value: str) -> datetime:
    return datetime.fromisoformat(value)


@pytest.mark.django_db
class TestUpdateEventDateByImpact:
    def _create_event(
        self,
        procedure: Procedure,
        impact: ProcedureStatusChoices | str,
        *,
        date_evenement: datetime,
        created_at: datetime | None = None,
        from_sudocuh: int | None = None,
        **kwargs: dict,
    ) -> Event:
        # The uuid suffix prevents unique constraint violations when several
        # event types are created for the same document type.
        event_type = EventTypeFactory(
            name=f"Type {impact} {uuid4().hex[:8]}",
            document_type=EventType.DocumentType.PLU,
            impact=impact,
        )
        return EventFactory(
            procedure=procedure,
            event_type=event_type,
            date_evenement=date_evenement,
            created_at=created_at,
            from_sudocuh=from_sudocuh,
            **kwargs,
        )

    def _call_command(self, *, wet_run: bool) -> list[list[str]]:
        out = StringIO()
        call_command("update_event_date_by_impact", wet_run=wet_run, stdout=out)
        return list(csv.reader(StringIO(out.getvalue())))

    @freeze_time("2024-12-01")
    def test_events_shifted_by_impact_priority(self) -> None:
        # Within a (procedure, date) group, the event with the lowest impact
        # priority keeps the original date, the next ones are pushed forward
        # by one millisecond per rank.
        now = timezone.now()
        procedure = ProcedureFactory()
        events = [
            self._create_event(procedure, "en projet", date_evenement=now),
            self._create_event(
                procedure, ProcedureStatusChoices.EN_COURS, date_evenement=now
            ),
            self._create_event(
                procedure, ProcedureStatusChoices.ABANDON, date_evenement=now
            ),
            self._create_event(procedure, "approuve", date_evenement=now),
            self._create_event(
                procedure, ProcedureStatusChoices.OPPOSABLE, date_evenement=now
            ),
            self._create_event(
                procedure, ProcedureStatusChoices.ANNULE, date_evenement=now
            ),
            self._create_event(procedure, "abroge", date_evenement=now),
            self._create_event(
                procedure, ProcedureStatusChoices.CADUC, date_evenement=now
            ),
        ]

        rows = self._call_command(wet_run=False)

        assert rows[0] == ["event_id", "old_date_iso", "new_date_iso"]
        expected = sorted(
            (
                (str(event.id), now, now + timedelta(hours=i))
                for i, event in enumerate(events[1:], start=1)
            ),
            key=lambda row: row[0],
        )
        exported = [
            (row[0], parse_timestamp(row[1]), parse_timestamp(row[2]))
            for row in rows[1:]
        ]
        assert exported == expected
        # Dry run must not modify anything.
        for event in events:
            event.refresh_from_db()
            assert event.date_evenement == now

        rows = self._call_command(wet_run=True)

        exported = [
            (row[0], parse_timestamp(row[1]), parse_timestamp(row[2]))
            for row in rows[1:]
        ]
        assert exported == expected
        for i, event in enumerate(events):
            event.refresh_from_db()
            assert event.date_evenement == now + timedelta(hours=i)

    @freeze_time("2024-12-01")
    def test_event_without_impact_keeps_the_original_date(self) -> None:
        # The CASE fallback (impact "") ranks before every impactful impact,
        # so a non-impactful event always keeps the original date.
        now = timezone.now()
        procedure = ProcedureFactory()
        without_impact = self._create_event(procedure, "", date_evenement=now)
        caduc = self._create_event(
            procedure, ProcedureStatusChoices.CADUC, date_evenement=now
        )

        rows = self._call_command(wet_run=True)

        assert rows[1] == [
            str(caduc.id),
            str(now),
            str(now + timedelta(hours=1)),
        ]

        without_impact.refresh_from_db()
        caduc.refresh_from_db()
        assert without_impact.date_evenement == now
        assert caduc.date_evenement == now + timedelta(hours=1)

    @freeze_time("2024-12-01")
    def test_same_impact_ordered_by_created_at(self) -> None:
        # Among events sharing the same impact, the oldest created_at keeps
        # the original date, the most recent one is pushed forward.
        now = timezone.now()
        procedure = ProcedureFactory()
        older = self._create_event(
            procedure,
            ProcedureStatusChoices.ABANDON,
            date_evenement=now,
            created_at=now - timedelta(minutes=10),
        )
        newer = self._create_event(
            procedure,
            ProcedureStatusChoices.ABANDON,
            date_evenement=now,
            created_at=now,
        )

        rows = self._call_command(wet_run=True)

        assert rows[1] == [
            str(newer.id),
            str(now),
            str(now + timedelta(hours=1)),
        ]

        older.refresh_from_db()
        newer.refresh_from_db()
        assert older.date_evenement == now
        assert newer.date_evenement == now + timedelta(hours=1)

    @freeze_time("2024-12-01")
    def test_same_impact_and_created_at_ordered_by_from_sudocuh(self) -> None:
        # from_sudocuh is the last tie-breaker: the lowest value keeps the
        # original date.
        now = timezone.now()
        procedure = ProcedureFactory()
        first = self._create_event(
            procedure,
            ProcedureStatusChoices.ABANDON,
            date_evenement=now,
            created_at=now,
            from_sudocuh=1,
        )
        second = self._create_event(
            procedure,
            ProcedureStatusChoices.ABANDON,
            date_evenement=now,
            created_at=now,
            from_sudocuh=2,
        )

        rows = self._call_command(wet_run=True)

        assert rows[1] == [
            str(second.id),
            str(now),
            str(now + timedelta(hours=1)),
        ]

        first.refresh_from_db()
        second.refresh_from_db()
        assert first.date_evenement == now
        assert second.date_evenement == now + timedelta(hours=1)

    @freeze_time("2024-12-01")
    def test_event_without_date_not_exported(self) -> None:
        now = timezone.now()
        procedure = ProcedureFactory()
        dated_first = self._create_event(
            procedure, ProcedureStatusChoices.EN_COURS, date_evenement=now
        )
        dated_second = self._create_event(
            procedure, ProcedureStatusChoices.OPPOSABLE, date_evenement=now
        )
        undated = EventFactory(procedure=procedure, date_evenement=None)

        rows = self._call_command(wet_run=True)

        assert rows[1] == [
            str(dated_second.id),
            str(now),
            str(now + timedelta(hours=1)),
        ]
        undated.refresh_from_db()
        dated_first.refresh_from_db()
        dated_second.refresh_from_db()
        assert undated.date_evenement is None
        assert dated_first.date_evenement == now
        assert dated_second.date_evenement == now + timedelta(hours=1)

    @freeze_time("2024-12-01")
    def test_procedure_without_duplicates_not_exported(self) -> None:
        now = timezone.now()
        lonely = self._create_event(
            ProcedureFactory(), ProcedureStatusChoices.EN_COURS, date_evenement=now
        )
        spaced_procedure = ProcedureFactory()
        first = self._create_event(
            spaced_procedure, ProcedureStatusChoices.EN_COURS, date_evenement=now
        )
        second = self._create_event(
            spaced_procedure,
            ProcedureStatusChoices.OPPOSABLE,
            date_evenement=now + timedelta(days=1),
        )

        rows = self._call_command(wet_run=True)

        assert rows == [["event_id", "old_date_iso", "new_date_iso"]]
        lonely.refresh_from_db()
        first.refresh_from_db()
        second.refresh_from_db()
        assert lonely.date_evenement == now
        assert first.date_evenement == now
        assert second.date_evenement == now + timedelta(days=1)

    @freeze_time("2024-12-01")
    def test_same_date_in_different_procedures_not_grouped(self) -> None:
        now = timezone.now()
        for _ in range(2):
            self._create_event(
                ProcedureFactory(),
                ProcedureStatusChoices.EN_COURS,
                date_evenement=now,
            )

        rows = self._call_command(wet_run=True)

        assert rows == [["event_id", "old_date_iso", "new_date_iso"]]

    @freeze_time("2024-12-01")
    def test_archived_and_invalid_events_also_shifted(self) -> None:
        # Unlike the impactful computations, this command processes every
        # event: the future unique constraint applies to the whole table.
        now = timezone.now()
        procedure = ProcedureFactory()
        valid = self._create_event(
            procedure, ProcedureStatusChoices.EN_COURS, date_evenement=now
        )
        archived = self._create_event(
            procedure,
            ProcedureStatusChoices.OPPOSABLE,
            date_evenement=now,
            archived=True,
        )
        invalid = self._create_event(
            procedure,
            ProcedureStatusChoices.ANNULE,
            date_evenement=now,
            is_valid=False,
        )

        rows = self._call_command(wet_run=True)

        exported = [
            (row[0], parse_timestamp(row[1]), parse_timestamp(row[2]))
            for row in rows[1:]
        ]
        assert exported == sorted(
            [
                (str(archived.id), now, now + timedelta(hours=1)),
                (str(invalid.id), now, now + timedelta(hours=2)),
            ],
            key=lambda row: row[0],
        )
        valid.refresh_from_db()
        archived.refresh_from_db()
        invalid.refresh_from_db()
        assert valid.date_evenement == now
        assert archived.date_evenement == now + timedelta(hours=1)
        assert invalid.date_evenement == now + timedelta(hours=2)

    @freeze_time("2024-12-01")
    def test_wet_run_is_idempotent(self) -> None:
        now = timezone.now()
        procedure = ProcedureFactory()
        self._create_event(
            procedure, ProcedureStatusChoices.EN_COURS, date_evenement=now
        )
        self._create_event(
            procedure, ProcedureStatusChoices.OPPOSABLE, date_evenement=now
        )

        rows = self._call_command(wet_run=True)
        assert len(rows) == 2

        rows = self._call_command(wet_run=True)
        assert rows == [["event_id", "old_date_iso", "new_date_iso"]]
