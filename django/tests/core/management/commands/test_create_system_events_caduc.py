import csv
from datetime import timedelta
from io import StringIO
from uuid import UUID

import pytest
from django.core.management import call_command
from django.utils import timezone

from docurba.core.enums import BaseDocumentType, ProcedureStatusChoices
from docurba.core.management.commands.create_system_events_caduc import DESCRIPTION
from docurba.core.models import Event, EventType, Procedure
from tests.core.factories import EventFactory, EventTypeFactory, ProcedureFactory
from tests.users.factories import ProfileFactory

CADUC_EVENT_NAME = "Caducité"


@pytest.mark.django_db
class TestCreateCaducSystemEvents:
    def _call_command(self, profile_id: str, *, wet_run: bool) -> list[list[str]]:
        out = StringIO()
        call_command(
            "create_system_events_caduc", profile_id, wet_run=wet_run, stdout=out
        )
        return list(csv.reader(StringIO(out.getvalue())))

    def test_caduc_event_listed_then_created_with_wet_run(self) -> None:
        profile_id = str(ProfileFactory().pk)
        caduc_event_type = EventTypeFactory(
            document_type=EventType.DocumentType.PLU,
            name=CADUC_EVENT_NAME,
            impact=ProcedureStatusChoices.CADUC,
            sudocuh_code="SAU",
        )
        now = timezone.now()
        approbation_date = now + timedelta(hours=1)
        event = EventFactory(
            procedure__base_doc_type=BaseDocumentType.POS,
            procedure__status=ProcedureStatusChoices.EN_COURS,
            event_type__impact=ProcedureStatusChoices.APPROUVE,
            date_evenement=now,
        )

        rows = self._call_command(profile_id, wet_run=False)

        expected_row = [
            str(event.procedure.id),
            str(event.procedure.project_id),
            str(approbation_date),
            str(caduc_event_type.id),
            CADUC_EVENT_NAME,
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
            procedure=event.procedure, event_type=caduc_event_type
        )
        assert event.date_evenement == approbation_date
        assert event.type == CADUC_EVENT_NAME
        assert event.code == "SAU"
        assert event.visibility == "private"
        assert event.is_valid is True
        assert event.created_by_id == UUID(profile_id)
        assert event.profile_id == UUID(profile_id)
        assert event.project_id == event.procedure.project_id
        assert event.description == DESCRIPTION

    def test_already_computed_caduc_procedure_not_exported(self) -> None:
        EventTypeFactory(
            document_type=EventType.DocumentType.PLU,
            name=CADUC_EVENT_NAME,
            impact=ProcedureStatusChoices.CADUC,
        )
        EventFactory(
            procedure__base_doc_type=BaseDocumentType.POS,
            procedure__status=ProcedureStatusChoices.EN_COURS,
            event_type__impact=ProcedureStatusChoices.CADUC,
        )

        rows = self._call_command(str(ProfileFactory().pk), wet_run=False)

        assert len(rows) == 1

    def test_procedure_without_impactful_event_not_exported(self) -> None:
        EventTypeFactory(
            document_type=EventType.DocumentType.PLU,
            name=CADUC_EVENT_NAME,
            impact=ProcedureStatusChoices.CADUC,
        )
        ProcedureFactory(
            base_doc_type=BaseDocumentType.POS, status=ProcedureStatusChoices.EN_COURS
        )

        rows = self._call_command(str(ProfileFactory().pk), wet_run=False)

        assert len(rows) == 1

    def test_secondary_procedure_not_exported(self) -> None:
        EventTypeFactory(
            document_type=EventType.DocumentType.PLU,
            name=CADUC_EVENT_NAME,
            impact=ProcedureStatusChoices.CADUC,
        )
        principale = ProcedureFactory(base_doc_type=BaseDocumentType.POS)
        secondaire = ProcedureFactory(with_parente=True, parente=principale)

        Procedure.objects.filter(id=secondaire.id).update(
            status=ProcedureStatusChoices.EN_COURS
        )
        EventFactory(
            procedure=secondaire,
            event_type__impact=ProcedureStatusChoices.APPROUVE,
        )

        rows = self._call_command(str(ProfileFactory().pk), wet_run=False)

        assert len(rows) == 1

    def test_events_without_impact_ignored(self) -> None:
        now = timezone.now()
        EventTypeFactory(
            document_type=EventType.DocumentType.PLU,
            name=CADUC_EVENT_NAME,
            impact=ProcedureStatusChoices.CADUC,
        )
        procedure = ProcedureFactory(
            base_doc_type=BaseDocumentType.POS, status=ProcedureStatusChoices.EN_COURS
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
            name=CADUC_EVENT_NAME,
            impact=ProcedureStatusChoices.CADUC,
        )
        EventFactory(
            procedure__base_doc_type=BaseDocumentType.POS,
            procedure__status=ProcedureStatusChoices.EN_COURS,
            event_type__impact=ProcedureStatusChoices.APPROUVE,
            is_valid=False,
        )
        EventFactory(
            procedure__base_doc_type=BaseDocumentType.POS,
            procedure__status=ProcedureStatusChoices.EN_COURS,
            event_type__impact=ProcedureStatusChoices.CADUC,
            archived=True,
        )

        rows = self._call_command(str(ProfileFactory().pk), wet_run=False)

        assert len(rows) == 1
        assert Event.full_objects.count() == 2

    def test_caduc_event_type_missing_for_document_type_not_exported(self) -> None:
        # The caduc event type is joined on its document type: an SCOT
        # caduc event type cannot fill a PLU procedure.
        EventTypeFactory(
            document_type=EventType.DocumentType.SCOT,
            name=CADUC_EVENT_NAME,
            impact=ProcedureStatusChoices.CADUC,
        )
        EventFactory(
            procedure__base_doc_type=BaseDocumentType.POS,
            procedure__status=ProcedureStatusChoices.EN_COURS,
            event_type__impact=ProcedureStatusChoices.APPROUVE,
        )

        rows = self._call_command(str(ProfileFactory().pk), wet_run=False)

        assert len(rows) == 1

    def test_several_procedures_exported(self) -> None:
        procedures = []
        for base_doc_type, document_type in [
            (BaseDocumentType.SD, EventType.DocumentType.SCOT),
            (BaseDocumentType.POS, EventType.DocumentType.PLU),
        ]:
            EventTypeFactory(
                document_type=document_type,
                name=CADUC_EVENT_NAME,
                impact=ProcedureStatusChoices.CADUC,
            )
            event = EventFactory(
                procedure__base_doc_type=base_doc_type,
                procedure__status=ProcedureStatusChoices.EN_COURS,
                event_type__impact=ProcedureStatusChoices.APPROUVE,
            )
            procedures.append(event.procedure)

        rows = self._call_command(str(ProfileFactory().pk), wet_run=False)

        assert len(rows) == 3
        assert {row[0] for row in rows[1:]} == {str(p.id) for p in procedures}
