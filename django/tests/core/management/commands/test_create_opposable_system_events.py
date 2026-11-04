import csv
from datetime import date
from io import StringIO
from uuid import UUID, uuid4

import pytest
from django.core.management import call_command

from docurba.core.enums import ProcedureStatusChoices
from docurba.core.management.commands.create_opposable_system_events import DESCRIPTION
from docurba.core.models import Event, EventType, Procedure
from tests.core.factories import EventFactory, EventTypeFactory, ProcedureFactory
from tests.users.factories import ProfileFactory

OPPOSABLE_EVENT_NAME = "Caractère exécutoire"


@pytest.mark.django_db
class TestCreateOpposableSystemEvents:
    def _create_impactful_event(
        self,
        procedure: Procedure,
        impact: ProcedureStatusChoices,
        *,
        date_evenement: date,
        document_type: EventType.DocumentType = EventType.DocumentType.PLU,
        **kwargs: dict,
    ) -> Event:
        event_type = EventTypeFactory(
            name=f"Type {impact} {date_evenement} {uuid4().hex[:8]}",
            document_type=document_type,
            impact=impact,
        )
        return EventFactory(
            procedure=procedure,
            event_type=event_type,
            date_evenement=date_evenement,
            **kwargs,
        )

    def _create_opposable_event_type(
        self,
        document_type: EventType.DocumentType = EventType.DocumentType.PLU,
    ) -> EventType:
        return EventTypeFactory(
            document_type=document_type,
            name=OPPOSABLE_EVENT_NAME,
            impact=ProcedureStatusChoices.OPPOSABLE,
            sudocuh_code="SAU",
        )

    def _call_command(self, profile_id: str, *, wet_run: bool) -> list[list[str]]:
        out = StringIO()
        call_command(
            "create_opposable_system_events", profile_id, wet_run=wet_run, stdout=out
        )
        return list(csv.reader(StringIO(out.getvalue())))

    def test_opposable_event_listed_then_created_with_wet_run(self) -> None:
        profile_id = str(ProfileFactory().pk)
        opposable_event_type = self._create_opposable_event_type()
        procedure = ProcedureFactory(status=ProcedureStatusChoices.OPPOSABLE)
        approbation_date = date(2025, 1, 1)
        self._create_impactful_event(
            procedure,
            ProcedureStatusChoices.APPROUVE,
            date_evenement=approbation_date,
        )

        rows = self._call_command(profile_id, wet_run=False)

        expected_row = [
            str(procedure.id),
            str(procedure.project_id),
            str(approbation_date),
            str(opposable_event_type.id),
            OPPOSABLE_EVENT_NAME,
            "SAU",
            "private",
            "True",
            profile_id,
            profile_id,
            DESCRIPTION,
        ]
        assert rows == [
            [
                "procedure_id",
                "project_id",
                "date_iso",
                "event_type_id",
                "type",
                "code",
                "visibility",
                "is_valid",
                "created_by_id",
                "profile_id",
                "description",
            ],
            expected_row,
        ]
        # Dry run must not create anything.
        assert Event.full_objects.count() == 1

        rows = self._call_command(profile_id, wet_run=True)

        assert rows[1] == expected_row
        event = Event.full_objects.get(
            procedure=procedure, event_type=opposable_event_type
        )
        assert event.date_evenement == approbation_date
        assert event.type == OPPOSABLE_EVENT_NAME
        assert event.code == "SAU"
        assert event.visibility == "private"
        assert event.is_valid is True
        assert event.created_by_id == UUID(profile_id)
        assert event.profile_id == UUID(profile_id)
        assert event.project_id == procedure.project_id
        assert event.description == DESCRIPTION

    def test_already_computed_opposable_procedure_not_exported(self) -> None:
        self._create_opposable_event_type()
        procedure = ProcedureFactory(status=ProcedureStatusChoices.OPPOSABLE)
        self._create_impactful_event(
            procedure,
            ProcedureStatusChoices.OPPOSABLE,
            date_evenement=date(2025, 1, 1),
        )

        rows = self._call_command(str(ProfileFactory().pk), wet_run=False)

        assert len(rows) == 1

    def test_procedure_without_impactful_event_not_exported(self) -> None:
        # Without any impactful event the procedure computes as "en projet",
        # not as "approuve".
        self._create_opposable_event_type()
        ProcedureFactory(status=ProcedureStatusChoices.OPPOSABLE)

        rows = self._call_command(str(ProfileFactory().pk), wet_run=False)

        assert len(rows) == 1

    def test_secondary_procedure_not_exported(self) -> None:
        # A secondary procedure computes as NULL, even with an approbation
        # event attached.
        self._create_opposable_event_type()
        principale = ProcedureFactory()
        secondaire = ProcedureFactory(with_parente=True, parente=principale)
        # Bypass Procedure.clean which forbids a status on secondary procedures.
        Procedure.objects.filter(id=secondaire.id).update(
            status=ProcedureStatusChoices.OPPOSABLE
        )
        self._create_impactful_event(
            secondaire,
            ProcedureStatusChoices.APPROUVE,
            date_evenement=date(2025, 1, 1),
        )

        rows = self._call_command(str(ProfileFactory().pk), wet_run=False)

        assert len(rows) == 1

    def test_last_impactful_event_not_approuve_not_exported(self) -> None:
        # The most recent impactful event drives the computed status: an
        # annulation after the approbation computes as "annule".
        self._create_opposable_event_type()
        procedure = ProcedureFactory(status=ProcedureStatusChoices.OPPOSABLE)
        self._create_impactful_event(
            procedure,
            ProcedureStatusChoices.APPROUVE,
            date_evenement=date(2024, 6, 1),
        )
        self._create_impactful_event(
            procedure,
            ProcedureStatusChoices.ANNULE,
            date_evenement=date(2025, 1, 1),
        )

        rows = self._call_command(str(ProfileFactory().pk), wet_run=False)

        assert len(rows) == 1

    def test_events_without_impact_ignored(self) -> None:
        # Events whose type has no impact never enter the computation: the
        # older approbation event still drives the computed status.
        self._create_opposable_event_type()
        procedure = ProcedureFactory(status=ProcedureStatusChoices.OPPOSABLE)
        self._create_impactful_event(
            procedure,
            ProcedureStatusChoices.APPROUVE,
            date_evenement=date(2024, 6, 1),
        )
        self._create_impactful_event(
            procedure,
            "",
            date_evenement=date(2025, 1, 1),
        )

        rows = self._call_command(str(ProfileFactory().pk), wet_run=False)

        assert len(rows) == 2

    def test_invalid_and_archived_events_ignored(self) -> None:
        self._create_opposable_event_type()
        procedure_invalid = ProcedureFactory(status=ProcedureStatusChoices.OPPOSABLE)
        self._create_impactful_event(
            procedure_invalid,
            ProcedureStatusChoices.APPROUVE,
            date_evenement=date(2025, 1, 1),
            is_valid=False,
        )
        procedure_archived = ProcedureFactory(status=ProcedureStatusChoices.OPPOSABLE)
        self._create_impactful_event(
            procedure_archived,
            ProcedureStatusChoices.APPROUVE,
            date_evenement=date(2025, 1, 1),
            archived=True,
        )

        rows = self._call_command(str(ProfileFactory().pk), wet_run=False)

        assert len(rows) == 1
        # Both procedures compute as "en projet" without their ignored events.
        assert Event.full_objects.count() == 2

    def test_opposable_event_type_missing_for_document_type_not_exported(self) -> None:
        # The opposable event type is joined on its document type: an SCOT
        # opposable event type cannot fill a PLU procedure.
        self._create_opposable_event_type(EventType.DocumentType.SCOT)
        procedure = ProcedureFactory(status=ProcedureStatusChoices.OPPOSABLE)
        self._create_impactful_event(
            procedure,
            ProcedureStatusChoices.APPROUVE,
            date_evenement=date(2025, 1, 1),
            document_type=EventType.DocumentType.PLU,
        )

        rows = self._call_command(str(ProfileFactory().pk), wet_run=False)

        assert len(rows) == 1

    def test_several_procedures_exported(self) -> None:
        self._create_opposable_event_type()
        procedures = [
            ProcedureFactory(status=ProcedureStatusChoices.OPPOSABLE) for _ in range(2)
        ]
        for index, procedure in enumerate(procedures):
            self._create_impactful_event(
                procedure,
                ProcedureStatusChoices.APPROUVE,
                date_evenement=date(2025, 1, index + 1),
            )

        rows = self._call_command(str(ProfileFactory().pk), wet_run=False)

        assert len(rows) == 3
        assert {row[0] for row in rows[1:]} == {str(p.id) for p in procedures}
