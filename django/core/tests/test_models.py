import logging

import pytest
from django.db import models
from pytest_django import DjangoAssertNumQueries

from core.models import (
    EVENT_IMPACT_BY_TYPE_DOCUMENT,
    CommuneProcedure,
    Event,
    EventImpact,
    Procedure,
    TypeDocument,
    TypeDocumentSimplifie,
)


def test_tous_document_types_ont_event_impact() -> None:
    assert list(TypeDocument) == list(EVENT_IMPACT_BY_TYPE_DOCUMENT.keys())


class TestProcedure:
    # @pytest.mark.parametrize(
    #     ("type_document", "type_document_simplifie"),
    #     [
    #         (TypeDocument.SCOT, TypeDocumentSimplifie.SCOT),
    #         (TypeDocument.PLUI, TypeDocumentSimplifie.PLU),
    #         (TypeDocument.PLUIH, TypeDocumentSimplifie.PLU),
    #         (TypeDocument.PLUIHM, TypeDocumentSimplifie.PLU),
    #         (TypeDocument.PLUIM, TypeDocumentSimplifie.PLU),
    #     ],
    # )
    # def test_type_document_simplifie(
    #     self,
    #     type_document: TypeDocument,
    #     type_document_simplifie: TypeDocumentSimplifie,
    # ) -> None:
    #     assert (
    #         Procedure(type_document=type_document).type_document_simplifie
    #         == type_document_simplifie
    #     )

    def test_is_schema(self) -> None:
        assert not Procedure(type_document=TypeDocument.CC).is_schema
        assert not Procedure(type_document=TypeDocument.PLU).is_schema
        assert not Procedure(type_document=TypeDocument.PLUI).is_schema
        assert not Procedure(type_document=TypeDocument.PLUIM).is_schema
        assert not Procedure(type_document=TypeDocument.PLUIH).is_schema
        assert not Procedure(type_document=TypeDocument.PLUIHM).is_schema

        assert Procedure(type_document=TypeDocument.SCOT).is_schema
        assert Procedure(type_document=TypeDocument.SD).is_schema

    @pytest.mark.django_db
    def test_plus_recent_event_prescription(
        self, django_assert_num_queries: DjangoAssertNumQueries
    ) -> None:
        procedure = Procedure.objects.create(type_document=TypeDocument.PLUI)
        procedure.event_set.create(
            type="Délibération de prescription du conseil municipal ou communautaire",
            date_iso="2022-12-01",
        )
        event_prescription = procedure.event_set.create(
            type="Délibération de prescription du conseil municipal ou communautaire",
            date_iso="2024-12-01",
        )
        procedure.event_set.create(
            type="Délibération de prescription du conseil municipal ou communautaire",
            date_iso="2023-12-01",
        )

        assert event_prescription.impact == EventImpact.EN_COURS
        with django_assert_num_queries(1):
            procedure_with_events = Procedure.objects.with_events().get(id=procedure.id)

            assert procedure_with_events.date_prescription == "2024-12-01"

    @pytest.mark.django_db
    def test_event_prescription_uniquement(
        self, django_assert_num_queries: DjangoAssertNumQueries
    ) -> None:
        procedure = Procedure.objects.create(type_document=TypeDocument.PLUI)
        procedure.event_set.create(
            type="Caractère exécutoire",
            date_iso="2025-12-01",
        )
        event_prescription = procedure.event_set.create(
            type="Délibération de prescription du conseil municipal ou communautaire",
            date_iso="2024-12-01",
        )
        procedure.event_set.create(
            type="Caractère exécutoire",
            date_iso="2025-12-01",
        )

        assert event_prescription.impact == EventImpact.EN_COURS
        with django_assert_num_queries(1):
            procedure_with_events = Procedure.objects.with_events().get(id=procedure.id)

            assert procedure_with_events.date_prescription == "2024-12-01"

    @pytest.mark.django_db
    def test_event_prescription_manquant(
        self, django_assert_num_queries: DjangoAssertNumQueries
    ) -> None:
        procedure = Procedure.objects.create(type_document=TypeDocument.PLUI)

        with django_assert_num_queries(1):
            procedure_with_events = Procedure.objects.with_events().get(id=procedure.id)

            assert procedure_with_events.date_prescription == "0000-00-00"


