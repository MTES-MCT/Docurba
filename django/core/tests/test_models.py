import logging

import pytest
from pytest_django import DjangoAssertNumQueries

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
        with django_assert_num_queries(2):
            procedure_with_events = Procedure.objects.prefetch_related("event_set").get(
                id=procedure.id
            )

        with django_assert_num_queries(0):
            assert procedure_with_events.event_prescription == event_prescription

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
        with django_assert_num_queries(2):
            procedure_with_events = Procedure.objects.prefetch_related("event_set").get(
                id=procedure.id
            )

        with django_assert_num_queries(0):
            assert procedure_with_events.event_prescription == event_prescription

    @pytest.mark.django_db
    def test_event_prescription_manquant(self) -> None:
        procedure = Procedure(type_document=TypeDocument.PLUI)
        assert procedure.event_prescription is None


class TestProcedureStatut:
    # FIXME More tests…
    @pytest.mark.django_db
    def test_principale_opposable(
        self, django_assert_num_queries: DjangoAssertNumQueries
    ) -> None:
        procedure = Procedure.objects.create(
            is_principale=True, type_document=TypeDocument.PLUI
        )
        event = procedure.event_set.create(type="Caractère exécutoire")

        assert event.impact == EventImpact.OPPOSABLE
        with django_assert_num_queries(2):
            procedure_with_events = Procedure.objects.prefetch_related("event_set").get(
                id=procedure.id
            )
        with django_assert_num_queries(0):
            assert procedure_with_events.statut == EventImpact.OPPOSABLE

    @pytest.mark.django_db
    def test_principale_sans_evenement(
        self, django_assert_num_queries: DjangoAssertNumQueries
    ) -> None:
        procedure = Procedure.objects.create(
            is_principale=True, type_document=TypeDocument.PLUI
        )
        Event.objects.create(procedure=procedure)

        with django_assert_num_queries(2):
            procedure_with_events = Procedure.objects.prefetch_related("event_set").get(
                id=procedure.id
            )
        with django_assert_num_queries(0):
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
        with django_assert_num_queries(2):
            procedure_with_events = Procedure.objects.prefetch_related("event_set").get(
                id=procedure.id
            )
        with django_assert_num_queries(0):
            assert procedure_with_events.statut == EventImpact.ANNULE

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
            collectivite_code="12345"
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
            collectivite_code="12345"
        )

        with django_assert_num_queries(2):
            procedure_opposable_with_events = Procedure.objects.prefetch_related(
                "event_set"
            ).get(id=procedure_opposable.id)
        with django_assert_num_queries(0):
            assert procedure_opposable_with_events.statut == EventImpact.OPPOSABLE

        with django_assert_num_queries(3):
            commune_procedure_opposable_with_events = (
                CommuneProcedure.objects.prefetch_related("procedure__event_set").get(
                    id=commune_procedure_opposable.id
                )
            )
        with django_assert_num_queries(2):
            assert commune_procedure_opposable_with_events.opposable

        with django_assert_num_queries(2):
            procedure_precedente_with_events = Procedure.objects.prefetch_related(
                "event_set"
            ).get(id=procedure_precedente.id)
        with django_assert_num_queries(0):
            assert procedure_precedente_with_events.statut == EventImpact.OPPOSABLE

        with django_assert_num_queries(3):
            commune_procedure_precedente_with_events = (
                CommuneProcedure.objects.prefetch_related("procedure__event_set").get(
                    id=commune_procedure_precedente.id
                )
            )
        with django_assert_num_queries(2):
            assert not commune_procedure_precedente_with_events.opposable

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
            collectivite_code="12345"
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
            collectivite_code="12345"
        )

        with django_assert_num_queries(2):
            plan_opposable_with_events = Procedure.objects.prefetch_related(
                "event_set"
            ).get(id=plan_opposable.id)
        with django_assert_num_queries(0):
            assert plan_opposable_with_events.statut == EventImpact.OPPOSABLE

        with django_assert_num_queries(3):
            commune_plan_opposable_with_events = (
                CommuneProcedure.objects.prefetch_related("procedure__event_set").get(
                    id=commune_plan_opposable.id
                )
            )
        with django_assert_num_queries(2):
            assert commune_plan_opposable_with_events.opposable

        with django_assert_num_queries(2):
            schema_opposable_with_events = Procedure.objects.prefetch_related(
                "event_set"
            ).get(id=schema_opposable.id)
        with django_assert_num_queries(0):
            assert schema_opposable_with_events.statut == EventImpact.OPPOSABLE

        with django_assert_num_queries(3):
            commune_schema_opposable_with_events = (
                CommuneProcedure.objects.prefetch_related("procedure__event_set").get(
                    id=commune_schema_opposable.id
                )
            )
        with django_assert_num_queries(2):
            assert commune_schema_opposable_with_events.opposable

    @pytest.mark.django_db
    def test_opposable_sans_prescription(
        self, django_assert_num_queries: DjangoAssertNumQueries
    ) -> None:
        procedure_opposable = Procedure.objects.create(
            is_principale=True, type_document=TypeDocument.PLUI
        )
        procedure_opposable.event_set.create(type="Caractère exécutoire")
        commune_procedure_opposable = procedure_opposable.perimetre.create(
            collectivite_code="12345"
        )

        with django_assert_num_queries(2):
            procedure_opposable_with_events = Procedure.objects.prefetch_related(
                "event_set"
            ).get(id=procedure_opposable.id)
        with django_assert_num_queries(0):
            assert procedure_opposable_with_events.statut == EventImpact.OPPOSABLE

        with django_assert_num_queries(3):
            commune_procedure_opposable_with_events = (
                CommuneProcedure.objects.prefetch_related("procedure__event_set").get(
                    id=commune_procedure_opposable.id
                )
            )
        with django_assert_num_queries(2):
            assert commune_procedure_opposable_with_events.opposable

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
            collectivite_code="12345"
        )

        with django_assert_num_queries(2):
            procedure_en_cours_with_events = Procedure.objects.prefetch_related(
                "event_set"
            ).get(id=procedure_en_cours.id)
        with django_assert_num_queries(0):
            assert procedure_en_cours_with_events.statut == EventImpact.EN_COURS

        with django_assert_num_queries(3):
            commune_procedure_en_cours_with_events = (
                CommuneProcedure.objects.prefetch_related("procedure__event_set").get(
                    id=commune_procedure_en_cours.id
                )
            )
        with django_assert_num_queries(2):
            assert not commune_procedure_en_cours_with_events.opposable
