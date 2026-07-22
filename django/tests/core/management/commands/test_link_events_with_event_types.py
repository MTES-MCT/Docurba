import pytest
from django.core.management import call_command

from docurba.core.models import Event, EventType, TypeDocument
from docurba.users.models import SupabaseUser
from tests.core.factories import EventFactory, EventTypeFactory

MAPPINGS = [
    (
        "PLU",
        "Débat sur le PADD en conseil municipal",
        "Débat sur le PADD en conseil municipal ou communautaire",
    ),
    ("PLU", "Avis de l'Etat", "Réception de l'avis de l'État"),
    ("CC", "Caractère éxécutoire", "Caractère exécutoire"),
    (
        "PLU",
        "Dérogation au principe d'urbanisation limitée -> consultation CDPENAF\n(délai 3 mois) et saisine Préfet pour avis (4 mois)",
        "Dérogation au principe d'urbanisation limitée -> consultation CDPENAF\n(délai 2 mois) et saisine Préfet pour avis (4 mois)",
    ),
    ("PLU", "Avis des services de l'Etat", "Réception de l'avis de l'État"),
    ("PLU", "Avis des services de l'État", "Réception de l'avis de l'État"),
    (
        "CC",
        "Abrogation : arrêté préfectoral",
        "Arrêté préfectoral d'abrogation de la carte communale",
    ),
    ("PLU", "Avis CDPENAF", "Réception de l'avis de la CDPENAF"),
    (
        "CC",
        "Abrogation : délibération communautaire",
        "Délibération communal ou communautaire d’abrogation de la carte communale",  # noqa: RUF001
    ),
    ("PLU", "Avis Etat", "Réception de l'avis de l'État"),
    ("PLU", "Bilan de la concertation", "Délibération de bilan de la concertation"),
    ("PLU", "Avis de la DDT", "Réception de l'avis de l'État"),
]


@pytest.fixture
def clear_data() -> None:
    call_command(
        "flush",
        verbosity=0,
        interactive=False,
        reset_sequences=False,
        allow_cascade=True,
        inhibit_post_migrate=True,
    )
    SupabaseUser.objects.all().delete()  # Why flush dont truncate user table ?


def _event_types_args(mapping: tuple) -> tuple:
    document_type, _, event_type = mapping
    return (document_type, event_type)