class TestProcedureStatut:
    @pytest.mark.django_db
    def test_principale_opposable(
        self, django_assert_num_queries: DjangoAssertNumQueries
    ) -> None:
        procedure = Procedure.objects.create(
            is_principale=True, type_document=TypeDocument.PLUI
        )
        event = procedure.event_set.create(type="Caractère exécutoire")

        assert event.impact == EventImpact.OPPOSABLE
        with django_assert_num_queries(1):
            procedure_with_events = Procedure.objects.with_events().get(id=procedure.id)

            assert procedure_with_events.statut == EventImpact.OPPOSABLE

    @pytest.mark.django_db
    def test_principale_sans_evenement(
        self, django_assert_num_queries: DjangoAssertNumQueries
    ) -> None:
        procedure = Procedure.objects.create(
            is_principale=True, type_document=TypeDocument.PLUI
        )
        Event.objects.create(procedure=procedure)

        with django_assert_num_queries(1):
            procedure_with_events = Procedure.objects.with_events().get(id=procedure.id)

            assert not procedure_with_events.statut

    @pytest.mark.django_db
    def test_principale_annule(
        self, django_assert_num_queries: DjangoAssertNumQueries
    ) -> None:
        procedure = Procedure.objects.create(
            is_principale=True, type_document=TypeDocument.PLUI
        )
        event = procedure.event_set.create(type="Abrogation")

        assert event.impact == EventImpact.ANNULE
        with django_assert_num_queries(1):
            procedure_with_events = Procedure.objects.with_events().get(id=procedure.id)

            assert procedure_with_events.statut == EventImpact.ANNULE

    @pytest.mark.django_db
    def test_principale_ignore_event_invalide(
        self, django_assert_num_queries: DjangoAssertNumQueries
    ) -> None:
        procedure = Procedure.objects.create(
            is_principale=True, type_document=TypeDocument.PLUI
        )
        event = procedure.event_set.create(type="Caractère exécutoire", is_valid=False)

        assert event.impact is None
        with django_assert_num_queries(1):
            procedure_with_events = Procedure.objects.with_events().get(id=procedure.id)

            assert not procedure_with_events.statut

    @pytest.mark.django_db
    def test_principale_carte_communale_deliberation_d_approbation_pas_opposable(
        self, django_assert_num_queries: DjangoAssertNumQueries
    ) -> None:
        procedure = Procedure.objects.create(
            is_principale=True, type_document=TypeDocument.CC
        )
        event = procedure.event_set.create(type="Délibération d'approbation")

        assert event.impact is None
        with django_assert_num_queries(1):
            procedure_with_events = Procedure.objects.with_events().get(id=procedure.id)

            assert not procedure_with_events.statut

    @pytest.mark.django_db
    def test_secondaire_non_opposable(
        self, django_assert_num_queries: DjangoAssertNumQueries
    ) -> None:
        procedure_secondaire = Procedure.objects.create(
            is_principale=False, type_document=TypeDocument.PLUI
        )
        procedure_secondaire.event_set.create(type="Caractère exécutoire")

        with django_assert_num_queries(0):
            assert not procedure_secondaire.statut


class TestEvent:
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
            ("CC", "Délibération d'approbation", None),
        ],
    )
    def test_event_impact(
        self, type_document: str, type_event: str, impact: EventImpact
    ) -> None:
        procedure = Procedure(type_document=type_document)
        assert Event(procedure=procedure, type=type_event).impact == impact


