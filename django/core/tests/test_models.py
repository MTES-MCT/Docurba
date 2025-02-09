import pytest

from core.models import (
    CommuneProcedure,
    Event,
    EventImpact,
    Procedure,
    TypeDocument,
    TypeDocumentSimplifie,
)


class TestProcedure:
    @pytest.mark.parametrize(
        ("type_document", "type_document_simplifie"),
        [
            (TypeDocument.SCOT, TypeDocumentSimplifie.SCOT),
            (TypeDocument.PLUI, TypeDocumentSimplifie.PLU),
            (TypeDocument.PLUIH, TypeDocumentSimplifie.PLU),
            (TypeDocument.PLUIHM, TypeDocumentSimplifie.PLU),
            (TypeDocument.PLUIM, TypeDocumentSimplifie.PLU),
        ],
    )
    def test_type_document_simplifie(
        self,
        type_document: TypeDocument,
        type_document_simplifie: TypeDocumentSimplifie,
    ) -> None:
        assert (
            Procedure(type_document=type_document).type_document_simplifie
            == type_document_simplifie
        )


@pytest.mark.parametrize(
    ("type_document", "type_event", "impact"),
    [
        ("PLU", "lol", None),
        (
            "PLU",
            "Délibération de prescription du conseil municipal ou communautaire",
            "en cours",
        ),
        (
            "PLUi",
            "Délibération de prescription du conseil municipal ou communautaire",
            "en cours",
        ),
    ],
)
def test_event_impact(type_document: str, type_event: str, impact: EventImpact) -> None:
    procedure = Procedure(type_document=type_document)
    assert Event(procedure=procedure, type=type_event).impact == impact


@pytest.mark.django_db
def test_non_opposable() -> None:
    assert CommuneProcedure.objects.count() == 0

    procedure = Procedure.objects.create(type_document=TypeDocument.PLUI)
    procedure.event_set.create()

    assert not procedure.opposable


@pytest.mark.django_db
def test_opposable() -> None:
    assert CommuneProcedure.objects.count() == 0

    procedure = Procedure.objects.create(type_document=TypeDocument.PLUI)
    event = procedure.event_set.create(type="Caractère exécutoire")

    assert event.impact == EventImpact.OPPOSABLE
    assert procedure.opposable