@pytest.mark.django_db(transaction=True)
class TestLinkEventsWithEventTypes:
    @pytest.mark.parametrize(
        (
            "procedure_doc_type",
            "et_document_type",
        ),
        [
            pytest.param(TypeDocument.CC, EventType.DocumentType.CC),
            pytest.param(TypeDocument.SCOT, EventType.DocumentType.SCOT),
            pytest.param(TypeDocument.SD, EventType.DocumentType.SCOT),
            pytest.param(TypeDocument.PLU, EventType.DocumentType.PLU),
            pytest.param(TypeDocument.PLUI, EventType.DocumentType.PLU),
            pytest.param(TypeDocument.PLUIH, EventType.DocumentType.PLU),
            pytest.param(TypeDocument.PLUIHM, EventType.DocumentType.PLU),
            pytest.param(TypeDocument.PLUIM, EventType.DocumentType.PLU),
            pytest.param(TypeDocument.POS, EventType.DocumentType.PLU),
        ],
    )
    @pytest.mark.parametrize(
        (
            "e_name",
            "e_code",
            "et_name",
            "et_sudocuh_name",
            "et_sudocuh_code",
        ),
        [
            pytest.param(
                "Name 1",
                "CODE 1",
                "Name 1",
                "Name 1",
                "CODE 1",
                id="link_by_all",
            ),
            pytest.param(
                "Name 1",
                "CODE 1",
                "Name 1",
                "Sudocuh Name 1",
                "SUDOCUH CODE 1",
                id="link_by_name",
            ),
            pytest.param(
                "Name 1",
                "",
                "Name 1",
                "",
                "",
                id="link_by_name_only",
            ),
            pytest.param(
                "",
                "CODE 1",
                "Name 1",
                "",
                "CODE 1",
                id="link_by_code_only",
            ),
            pytest.param(
                "Sudocuh Name 1",
                "CODE 1",
                "Name 1",
                "Sudocuh Name 1",
                "SUDOCUH CODE 1",
                id="link_by_sudocuh_name",
            ),
            pytest.param(
                "Name 1",
                "CODE 1",
                "Name 2",
                "Sudocuh Name 1",
                "CODE 1",
                id="link_by_sudocuh_code",
            ),
        ],
    )
    def test_call_command_link(
        self,
        clear_data,  # noqa: ANN001, ARG002
        procedure_doc_type: TypeDocument,
        et_document_type: EventType.DocumentType,
        e_name: str,
        e_code: str,
        et_name: str,
        et_sudocuh_name: str,
        et_sudocuh_code: str,
    ) -> None:

        event_type = EventTypeFactory(
            document_type=et_document_type,
            name=et_name,
            sudocuh_name=et_sudocuh_name,
            sudocuh_code=et_sudocuh_code,
        )

        event = EventFactory(
            procedure__doc_type=procedure_doc_type, type=e_name, code=e_code
        )

        call_command("link_events_with_event_types")

        event.refresh_from_db()

        assert event.event_type_id == event_type.id
        snapshots = list(event.snapshots.all())
        assert len(snapshots) == 2
        assert snapshots[0].pgh_label == "insert"
        assert snapshots[0].event_type_id is None
        assert snapshots[1].pgh_label == "update"
        assert snapshots[1].event_type_id == event_type.id

    @pytest.mark.parametrize(
        (
            "procedure_doc_type",
            "et_document_type",
        ),
        [
            pytest.param(TypeDocument.CC, EventType.DocumentType.CC),
            pytest.param(TypeDocument.SCOT, EventType.DocumentType.SCOT),
            pytest.param(TypeDocument.SD, EventType.DocumentType.SCOT),
            pytest.param(TypeDocument.PLU, EventType.DocumentType.PLU),
            pytest.param(TypeDocument.PLUI, EventType.DocumentType.PLU),
        ],
    )
    @pytest.mark.parametrize(
        (
            "e_name",
            "e_code",
            "et_name",
            "et_sudocuh_name",
            "et_sudocuh_code",
        ),
        [
            pytest.param(
                "Name 1",
                "CODE 1",
                "Name 2",
                "Sudocuh Name 2",
                "CODE 2",
                id="no_link",
            ),
            pytest.param(
                "Name 1",
                "",
                "Name 2",
                "",
                "",
                id="no_link_empty",
            ),
            pytest.param(
                "",
                "CODE 1",
                "Name 1",
                "Sudocuh Name 1",
                "CODE 2",
                id="no_link_empty_type",
            ),
            pytest.param(
                "Name 1",
                "",
                "Name 2",
                "Sudocuh Name 1",
                "CODE 1",
                id="no_link_empty_code",
            ),
            pytest.param(
                "Name 1",
                "AUTRE",
                "Name 2",
                "Sudocuh Name 1",
                "AUTRE",
                id="no_link_AUTRE",
            ),
            pytest.param(
                "Name 1",
                "AVISETAT",
                "Name 2",
                "Sudocuh Name 1",
                "AVISETAT",
                id="no_link_AVISETAT",
            ),
        ],
    )
    def test_call_command_no_link(
        self,
        clear_data,  # noqa: ANN001, ARG002
        procedure_doc_type: TypeDocument,
        et_document_type: EventType.DocumentType,
        e_name: str,
        e_code: str,
        et_name: str,
        et_sudocuh_name: str,
        et_sudocuh_code: str,
    ) -> None:

        EventTypeFactory(
            document_type=et_document_type,
            name=et_name,
            sudocuh_name=et_sudocuh_name,
            sudocuh_code=et_sudocuh_code,
        )

        event = EventFactory(
            procedure__doc_type=procedure_doc_type, type=e_name, code=e_code
        )

        call_command("link_events_with_event_types")

        event.refresh_from_db()

        assert event.event_type_id is None
        snapshots = list(event.snapshots.all())
        assert len(snapshots) == 1
        assert snapshots[0].pgh_label == "insert"
        assert snapshots[0].event_type_id is None

    @pytest.mark.parametrize(
        (
            "procedure_doc_type",
            "et_document_type",
        ),
        [
            pytest.param(TypeDocument.CC, EventType.DocumentType.SCOT),
            pytest.param(TypeDocument.CC, EventType.DocumentType.PLU),
            pytest.param(TypeDocument.PLU, EventType.DocumentType.CC),
            pytest.param(TypeDocument.PLU, EventType.DocumentType.SCOT),
            pytest.param(TypeDocument.SCOT, EventType.DocumentType.PLU),
            pytest.param(TypeDocument.SCOT, EventType.DocumentType.CC),
            pytest.param(TypeDocument.SD, EventType.DocumentType.PLU),
            pytest.param(TypeDocument.PLUI, EventType.DocumentType.SCOT),
        ],
    )
    def test_call_command_no_link_procedure_unmatch(
        self,
        clear_data,  # noqa: ANN001, ARG002
        procedure_doc_type: TypeDocument,
        et_document_type: EventType.DocumentType,
    ) -> None:

        EventTypeFactory(
            document_type=et_document_type,
            name="Name 1",
            sudocuh_name="Name 1",
            sudocuh_code="CODE 1",
        )

        event = EventFactory(
            procedure__doc_type=procedure_doc_type, type="Name 1", code="CODE 1"
        )

        call_command("link_events_with_event_types")

        event.refresh_from_db()

        assert event.event_type_id is None
        snapshots = list(event.snapshots.all())
        assert len(snapshots) == 1
        assert snapshots[0].pgh_label == "insert"
        assert snapshots[0].event_type_id is None

    def test_call_command_only_mappings(
        self,
        clear_data,  # noqa: ANN001, ARG002
    ) -> None:

        for document_type, event_type in set(map(_event_types_args, MAPPINGS)):
            EventTypeFactory(document_type=document_type, name=event_type, impact="")

        for _, event_name, _ in MAPPINGS:
            for document_type in EventType.DocumentType:
                EventFactory(procedure__doc_type=document_type, type=event_name)

        call_command("link_events_with_event_types")

        assert Event.full_objects.filter(event_type__isnull=True).count() == len(
            MAPPINGS
        ) * (len(EventType.DocumentType) - 1)

        queryset = (
            Event.full_objects.select_related("procedure", "event_type")
            .prefetch_related("snapshots")
            .filter(event_type__isnull=False)
        )
        assert queryset.count() == len(MAPPINGS)
        for document_type, event_name, event_type in MAPPINGS:
            event = next(
                filter(
                    lambda i: (
                        i.procedure.doc_type == document_type
                        and i.type == event_name
                        and i.event_type.name == event_type
                    ),
                    queryset,
                ),
                None,
            )
            assert event
            snapshots = list(event.snapshots.all())
            assert len(snapshots) == 2
            assert snapshots[0].pgh_label == "insert"
            assert snapshots[0].event_type_id is None
            assert snapshots[1].pgh_label == "update"
            assert snapshots[1].event_type_id == event.event_type.id
