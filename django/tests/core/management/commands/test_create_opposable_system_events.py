import csv
from datetime import timedelta
from io import StringIO
from uuid import UUID

import pytest
from django.core.management import call_command
from django.utils import timezone
from freezegun import freeze_time

from docurba.core.enums import BaseDocumentType, ProcedureStatusChoices
from docurba.core.management.commands.create_opposable_system_events import DESCRIPTION
from docurba.core.models import Event, EventType, Procedure
from tests.core.factories import EventFactory, EventTypeFactory, ProcedureFactory
from tests.users.factories import ProfileFactory

OPPOSABLE_EVENT_NAME = "Caractère exécutoire"


@pytest.mark.django_db
class TestCreateOpposableSystemEvents:
    def _call_command(self, profile_id: str, *, wet_run: bool) -> list[list[str]]:
        out = StringIO()
        call_command(
            "create_opposable_system_events", profile_id, wet_run=wet_run, stdout=out
        )
        return list(csv.reader(StringIO(out.getvalue())))

    @freeze_time("2025-01-01")
    def test_opposable_event_listed_then_created_with_wet_run(self) -> None:
        profile_id = str(ProfileFactory().pk)
        opposable_event_type = EventTypeFactory(
            document_type=EventType.DocumentType.PLU,
            name=OPPOSABLE_EVENT_NAME,
            impact=ProcedureStatusChoices.OPPOSABLE,
            sudocuh_code="SAU",
        )
        now = timezone.now()
        approbation_date = now + timedelta(hours=1)
        event = EventFactory(
            procedure__base_doc_type=BaseDocumentType.PLU,
            procedure__status=ProcedureStatusChoices.OPPOSABLE,
            event_type__impact=ProcedureStatusChoices.APPROUVE,
            date_evenement=now,
        )

        rows = self._call_command(profile_id, wet_run=False)

        expected_row = [
            str(event.procedure.id),
            str(event.procedure.project_id),
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
            procedure=event.procedure, event_type=opposable_event_type
        )
        assert event.date_evenement == approbation_date
        assert event.type == OPPOSABLE_EVENT_NAME
        assert event.code == "SAU"
        assert event.visibility == "private"
        assert event.is_valid is True
        assert event.created_by_id == UUID(profile_id)
        assert event.profile_id == UUID(profile_id)
        assert event.project_id == event.procedure.project_id
        assert event.description == DESCRIPTION

    def test_already_computed_opposable_procedure_not_exported(self) -> None:
        EventTypeFactory(
            document_type=EventType.DocumentType.PLU,
            name=OPPOSABLE_EVENT_NAME,
            impact=ProcedureStatusChoices.OPPOSABLE,
        )
        EventFactory(
            procedure__base_doc_type=BaseDocumentType.PLU,
            procedure__status=ProcedureStatusChoices.OPPOSABLE,
            event_type__impact=ProcedureStatusChoices.OPPOSABLE,
        )

        rows = self._call_command(str(ProfileFactory().pk), wet_run=False)

        assert len(rows) == 1

    def test_procedure_without_impactful_event_not_exported(self) -> None:
        # Without any impactful event the procedure computes as "en projet",
        # not as "approuve".
        EventTypeFactory(
            document_type=EventType.DocumentType.PLU,
            name=OPPOSABLE_EVENT_NAME,
            impact=ProcedureStatusChoices.OPPOSABLE,
        )
        ProcedureFactory(
            base_doc_type=BaseDocumentType.PLU, status=ProcedureStatusChoices.OPPOSABLE
        )

        rows = self._call_command(str(ProfileFactory().pk), wet_run=False)

        assert len(rows) == 1

    def test_secondary_procedure_not_exported(self) -> None:
        # A secondary procedure computes as NULL, even with an approbation
        # event attached.
        EventTypeFactory(
            document_type=EventType.DocumentType.PLU,
            name=OPPOSABLE_EVENT_NAME,
            impact=ProcedureStatusChoices.OPPOSABLE,
        )
        principale = ProcedureFactory(base_doc_type=BaseDocumentType.PLU)
        secondaire = ProcedureFactory(with_parente=True, parente=principale)
        # Bypass Procedure.clean which forbids a status on secondary procedures.
        Procedure.objects.filter(id=secondaire.id).update(
            status=ProcedureStatusChoices.OPPOSABLE
        )
        EventFactory(
            procedure=secondaire,
            event_type__impact=ProcedureStatusChoices.APPROUVE,
        )

        rows = self._call_command(str(ProfileFactory().pk), wet_run=False)

        assert len(rows) == 1

    @freeze_time("2025-01-01")
    def test_last_impactful_event_not_approuve_not_exported(self) -> None:
        # The most recent impactful event drives the computed status: an
        # annulation after the approbation computes as "annule".
        now = timezone.now()
        EventTypeFactory(
            document_type=EventType.DocumentType.PLU,
            name=OPPOSABLE_EVENT_NAME,
            impact=ProcedureStatusChoices.OPPOSABLE,
        )
        procedure = ProcedureFactory(
            base_doc_type=BaseDocumentType.PLU, status=ProcedureStatusChoices.OPPOSABLE
        )
        EventFactory(
            procedure=procedure,
            event_type__impact=ProcedureStatusChoices.APPROUVE,
            date_evenement=now - timedelta(days=30),
        )
        EventFactory(
            procedure=procedure,
            event_type__impact=ProcedureStatusChoices.ANNULE,
            date_evenement=now,
        )

        rows = self._call_command(str(ProfileFactory().pk), wet_run=False)

        assert len(rows) == 1

    @freeze_time("2025-01-01")
    def test_events_without_impact_ignored(self) -> None:
        # Events whose type has no impact never enter the computation: the
        # older approbation event still drives the computed status.
        now = timezone.now()
        EventTypeFactory(
            document_type=EventType.DocumentType.PLU,
            name=OPPOSABLE_EVENT_NAME,
            impact=ProcedureStatusChoices.OPPOSABLE,
        )
        procedure = ProcedureFactory(
            base_doc_type=BaseDocumentType.PLU, status=ProcedureStatusChoices.OPPOSABLE
        )
        EventFactory(
            procedure=procedure,
            event_type__impact=ProcedureStatusChoices.APPROUVE,
            date_evenement=now - timedelta(days=30),
        )
        EventFactory(
            procedure=procedure,
            event_type__impact="",
            date_evenement=now,
        )

        rows = self._call_command(str(ProfileFactory().pk), wet_run=False)

        assert len(rows) == 2

    def test_invalid_and_archived_events_ignored(self) -> None:
        EventTypeFactory(
            document_type=EventType.DocumentType.PLU,
            name=OPPOSABLE_EVENT_NAME,
            impact=ProcedureStatusChoices.OPPOSABLE,
        )
        EventFactory(
            procedure__base_doc_type=BaseDocumentType.PLU,
            procedure__status=ProcedureStatusChoices.OPPOSABLE,
            event_type__impact=ProcedureStatusChoices.APPROUVE,
            is_valid=False,
        )
        EventFactory(
            procedure__base_doc_type=BaseDocumentType.PLU,
            procedure__status=ProcedureStatusChoices.OPPOSABLE,
            event_type__impact=ProcedureStatusChoices.APPROUVE,
            archived=True,
        )

        rows = self._call_command(str(ProfileFactory().pk), wet_run=False)

        assert len(rows) == 1
        # Both procedures compute as "en projet" without their ignored events.
        assert Event.full_objects.count() == 2

    def test_opposable_event_type_missing_for_document_type_not_exported(self) -> None:
        # The opposable event type is joined on its document type: an SCOT
        # opposable event type cannot fill a PLU procedure.
        EventTypeFactory(
            document_type=EventType.DocumentType.SCOT,
            name=OPPOSABLE_EVENT_NAME,
            impact=ProcedureStatusChoices.OPPOSABLE,
        )
        EventFactory(
            procedure__base_doc_type=BaseDocumentType.PLU,
            procedure__status=ProcedureStatusChoices.OPPOSABLE,
            event_type__impact=ProcedureStatusChoices.APPROUVE,
        )

        rows = self._call_command(str(ProfileFactory().pk), wet_run=False)

        assert len(rows) == 1

    def test_several_procedures_exported(self) -> None:
        procedures = []
        for document_type in EventType.DocumentType:
            EventTypeFactory(
                document_type=document_type,
                name=OPPOSABLE_EVENT_NAME,
                impact=ProcedureStatusChoices.OPPOSABLE,
            )
            event = EventFactory(
                procedure__base_doc_type=document_type,
                procedure__status=ProcedureStatusChoices.OPPOSABLE,
                event_type__impact=ProcedureStatusChoices.APPROUVE,
            )
            procedures.append(event.procedure)

        rows = self._call_command(str(ProfileFactory().pk), wet_run=False)

        assert len(rows) == 4
        assert {row[0] for row in rows[1:]} == {str(p.id) for p in procedures}
