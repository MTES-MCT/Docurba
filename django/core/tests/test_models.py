from datetime import date

import pytest
from pytest_django import DjangoAssertNumQueries

from core.models import (
    EVENT_IMPACT_BY_TYPE_DOCUMENT,
    Commune,
    Event,
    EventImpact,
    Procedure,
    Region,
    TypeDocument,
)


def create_commune() -> Commune:
    region = Region.objects.create()
    departement = region.departements.create()
    return Commune.objects.create(
        id="12345_COM",
        code_insee="12345",
        type="COM",
        departement=departement,
        competence_plan=False,
        competence_schema=False,
    )


def test_tous_document_types_ont_event_impact() -> None:
    assert list(TypeDocument) == list(EVENT_IMPACT_BY_TYPE_DOCUMENT.keys())


class TestProcedure:
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
    def test_date_approbation_retourne_plus_recent_event_approbation(
        self, django_assert_num_queries: DjangoAssertNumQueries
    ) -> None:
        commune = create_commune()
        procedure = Procedure.objects.create(
            type_document=TypeDocument.PLUI,
            collectivite_porteuse=commune,
        )
        procedure.event_set.create(
            type="Caractère exécutoire",
            date_evenement_string="2022-12-01",
        )
        procedure.event_set.create(
            type="Délibération d'approbation du municipal ou communautaire",
            date_evenement_string="2024-12-01",
        )
        procedure.event_set.create(
            type="Délibération d'approbation",
            date_evenement_string="2023-12-01",
        )

        assert [event.impact for event in procedure.event_set.all()] == [
            EventImpact.APPROUVE,
            EventImpact.APPROUVE,
            EventImpact.APPROUVE,
        ]
        with django_assert_num_queries(1):
            procedure_with_events = Procedure.objects.with_events().get(id=procedure.id)

            assert procedure_with_events.date_approbation == "2024-12-01"

    @pytest.mark.django_db
    def test_date_approbation_ignore_event_pas_approbation(
        self, django_assert_num_queries: DjangoAssertNumQueries
    ) -> None:
        commune = create_commune()
        procedure = Procedure.objects.create(
            type_document=TypeDocument.PLUI, collectivite_porteuse=commune
        )
        procedure.event_set.create(
            type="Délibération de prescription du conseil municipal ou communautaire",
            date_evenement_string="2023-12-01",
        )
        procedure.event_set.create(
            type="Caractère exécutoire",
            date_evenement_string="2024-12-01",
        )
        procedure.event_set.create(
            type="Délibération de prescription du conseil municipal ou communautaire",
            date_evenement_string="2025-12-01",
        )

        assert [event.impact for event in procedure.event_set.all()] == [
            EventImpact.EN_COURS,
            EventImpact.APPROUVE,
            EventImpact.EN_COURS,
        ]
        with django_assert_num_queries(1):
            procedure_with_events = Procedure.objects.with_events().get(id=procedure.id)

            assert procedure_with_events.date_approbation == "2024-12-01"

    @pytest.mark.django_db
    def test_date_approbation_quand_event_approbation_manquant(
        self, django_assert_num_queries: DjangoAssertNumQueries
    ) -> None:
        commune = create_commune()
        procedure = Procedure.objects.create(
            type_document=TypeDocument.PLUI, collectivite_porteuse=commune
        )

        with django_assert_num_queries(1):
            procedure_with_events = Procedure.objects.with_events().get(id=procedure.id)

            assert procedure_with_events.date_approbation == "0000-00-00"

    @pytest.mark.django_db
    def test_date_approbation_ignore_event_apres(
        self, django_assert_num_queries: DjangoAssertNumQueries
    ) -> None:
        commune = create_commune()
        procedure = Procedure.objects.create(
            type_document=TypeDocument.PLUI, collectivite_porteuse=commune
        )
        procedure.event_set.create(
            type="Caractère exécutoire",
            date_evenement_string="2022-12-01",
        )
        procedure.event_set.create(
            type="Délibération d'approbation",
            date_evenement_string="2023-12-01",
        )

        assert [event.impact for event in procedure.event_set.all()] == [
            EventImpact.APPROUVE,
            EventImpact.APPROUVE,
        ]
        with django_assert_num_queries(1):
            procedure_with_events = Procedure.objects.with_events(
                avant=date(2023, 12, 1)
            ).get(id=procedure.id)

            assert procedure_with_events.date_approbation == "2022-12-01"