class TestCommuneProcedure:
    @pytest.mark.django_db
    def test_plus_recente_opposable(
        self, django_assert_num_queries: DjangoAssertNumQueries
    ) -> None:
        procedure_opposable = Procedure.objects.create(
            is_principale=True, type_document=TypeDocument.PLUI
        )
        procedure_opposable.event_set.create(
            type="Délibération de prescription du conseil municipal ou communautaire",
            date_iso="2024-12-01",
        )
        procedure_opposable.event_set.create(type="Caractère exécutoire")
        commune_procedure_opposable = procedure_opposable.perimetre.create(
            collectivite_code="12345", departement="12"
        )

        procedure_precedente = Procedure.objects.create(
            is_principale=True, type_document=TypeDocument.PLU
        )
        procedure_precedente.event_set.create(
            type="Délibération de prescription du conseil municipal ou communautaire",
            date_iso="2023-12-01",
        )
        procedure_precedente.event_set.create(
            type="Caractère exécutoire",
        )
        commune_procedure_precedente = procedure_precedente.perimetre.create(
            collectivite_code="12345", departement="12"
        )

        with django_assert_num_queries(1):
            procedures = Procedure.objects.with_events()

            assert all(
                procedure.statut == EventImpact.OPPOSABLE for procedure in procedures
            )

        with django_assert_num_queries(2):
            perimetres = CommuneProcedure.objects.departement("12")
        with django_assert_num_queries(0):
            assert perimetres == [
                commune_procedure_opposable,
                commune_procedure_precedente,
            ]
            assert perimetres[0].opposable
            assert not perimetres[1].opposable

    @pytest.mark.django_db
    def test_plans_et_schemas_opposable(
        self, django_assert_num_queries: DjangoAssertNumQueries
    ) -> None:
        plan_opposable = Procedure.objects.create(
            is_principale=True, type_document=TypeDocument.PLUI
        )
        plan_opposable.event_set.create(
            type="Délibération de prescription du conseil municipal ou communautaire",
            date_iso="2024-12-01",
        )
        plan_opposable.event_set.create(type="Caractère exécutoire")
        commune_plan_opposable = plan_opposable.perimetre.create(
            collectivite_code="12345", departement="12"
        )

        schema_opposable = Procedure.objects.create(
            is_principale=True, type_document=TypeDocument.SCOT
        )
        schema_opposable.event_set.create(
            type="Délibération de prescription du conseil municipal ou communautaire",
            date_iso="2023-12-01",
        )
        schema_opposable.event_set.create(
            type="Caractère exécutoire",
        )
        commune_schema_opposable = schema_opposable.perimetre.create(
            collectivite_code="12345", departement="12"
        )

        with django_assert_num_queries(1):
            procedures = Procedure.objects.with_events()

            assert all(
                procedure.statut == EventImpact.OPPOSABLE for procedure in procedures
            )

        with django_assert_num_queries(2):
            perimetres = CommuneProcedure.objects.departement("12")
        with django_assert_num_queries(0):
            assert perimetres == [
                commune_plan_opposable,
                commune_schema_opposable,
            ]
            assert perimetres[0].opposable
            assert perimetres[1].opposable

    @pytest.mark.django_db
    def test_opposable_sans_prescription(
        self, django_assert_num_queries: DjangoAssertNumQueries
    ) -> None:
        procedure_opposable = Procedure.objects.create(
            is_principale=True, type_document=TypeDocument.PLUI
        )
        procedure_opposable.event_set.create(type="Caractère exécutoire")
        commune_procedure_opposable = procedure_opposable.perimetre.create(
            collectivite_code="12345", departement="12"
        )

        with django_assert_num_queries(1):
            procedure_opposable_with_events = Procedure.objects.with_events().get(
                id=procedure_opposable.id
            )

            assert procedure_opposable_with_events.statut == EventImpact.OPPOSABLE

        with django_assert_num_queries(2):
            perimetres = CommuneProcedure.objects.departement("12")
        with django_assert_num_queries(0):
            assert perimetres == [commune_procedure_opposable]
            assert perimetres[0].opposable

    @pytest.mark.django_db
    def test_aucune_opposable(
        self, django_assert_num_queries: DjangoAssertNumQueries
    ) -> None:
        procedure_en_cours = Procedure.objects.create(
            is_principale=True, type_document=TypeDocument.PLUI
        )
        procedure_en_cours.event_set.create(
            type="Délibération de prescription du conseil municipal ou communautaire",
            date_iso="2024-12-01",
        )

        commune_procedure_en_cours = procedure_en_cours.perimetre.create(
            collectivite_code="12345", departement="12"
        )

        with django_assert_num_queries(1):
            procedure_en_cours_with_events = Procedure.objects.with_events().get(
                id=procedure_en_cours.id
            )

            assert procedure_en_cours_with_events.statut == EventImpact.EN_COURS

        with django_assert_num_queries(2):
            perimetres = CommuneProcedure.objects.departement("12")
        with django_assert_num_queries(0):
            assert perimetres == [commune_procedure_en_cours]
            assert not perimetres[0].opposable

    @pytest.mark.django_db
    def test_abrogation_non_opposable(
        self, django_assert_num_queries: DjangoAssertNumQueries
    ) -> None:
        procedure_opposable = Procedure.objects.create(
            is_principale=True, type_document=TypeDocument.PLUI, type="Abrogation"
        )
        procedure_opposable.event_set.create(type="Caractère exécutoire")
        commune_procedure_opposable = procedure_opposable.perimetre.create(
            collectivite_code="12345", departement="12"
        )

        with django_assert_num_queries(1):
            procedure_opposable_with_events = Procedure.objects.with_events().get(
                id=procedure_opposable.id
            )

            assert procedure_opposable_with_events.statut == EventImpact.OPPOSABLE

        with django_assert_num_queries(2):
            perimetres = CommuneProcedure.objects.departement("12")
        with django_assert_num_queries(0):
            assert perimetres == [commune_procedure_opposable]
            assert not perimetres[0].opposable