class TestProcedureStatut:
    @pytest.mark.django_db
    def test_principale_opposable(
        self, django_assert_num_queries: DjangoAssertNumQueries
    ) -> None:
        commune = create_commune()
        procedure = Procedure.objects.create(
            type_document=TypeDocument.PLUI, collectivite_porteuse=commune
        )
        event = procedure.event_set.create(type="Caractère exécutoire")

        assert event.impact == EventImpact.APPROUVE
        with django_assert_num_queries(1):
            procedure_with_events = Procedure.objects.with_events().get(id=procedure.id)

            assert procedure_with_events.statut == EventImpact.APPROUVE

    @pytest.mark.django_db
    @pytest.mark.parametrize(
        ("jour_limite", "impact"),
        [
            (3, None),
            (4, EventImpact.EN_COURS),
            (5, EventImpact.EN_COURS),
            (6, EventImpact.APPROUVE),
        ],
    )
    def test_ignore_event_apres(
        self,
        django_assert_num_queries: DjangoAssertNumQueries,
        jour_limite: int,
        impact: EventImpact,
    ) -> None:
        commune = create_commune()
        procedure = Procedure.objects.create(
            type_document=TypeDocument.PLUI, collectivite_porteuse=commune
        )
        event_prescription = procedure.event_set.create(
            type="Délibération de prescription du conseil municipal ou communautaire",
            date_evenement_string="2024-12-03",
        )
        event_approbation = procedure.event_set.create(
            type="Caractère exécutoire", date_evenement_string="2024-12-05"
        )

        assert event_prescription.impact == EventImpact.EN_COURS
        assert event_approbation.impact == EventImpact.APPROUVE
        with django_assert_num_queries(1):
            procedure_with_events = Procedure.objects.with_events(
                avant=date(2024, 12, jour_limite)
            ).get(id=procedure.id)

            assert procedure_with_events.statut == impact

    @pytest.mark.django_db
    def test_principale_sans_evenement(
        self, django_assert_num_queries: DjangoAssertNumQueries
    ) -> None:
        commune = create_commune()
        procedure = Procedure.objects.create(
            type_document=TypeDocument.PLUI, collectivite_porteuse=commune
        )
        Event.objects.create(procedure=procedure)

        with django_assert_num_queries(1):
            procedure_with_events = Procedure.objects.with_events().get(id=procedure.id)

            assert not procedure_with_events.statut

    @pytest.mark.django_db
    def test_principale_annule(
        self, django_assert_num_queries: DjangoAssertNumQueries
    ) -> None:
        commune = create_commune()
        procedure = Procedure.objects.create(
            type_document=TypeDocument.PLUI, collectivite_porteuse=commune
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
        commune = create_commune()
        procedure = Procedure.objects.create(
            type_document=TypeDocument.PLUI, collectivite_porteuse=commune
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
        commune = create_commune()
        procedure = Procedure.objects.create(
            type_document=TypeDocument.CC, collectivite_porteuse=commune
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
        commune = create_commune()
        procedure_principale = Procedure.objects.create(
            type_document=TypeDocument.PLUI, collectivite_porteuse=commune
        )
        procedure_secondaire = Procedure.objects.create(
            parente=procedure_principale,
            type_document=TypeDocument.PLUI,
            collectivite_porteuse=commune,
        )
        procedure_secondaire.event_set.create(type="Caractère exécutoire")

        with django_assert_num_queries(1):
            procedure_with_events = Procedure.objects.with_events().get(
                id=procedure_secondaire.id
            )
            assert not procedure_with_events.statut


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


class TestCollectivite:
    # test récupérer toutes les communes d'un EPCI
    pass


class TestCommuneProceduresPrincipales:
    @pytest.mark.django_db
    def test_exclut_secondaires(
        self, django_assert_num_queries: DjangoAssertNumQueries
    ) -> None:
        commune = create_commune()

        procedure_principale = commune.procedures.create(
            type_document=TypeDocument.PLUI, collectivite_porteuse=commune
        )
        _procedure_secondaire = commune.procedures.create(
            parente=procedure_principale,
            type_document=TypeDocument.PLUI,
            collectivite_porteuse=commune,
        )

        with django_assert_num_queries(2):
            commune = Commune.objects.with_procedures_principales().get()
            assert commune.procedures_principales == [procedure_principale]

    @pytest.mark.django_db
    def test_exclut_archivees(
        self, django_assert_num_queries: DjangoAssertNumQueries
    ) -> None:
        commune = create_commune()
        procedure_reelle = commune.procedures.create(
            type_document=TypeDocument.PLUI, collectivite_porteuse=commune
        )

        _procedure_supprimee = commune.procedures.create(
            soft_delete=True, collectivite_porteuse=commune
        )

        _procedure_doublon = commune.procedures.create(
            doublon_cache_de=procedure_reelle, collectivite_porteuse=commune
        )

        with django_assert_num_queries(2):
            commune = Commune.objects.with_procedures_principales().get()
            assert commune.procedures_principales == [procedure_reelle]


class TestCommuneOpposabilite:
    @pytest.mark.django_db
    def test_plus_recente_opposable(
        self, django_assert_num_queries: DjangoAssertNumQueries
    ) -> None:
        commune = create_commune()

        procedure_opposable = commune.procedures.create(
            type_document=TypeDocument.PLUI, collectivite_porteuse=commune
        )
        procedure_opposable.event_set.create(
            type="Caractère exécutoire", date_evenement_string="2024-12-01"
        )

        procedure_precedente = commune.procedures.create(
            type_document=TypeDocument.PLU, collectivite_porteuse=commune
        )
        procedure_precedente.event_set.create(
            type="Caractère exécutoire", date_evenement_string="2023-12-01"
        )

        with django_assert_num_queries(2):
            commune = Commune.objects.with_procedures_principales().get()
            assert commune.procedures_principales_approuvees == [
                procedure_opposable,
                procedure_precedente,
            ]

            assert commune.plan_opposable == procedure_opposable
            assert not commune.schema_opposable

            assert commune.is_opposable(procedure_opposable)
            assert not commune.is_opposable(procedure_precedente)

    @pytest.mark.django_db
    def test_plans_et_schemas_opposable(
        self, django_assert_num_queries: DjangoAssertNumQueries
    ) -> None:
        commune = create_commune()

        plan_opposable = commune.procedures.create(
            type_document=TypeDocument.PLUI, collectivite_porteuse=commune
        )
        plan_opposable.event_set.create(
            type="Délibération de prescription du conseil municipal ou communautaire",
            date_evenement_string="2024-12-01",
        )
        plan_opposable.event_set.create(type="Caractère exécutoire")

        schema_opposable = commune.procedures.create(
            type_document=TypeDocument.SCOT, collectivite_porteuse=commune
        )
        schema_opposable.event_set.create(
            type="Délibération de prescription du conseil municipal ou communautaire",
            date_evenement_string="2023-12-01",
        )
        schema_opposable.event_set.create(
            type="Caractère exécutoire",
        )

        with django_assert_num_queries(2):
            commune = Commune.objects.with_procedures_principales().get()
            assert commune.procedures_principales_approuvees == [
                plan_opposable,
                schema_opposable,
            ]

            assert commune.plan_opposable == plan_opposable
            assert commune.schema_opposable == schema_opposable

            assert commune.is_opposable(plan_opposable)
            assert commune.is_opposable(schema_opposable)

    @pytest.mark.django_db
    def test_opposable_sans_prescription(
        self, django_assert_num_queries: DjangoAssertNumQueries
    ) -> None:
        commune = create_commune()

        procedure_opposable = commune.procedures.create(
            type_document=TypeDocument.PLUI, collectivite_porteuse=commune
        )
        procedure_opposable.event_set.create(type="Caractère exécutoire")

        with django_assert_num_queries(2):
            commune = Commune.objects.with_procedures_principales().get()
            assert commune.procedures_principales_approuvees == [procedure_opposable]

            assert commune.plan_opposable == procedure_opposable
            assert not commune.schema_opposable

            assert commune.is_opposable(procedure_opposable)

    @pytest.mark.django_db
    def test_aucune_opposable(
        self, django_assert_num_queries: DjangoAssertNumQueries
    ) -> None:
        commune = create_commune()

        procedure_en_cours = commune.procedures.create(
            type_document=TypeDocument.PLUI, collectivite_porteuse=commune
        )
        procedure_en_cours.event_set.create(
            type="Délibération de prescription du conseil municipal ou communautaire",
            date_evenement_string="2024-12-01",
        )

        with django_assert_num_queries(2):
            commune = Commune.objects.with_procedures_principales().get()
            assert commune.procedures_principales_approuvees == []

            assert not commune.plan_opposable
            assert not commune.schema_opposable

            assert not commune.is_opposable(procedure_en_cours)

    @pytest.mark.django_db
    def test_abrogation_non_opposable(
        self, django_assert_num_queries: DjangoAssertNumQueries
    ) -> None:
        commune = create_commune()

        procedure_approuvee = commune.procedures.create(
            type_document=TypeDocument.PLUI,
            type="Abrogation",
            collectivite_porteuse=commune,
        )
        procedure_approuvee.event_set.create(type="Caractère exécutoire")

        with django_assert_num_queries(2):
            commune = Commune.objects.with_procedures_principales().get()
            assert commune.procedures_principales_approuvees == []

            assert not commune.plan_opposable
            assert not commune.schema_opposable

            assert not commune.is_opposable(procedure_approuvee)

    @pytest.mark.django_db
    def test_ignore_procedures_secondaires(
        self, django_assert_num_queries: DjangoAssertNumQueries
    ) -> None:
        commune = create_commune()

        procedure_principale = commune.procedures.create(
            type_document=TypeDocument.PLUI, collectivite_porteuse=commune
        )
        procedure_secondaire = commune.procedures.create(
            parente=procedure_principale,
            type_document=TypeDocument.PLUI,
            collectivite_porteuse=commune,
        )
        procedure_secondaire.event_set.create(type="Caractère exécutoire")

        with django_assert_num_queries(2):
            commune = Commune.objects.with_procedures_principales().get()
            assert commune.procedures_principales_approuvees == []

            assert not commune.plan_opposable
            assert not commune.schema_opposable

            assert not commune.is_opposable(procedure_principale)
            assert not commune.is_opposable(procedure_secondaire)

    @pytest.mark.django_db
    def test_ignore_procedures_archivees(
        self, django_assert_num_queries: DjangoAssertNumQueries
    ) -> None:
        commune = create_commune()
        procedure_reelle = commune.procedures.create(collectivite_porteuse=commune)

        procedure_supprimee = commune.procedures.create(
            soft_delete=True, collectivite_porteuse=commune
        )
        procedure_supprimee.event_set.create(type="Caractère exécutoire")

        procedure_doublon = commune.procedures.create(
            doublon_cache_de=procedure_reelle, collectivite_porteuse=commune
        )
        procedure_doublon.event_set.create(type="Caractère exécutoire")

        with django_assert_num_queries(2):
            commune = Commune.objects.with_procedures_principales().get()
            assert commune.procedures_principales_approuvees == []

            assert not commune.plan_opposable
            assert not commune.schema_opposable

            assert not commune.is_opposable(procedure_reelle)
            assert not commune.is_opposable(procedure_supprimee)
            assert not commune.is_opposable(procedure_doublon)

    @pytest.mark.django_db
    def test_ignore_event_apres(
        self, django_assert_num_queries: DjangoAssertNumQueries
    ) -> None:
        commune = create_commune()

        procedure_opposable_fevrier = commune.procedures.create(
            type_document=TypeDocument.PLUI, collectivite_porteuse=commune
        )
        procedure_opposable_fevrier.event_set.create(
            type="Caractère exécutoire", date_evenement_string="2024-02-01"
        )

        procedure_opposable_janvier = commune.procedures.create(
            type_document=TypeDocument.PLU, collectivite_porteuse=commune
        )
        procedure_opposable_janvier.event_set.create(
            type="Caractère exécutoire", date_evenement_string="2024-01-01"
        )

        with django_assert_num_queries(1):
            procedures = Procedure.objects.with_events()

            assert all(
                procedure.statut == EventImpact.APPROUVE for procedure in procedures
            )

        with django_assert_num_queries(2):
            commune = Commune.objects.with_procedures_principales(
                avant=date(2024, 2, 1)
            ).get()

        with django_assert_num_queries(0):
            assert commune.procedures_principales == [
                procedure_opposable_janvier,
                procedure_opposable_fevrier,
            ]
            assert commune.procedures_principales_approuvees == [
                procedure_opposable_janvier,
            ]
            assert commune.plan_opposable == procedure_opposable_janvier
            assert not commune.schema_opposable

            assert commune.is_opposable(procedure_opposable_janvier)
            assert not commune.is_opposable(procedure_opposable_fevrier)
