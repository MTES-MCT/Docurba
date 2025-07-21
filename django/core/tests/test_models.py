# ruff: noqa: FBT001, N803
import logging
from datetime import date

import pytest
from pytest_django import DjangoAssertNumQueries

from core.models import (
    EVENT_CATEGORY_BY_DOC_TYPE,
    Collectivite,
    Commune,
    Event,
    EventCategory,
    Procedure,
    TypeDocument,
)
from core.tests.factories import (
    create_commune,
    create_departement,
    create_groupement,
)


class TestCollectivite:
    def test_code_insee(self) -> None:
        assert Commune(id="12345_COM").code_insee == "12345"


def test_tous_document_types_ont_event_category() -> None:
    assert list(TypeDocument) == list(EVENT_CATEGORY_BY_DOC_TYPE.keys())


class TestCollectivitePortantScot:
    @pytest.mark.django_db
    def test_retourne_que_collectivite_avec_scot(
        self, django_assert_num_queries: DjangoAssertNumQueries
    ) -> None:
        groupement_avec_scot = create_groupement()
        scot_en_cours = groupement_avec_scot.procedure_set.create(
            doc_type=TypeDocument.SCOT
        )
        scot_en_cours.event_set.create(
            type="Délibération de l'établissement public qui prescrit",
            date_evenement_string="2024-12-01",
        )

        _groupement_sans_procedure = create_groupement()

        groupement_avec_plan = create_groupement()
        groupement_avec_plan.procedure_set.create(doc_type=TypeDocument.PLU)

        with django_assert_num_queries(4):
            groupements = list(Collectivite.objects.portant_scot())
            assert groupements == [groupement_avec_scot]

            assert groupements[0].scots_pour_csv == [(None, scot_en_cours)]

    @pytest.mark.django_db
    def test_ignore_procedures_archivees(
        self, django_assert_num_queries: DjangoAssertNumQueries
    ) -> None:
        groupement = create_groupement()
        scot_supprime = groupement.procedure_set.create(
            doc_type=TypeDocument.SCOT, soft_delete=True
        )

        _scot_doublon = groupement.procedure_set.create(
            doc_type=TypeDocument.SCOT, doublon_cache_de=scot_supprime
        )

        with django_assert_num_queries(1):
            assert list(Collectivite.objects.portant_scot()) == []

    @pytest.mark.django_db
    def test_ignore_procedures_secondaires(
        self, django_assert_num_queries: DjangoAssertNumQueries
    ) -> None:
        groupement = create_groupement()
        parent_procedure = groupement.procedure_set.create(
            doc_type=TypeDocument.SCOT, soft_delete=True
        )
        groupement.procedure_set.create(
            doc_type=TypeDocument.SCOT, parente=parent_procedure, archived=False
        )

        with django_assert_num_queries(1):
            assert list(Collectivite.objects.portant_scot()) == []

    @pytest.mark.django_db
    def test_retourne_collectivites_distinctes(
        self,
        django_assert_num_queries: DjangoAssertNumQueries,
    ) -> None:
        groupement_avec_scot = create_groupement()
        commune = create_commune()

        scots_opposables = []
        for date_string in ("2024-02-01", "2024-02-02"):
            scot_opposable = groupement_avec_scot.procedure_set.create(
                doc_type=TypeDocument.SCOT
            )
            scot_opposable.event_set.create(
                type="Délibération d'approbation", date_evenement_string=date_string
            )
            scot_opposable.perimetre.add(commune)
            scots_opposables.append(scot_opposable)

        with django_assert_num_queries(6):
            groupements = list(Collectivite.objects.portant_scot())
            assert groupements == [groupement_avec_scot]

            assert groupements[0].scots_pour_csv == [(scots_opposables[1], None)]

    @pytest.mark.django_db
    def test_fonctionne_et_log_erreur_quand_plusieurs_scots_en_cours(
        self,
        django_assert_num_queries: DjangoAssertNumQueries,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        groupement_avec_scot = create_groupement()

        scots_en_cours = []
        for _ in range(2):
            scot_en_cours = groupement_avec_scot.procedure_set.create(
                doc_type=TypeDocument.SCOT
            )
            scot_en_cours.event_set.create(
                type="Délibération de l'établissement public qui prescrit",
                date_evenement_string="2024-12-01",
            )
            scots_en_cours.append(scot_en_cours)

        with django_assert_num_queries(4):
            groupements = list(Collectivite.objects.portant_scot())
            assert groupements == [groupement_avec_scot]

            assert groupements[0].scots_pour_csv == [(None, scots_en_cours[0])]

            assert caplog.record_tuples == [
                (
                    "root",
                    logging.ERROR,
                    f"Plusieurs SCoT en cours pour la collectivité {groupement_avec_scot.code_insee}",
                )
            ]

    @pytest.mark.django_db
    def test_scot_sans_prescription_considere_en_cours(
        self,
        django_assert_num_queries: DjangoAssertNumQueries,
    ) -> None:
        groupement_avec_scot = create_groupement()
        scot_en_cours = groupement_avec_scot.procedure_set.create(
            doc_type=TypeDocument.SCOT
        )

        with django_assert_num_queries(4):
            groupements = list(Collectivite.objects.portant_scot())
            assert groupements == [groupement_avec_scot]

            assert groupements[0].scots_pour_csv == [(None, scot_en_cours)]

    @pytest.mark.django_db
    def test_retourne_scot_opposables_des_qu_une_commune_considere_opposable(
        self, django_assert_num_queries: DjangoAssertNumQueries
    ) -> None:
        groupement = create_groupement()
        commune_a = create_commune()
        commune_b = create_commune()

        scot_opposable_a = groupement.procedure_set.create(
            doc_type=TypeDocument.SCOT, type="A"
        )
        scot_opposable_a.event_set.create(
            type="Délibération d'approbation", date_evenement_string="2024-01-01"
        )

        scot_precedent_a = groupement.procedure_set.create(
            doc_type=TypeDocument.SCOT, type="B"
        )
        scot_precedent_a.event_set.create(
            type="Délibération d'approbation", date_evenement_string="1999-01-01"
        )
        commune_a.procedures.add(scot_opposable_a, scot_precedent_a)

        scot_opposable_a_et_b = groupement.procedure_set.create(
            doc_type=TypeDocument.SCOT, type="C"
        )
        scot_opposable_a_et_b.event_set.create(
            type="Délibération d'approbation", date_evenement_string="2023-01-01"
        )
        scot_opposable_a_et_b.perimetre.add(commune_a, commune_b)

        with django_assert_num_queries(6):
            groupements = list(Collectivite.objects.portant_scot())
            assert groupements == [groupement]

            assert groupements[0].scots_pour_csv == [
                (scot_opposable_a, None),
                (scot_opposable_a_et_b, None),
            ]

    @pytest.mark.django_db
    def test_retourne_le_meme_scot_en_cours_pour_chaque_opposable(
        self,
        django_assert_num_queries: DjangoAssertNumQueries,
    ) -> None:
        groupement_avec_scot = create_groupement()
        commune_a = create_commune()
        commune_b = create_commune()

        scot_en_cours = groupement_avec_scot.procedure_set.create(
            doc_type=TypeDocument.SCOT
        )
        scot_en_cours.event_set.create(
            type="Délibération de l'établissement public qui prescrit",
            date_evenement_string="2024-12-01",
        )

        scots_opposables = []
        for commune in [commune_a, commune_b]:
            scot_opposable = groupement_avec_scot.procedure_set.create(
                doc_type=TypeDocument.SCOT
            )
            scot_opposable.event_set.create(
                type="Délibération d'approbation", date_evenement_string="2024-12-01"
            )
            scot_opposable.perimetre.add(commune)
            scots_opposables.append(scot_opposable)

        with django_assert_num_queries(6):
            groupements = list(Collectivite.objects.portant_scot())
            assert groupements == [groupement_avec_scot]

            assert groupements[0].scots_pour_csv == [
                (scots_opposables[0], scot_en_cours),
                (scots_opposables[1], scot_en_cours),
            ]


class TestScotInterdepartemental:
    @pytest.mark.django_db
    def test_un_departement(
        self,
        django_assert_num_queries: DjangoAssertNumQueries,
    ) -> None:
        departement = create_departement()
        groupement_avec_scot = create_groupement()
        commune_a = create_commune(departement=departement)
        commune_b = create_commune(departement=departement)

        scot_en_cours = groupement_avec_scot.procedure_set.create(
            doc_type=TypeDocument.SCOT
        )
        scot_en_cours.event_set.create(
            type="Prescription", date_evenement_string="2024-12-01"
        )
        scot_en_cours.perimetre.add(commune_a, commune_b)

        with django_assert_num_queries(6):
            groupements = list(Collectivite.objects.portant_scot())
            assert groupements == [groupement_avec_scot]

            assert not groupements[0].scots[0].is_interdepartemental

    @pytest.mark.django_db
    def test_plusieurs_departements(
        self,
        django_assert_num_queries: DjangoAssertNumQueries,
    ) -> None:
        groupement_avec_scot = create_groupement()
        commune_a = create_commune()
        commune_b = create_commune()

        scot_en_cours = groupement_avec_scot.procedure_set.create(
            doc_type=TypeDocument.SCOT
        )
        scot_en_cours.event_set.create(
            type="Prescription", date_evenement_string="2024-12-01"
        )
        scot_en_cours.perimetre.add(commune_a, commune_b)

        with django_assert_num_queries(6):
            groupements = list(Collectivite.objects.portant_scot())
            assert groupements == [groupement_avec_scot]

            assert groupements[0].scots[0].is_interdepartemental


class TestProcedure:
    def test_is_schema(self) -> None:
        assert not Procedure(doc_type=TypeDocument.CC).is_schema
        assert not Procedure(doc_type=TypeDocument.PLU).is_schema
        assert not Procedure(doc_type=TypeDocument.PLUI).is_schema
        assert not Procedure(doc_type=TypeDocument.PLUIM).is_schema
        assert not Procedure(doc_type=TypeDocument.PLUIH).is_schema
        assert not Procedure(doc_type=TypeDocument.PLUIHM).is_schema

        assert Procedure(doc_type=TypeDocument.SCOT).is_schema
        assert Procedure(doc_type=TypeDocument.SD).is_schema

    @pytest.mark.django_db
    def test_liable_a_collectivite_porteuse_inexistante(self) -> None:
        """Tant que l'on ne gère pas bien les communes des anciens COG."""
        Procedure.objects.create(collectivite_porteuse_id=12)

        assert Procedure.objects.count() == 1

    @pytest.mark.django_db
    def test_liable_a_commune_inexistante(self) -> None:
        """Tant que l'on ne gère pas bien les communes des anciens COG."""
        procedure = Procedure.objects.create()
        procedure.perimetre.through.objects.create(commune_id=12, procedure=procedure)

        assert procedure.perimetre.through.objects.count() == 1


class TestProcedureDates:
    @pytest.mark.django_db
    def test_none_quand_inexistantes(
        self, django_assert_num_queries: DjangoAssertNumQueries
    ) -> None:
        commune = create_commune()
        Procedure.objects.create(
            doc_type=TypeDocument.SCOT, collectivite_porteuse=commune
        )

        with django_assert_num_queries(2):
            procedure = Procedure.objects.with_events().first()

            assert procedure.date_approbation is None
            assert procedure.date_prescription is None
            assert procedure.date_publication_perimetre is None
            assert procedure.date_arret_projet is None
            assert procedure.date_fin_echeance is None

    @pytest.mark.django_db
    @pytest.mark.parametrize(
        ("event_type", "date_attribute"),
        [
            ("Délibération d'approbation", "date_approbation"),
            ("Prescription", "date_prescription"),
            ("Publication périmètre", "date_publication_perimetre"),
            ("Arrêt de projet", "date_arret_projet"),
            ("Fin d'échéance", "date_fin_echeance"),
        ],
    )
    def test_retourne_plus_recent(
        self,
        event_type: str,
        date_attribute: str,
        django_assert_num_queries: DjangoAssertNumQueries,
    ) -> None:
        commune = create_commune()
        procedure = Procedure.objects.create(
            doc_type=TypeDocument.SCOT,
            collectivite_porteuse=commune,
        )
        for date_string in ("2022-12-01", "2024-12-01", "2023-12-01"):
            procedure.event_set.create(
                type=event_type, date_evenement_string=date_string
            )

        with django_assert_num_queries(2):
            procedure_with_events = Procedure.objects.with_events().first()

            assert getattr(procedure_with_events, date_attribute) == date(2024, 12, 1)

    @pytest.mark.django_db
    @pytest.mark.parametrize(
        ("event_type", "date_attribute"),
        [
            ("Délibération d'approbation", "date_approbation"),
            ("Prescription", "date_prescription"),
            ("Publication périmètre", "date_publication_perimetre"),
            ("Arrêt de projet", "date_arret_projet"),
            ("Fin d'échéance", "date_fin_echeance"),
        ],
    )
    def test_ignore_event_pas_valid(
        self,
        event_type: str,
        date_attribute: str,
        django_assert_num_queries: DjangoAssertNumQueries,
    ) -> None:
        commune = create_commune()
        procedure = Procedure.objects.create(
            doc_type=TypeDocument.SCOT, collectivite_porteuse=commune
        )
        procedure.event_set.create(
            type=event_type, date_evenement_string="2024-12-01", is_valid=False
        )

        with django_assert_num_queries(2):
            procedure_with_events = Procedure.objects.with_events().first()

            assert getattr(procedure_with_events, date_attribute) is None

    @pytest.mark.django_db
    @pytest.mark.parametrize(
        ("event_type", "date_attribute"),
        [
            ("Délibération d'approbation", "date_approbation"),
            ("Prescription", "date_prescription"),
            ("Publication périmètre", "date_publication_perimetre"),
            ("Arrêt de projet", "date_arret_projet"),
            ("Fin d'échéance", "date_fin_echeance"),
        ],
    )
    def test_ignore_event_apres(
        self,
        event_type: str,
        date_attribute: str,
        django_assert_num_queries: DjangoAssertNumQueries,
    ) -> None:
        commune = create_commune()
        procedure = Procedure.objects.create(
            doc_type=TypeDocument.SCOT, collectivite_porteuse=commune
        )
        procedure.event_set.create(type=event_type, date_evenement_string="2022-12-01")

        with django_assert_num_queries(2):
            procedure_with_events = Procedure.objects.with_events(
                avant="2022-11-30"
            ).first()
            assert getattr(procedure_with_events, date_attribute) is None
        with django_assert_num_queries(2):
            procedure_with_events = Procedure.objects.with_events(
                avant="2022-12-01"
            ).first()
            assert getattr(procedure_with_events, date_attribute) is None
        with django_assert_num_queries(2):
            procedure_with_events = Procedure.objects.with_events(
                avant="2022-12-02"
            ).first()
            assert getattr(procedure_with_events, date_attribute) == date(2022, 12, 1)


class TestProcedureTypeDocument:
    def test_non_plu_like(self) -> None:
        assert Procedure(doc_type=TypeDocument.CC).type_document == TypeDocument.CC
        assert Procedure(doc_type=TypeDocument.SCOT).type_document == TypeDocument.SCOT
        assert Procedure(doc_type=TypeDocument.SD).type_document == TypeDocument.SD

    @pytest.mark.django_db
    @pytest.mark.parametrize(
        "doc_type",
        [
            (TypeDocument.PLU),
            (TypeDocument.PLUI),
            (TypeDocument.PLUIH),
            (TypeDocument.PLUIM),
            (TypeDocument.PLUIHM),
        ],
    )
    def test_plu(
        self, doc_type: TypeDocument, django_assert_num_queries: DjangoAssertNumQueries
    ) -> None:
        commune = create_commune()
        procedure = Procedure.objects.create(
            doc_type=doc_type, collectivite_porteuse=commune
        )
        procedure.perimetre.add(commune)

        with django_assert_num_queries(1):
            procedure = Procedure.objects.get(id=procedure.id)
            assert procedure.type_document == TypeDocument.PLU

    @pytest.mark.django_db
    @pytest.mark.parametrize(
        "doc_type",
        [
            (TypeDocument.PLU),
            (TypeDocument.PLUI),
        ],
    )
    def test_plui(
        self, doc_type: TypeDocument, django_assert_num_queries: DjangoAssertNumQueries
    ) -> None:
        commune = create_commune()
        procedure = Procedure.objects.create(
            doc_type=doc_type, collectivite_porteuse=commune
        )
        procedure.perimetre.add(commune)
        procedure.perimetre.create(
            id="12346_COM",
            code_insee_unique="12346",
            type="COM",
            departement=commune.departement,
        )

        with django_assert_num_queries(1):
            procedure = Procedure.objects.get(id=procedure.id)
            assert procedure.type_document == TypeDocument.PLUI

    @pytest.mark.django_db
    @pytest.mark.parametrize(
        ("doc_type", "vaut_PLH"),
        [
            (TypeDocument.PLU, True),
            (TypeDocument.PLUI, True),
            (TypeDocument.PLUIH, False),
            (TypeDocument.PLUIH, True),
        ],
    )
    def test_pluih(
        self,
        doc_type: TypeDocument,
        vaut_PLH: bool,
        django_assert_num_queries: DjangoAssertNumQueries,
    ) -> None:
        commune = create_commune()
        procedure = Procedure.objects.create(
            doc_type=doc_type, collectivite_porteuse=commune, vaut_PLH=vaut_PLH
        )
        procedure.perimetre.add(commune)
        procedure.perimetre.create(
            id="12346_COM",
            code_insee_unique="12346",
            type="COM",
            departement=commune.departement,
        )

        with django_assert_num_queries(1):
            procedure = Procedure.objects.get(id=procedure.id)
            assert procedure.type_document == TypeDocument.PLUIH

    @pytest.mark.django_db
    @pytest.mark.parametrize(
        ("doc_type", "vaut_PDM"),
        [
            (TypeDocument.PLU, True),
            (TypeDocument.PLUI, True),
            (TypeDocument.PLUIM, False),
            (TypeDocument.PLUIM, True),
        ],
    )
    def test_pluim(
        self,
        doc_type: TypeDocument,
        vaut_PDM: bool,
        django_assert_num_queries: DjangoAssertNumQueries,
    ) -> None:
        commune = create_commune()
        procedure = Procedure.objects.create(
            doc_type=doc_type, collectivite_porteuse=commune, vaut_PDM=vaut_PDM
        )
        procedure.perimetre.add(commune)
        procedure.perimetre.create(
            id="12346_COM",
            code_insee_unique="12346",
            type="COM",
            departement=commune.departement,
        )

        with django_assert_num_queries(1):
            procedure = Procedure.objects.get(id=procedure.id)
            assert procedure.type_document == TypeDocument.PLUIM

    @pytest.mark.django_db
    @pytest.mark.parametrize(
        ("doc_type", "vaut_PLH", "vaut_PDM"),
        [
            (TypeDocument.PLU, True, True),
            (TypeDocument.PLUI, True, True),
            (TypeDocument.PLUIH, True, True),
            (TypeDocument.PLUIM, True, True),
            (TypeDocument.PLUIHM, False, False),
            (TypeDocument.PLUIHM, False, True),
            (TypeDocument.PLUIHM, True, False),
            (TypeDocument.PLUIHM, True, True),
        ],
    )
    def test_pluihm(
        self,
        doc_type: TypeDocument,
        vaut_PLH: bool,
        vaut_PDM: bool,
        django_assert_num_queries: DjangoAssertNumQueries,
    ) -> None:
        commune = create_commune()
        procedure = Procedure.objects.create(
            doc_type=doc_type,
            collectivite_porteuse=commune,
            vaut_PLH=vaut_PLH,
            vaut_PDM=vaut_PDM,
        )
        procedure.perimetre.add(commune)
        procedure.perimetre.create(
            id="12346_COM",
            code_insee_unique="12346",
            type="COM",
            departement=commune.departement,
        )

        with django_assert_num_queries(1):
            procedure = Procedure.objects.get(id=procedure.id)
            assert procedure.type_document == TypeDocument.PLUIHM


class TestProcedureDelaiApprobation:
    @pytest.mark.django_db
    @pytest.mark.parametrize(
        ("date_approbation", "date_prescription"),
        [
            (None, None),
            ("2024-12-01", None),
            (None, "2024-01-01"),
        ],
    )
    def test_none_si_au_moins_une_date_absente(
        self, date_approbation: str, date_prescription: str
    ) -> None:
        commune = create_commune()
        procedure = Procedure.objects.create(
            doc_type=TypeDocument.PLUI, collectivite_porteuse=commune
        )
        if date_approbation:
            procedure.event_set.create(
                type="Délibération d'approbation",
                date_evenement_string=date_approbation,
            )
        if date_prescription:
            procedure.event_set.create(
                type="Prescription", date_evenement_string=date_prescription
            )

        procedure_with_events = Procedure.objects.with_events().get(id=procedure.id)
        assert procedure_with_events.delai_d_approbation is None

    @pytest.mark.django_db
    def test_delai_d_approbation_calcule(self) -> None:
        commune = create_commune()
        procedure = Procedure.objects.create(
            doc_type=TypeDocument.PLUI, collectivite_porteuse=commune
        )
        procedure.event_set.create(
            type="Prescription", date_evenement_string="2024-01-01"
        )
        procedure.event_set.create(
            type="Délibération d'approbation", date_evenement_string="2024-02-01"
        )

        procedure_with_events = Procedure.objects.with_events().get(id=procedure.id)
        assert procedure_with_events.delai_d_approbation == 31


class TestProcedureSort:
    @pytest.mark.django_db
    def test_approuvee_plus_recemment(self) -> None:
        commune = create_commune()
        procedure_recente = Procedure.objects.create(
            doc_type=TypeDocument.PLUI, collectivite_porteuse=commune
        )
        procedure_recente.event_set.create(
            type="Délibération d'approbation", date_evenement_string="2024-12-01"
        )

        procedure_vieille = Procedure.objects.create(
            doc_type=TypeDocument.PLUI, collectivite_porteuse=commune
        )
        procedure_vieille.event_set.create(
            type="Délibération d'approbation", date_evenement_string="2023-12-01"
        )

        procedure_recent_with_events = Procedure.objects.with_events().get(
            id=procedure_recente.id
        )
        procedure_vieille_with_events = Procedure.objects.with_events().get(
            id=procedure_vieille.id
        )
        assert procedure_vieille_with_events < procedure_recent_with_events

    @pytest.mark.django_db
    def test_prescrite_plus_recemment(self) -> None:
        commune = create_commune()
        procedure_recente = Procedure.objects.create(
            doc_type=TypeDocument.PLUI, collectivite_porteuse=commune
        )
        procedure_recente.event_set.create(
            type="Prescription", date_evenement_string="2024-12-01"
        )

        procedure_vieille = Procedure.objects.create(
            doc_type=TypeDocument.PLUI, collectivite_porteuse=commune
        )
        procedure_vieille.event_set.create(
            type="Prescription", date_evenement_string="2023-12-01"
        )

        procedure_recent_with_events = Procedure.objects.with_events().get(
            id=procedure_recente.id
        )
        procedure_vieille_with_events = Procedure.objects.with_events().get(
            id=procedure_vieille.id
        )
        assert procedure_vieille_with_events < procedure_recent_with_events

    @pytest.mark.django_db
    def test_date_approbation_priorite_quand_date_entremelees(self) -> None:
        commune = create_commune()
        procedure_recente = Procedure.objects.create(
            doc_type=TypeDocument.PLUI, collectivite_porteuse=commune
        )
        procedure_recente.event_set.create(
            type="Prescription", date_evenement_string="1999-12-01"
        )
        procedure_recente.event_set.create(
            type="Délibération d'approbation", date_evenement_string="2024-12-01"
        )

        procedure_vieille = Procedure.objects.create(
            doc_type=TypeDocument.PLUI, collectivite_porteuse=commune
        )
        procedure_vieille.event_set.create(
            type="Prescription", date_evenement_string="2023-12-01"
        )
        procedure_vieille.event_set.create(
            type="Délibération d'approbation", date_evenement_string="2023-12-02"
        )

        procedure_recent_with_events = Procedure.objects.with_events().get(
            id=procedure_recente.id
        )
        procedure_vieille_with_events = Procedure.objects.with_events().get(
            id=procedure_vieille.id
        )
        assert procedure_vieille_with_events < procedure_recent_with_events

    @pytest.mark.django_db
    def test_sans_prescription_utilise_date_creation(self) -> None:
        commune = create_commune()
        procedure_vieille = Procedure.objects.create(
            doc_type=TypeDocument.PLUI, collectivite_porteuse=commune
        )
        procedure_recente = Procedure.objects.create(
            doc_type=TypeDocument.PLUI, collectivite_porteuse=commune
        )

        procedure_recent_with_events = Procedure.objects.with_events().get(
            id=procedure_recente.id
        )
        procedure_vieille_with_events = Procedure.objects.with_events().get(
            id=procedure_vieille.id
        )

        assert procedure_vieille_with_events < procedure_recent_with_events
        assert not procedure_vieille_with_events > procedure_recent_with_events


class TestProcedureStatut:
    @pytest.mark.django_db
    def test_principale_opposable(
        self, django_assert_num_queries: DjangoAssertNumQueries
    ) -> None:
        commune = create_commune()
        procedure = Procedure.objects.create(
            doc_type=TypeDocument.PLUI, collectivite_porteuse=commune
        )
        event = procedure.event_set.create(
            type="Délibération d'approbation", date_evenement_string="2024-12-01"
        )

        assert event.category == EventCategory.APPROUVE
        with django_assert_num_queries(2):
            procedure_with_events = Procedure.objects.with_events().get(id=procedure.id)

            assert procedure_with_events.dernier_event_impactant == event
            assert procedure_with_events.statut == EventCategory.APPROUVE

    @pytest.mark.django_db
    @pytest.mark.parametrize(
        ("jour_limite", "statut"),
        [
            (3, None),
            (4, EventCategory.PRESCRIPTION),
            (5, EventCategory.PRESCRIPTION),
            (6, EventCategory.APPROUVE),
        ],
    )
    def test_ignore_event_apres(
        self,
        django_assert_num_queries: DjangoAssertNumQueries,
        jour_limite: int,
        statut: EventCategory,
    ) -> None:
        commune = create_commune()
        procedure = Procedure.objects.create(
            doc_type=TypeDocument.PLUI, collectivite_porteuse=commune
        )
        event_prescription = procedure.event_set.create(
            type="Délibération de prescription du conseil municipal ou communautaire",
            date_evenement_string="2024-12-03",
        )
        event_approbation = procedure.event_set.create(
            type="Délibération d'approbation", date_evenement_string="2024-12-05"
        )

        assert event_prescription.category == EventCategory.PRESCRIPTION
        assert event_approbation.category == EventCategory.APPROUVE
        with django_assert_num_queries(2):
            procedure_with_events = Procedure.objects.with_events(
                avant=date(2024, 12, jour_limite)
            ).get(id=procedure.id)

            assert procedure_with_events.statut == statut

    @pytest.mark.django_db
    def test_principale_sans_evenement(
        self, django_assert_num_queries: DjangoAssertNumQueries
    ) -> None:
        commune = create_commune()
        procedure = Procedure.objects.create(
            doc_type=TypeDocument.PLUI, collectivite_porteuse=commune
        )

        with django_assert_num_queries(2):
            procedure_with_events = Procedure.objects.with_events().get(id=procedure.id)

            assert not procedure_with_events.dernier_event_impactant
            assert not procedure_with_events.statut

    @pytest.mark.django_db
    def test_principale_annule(
        self, django_assert_num_queries: DjangoAssertNumQueries
    ) -> None:
        commune = create_commune()
        procedure = Procedure.objects.create(
            doc_type=TypeDocument.PLUI, collectivite_porteuse=commune
        )
        event = procedure.event_set.create(
            type="Abrogation", date_evenement_string="2024-12-01"
        )

        assert event.category == EventCategory.ANNULE
        with django_assert_num_queries(2):
            procedure_with_events = Procedure.objects.with_events().get(id=procedure.id)

            assert procedure_with_events.dernier_event_impactant == event
            assert procedure_with_events.statut == EventCategory.ANNULE

    @pytest.mark.django_db
    def test_principale_ignore_event_invalide(
        self, django_assert_num_queries: DjangoAssertNumQueries
    ) -> None:
        commune = create_commune()
        procedure = Procedure.objects.create(
            doc_type=TypeDocument.PLUI, collectivite_porteuse=commune
        )
        event = procedure.event_set.create(
            type="Délibération d'approbation",
            date_evenement_string="2024-12-01",
            is_valid=False,
        )

        assert event.category is None
        with django_assert_num_queries(2):
            procedure_with_events = Procedure.objects.with_events().get(id=procedure.id)

            assert not procedure_with_events.dernier_event_impactant
            assert not procedure_with_events.statut

    @pytest.mark.django_db
    def test_principale_carte_communale_deliberation_d_approbation_pas_opposable(
        self, django_assert_num_queries: DjangoAssertNumQueries
    ) -> None:
        commune = create_commune()
        procedure = Procedure.objects.create(
            doc_type=TypeDocument.CC, collectivite_porteuse=commune
        )
        event = procedure.event_set.create(
            type="Délibération d'approbation", date_evenement_string="2024-12-01"
        )

        assert event.category is None
        with django_assert_num_queries(2):
            procedure_with_events = Procedure.objects.with_events().get(id=procedure.id)

            assert not procedure_with_events.dernier_event_impactant
            assert not procedure_with_events.statut

    @pytest.mark.django_db
    def test_secondaire_non_opposable(
        self, django_assert_num_queries: DjangoAssertNumQueries
    ) -> None:
        commune = create_commune()
        procedure_principale = Procedure.objects.create(
            doc_type=TypeDocument.PLUI, collectivite_porteuse=commune
        )
        procedure_secondaire = Procedure.objects.create(
            parente=procedure_principale,
            doc_type=TypeDocument.PLUI,
            collectivite_porteuse=commune,
        )
        procedure_secondaire.event_set.create(
            type="Délibération d'approbation", date_evenement_string="2024-12-01"
        )

        with django_assert_num_queries(2):
            procedure_with_events = Procedure.objects.with_events().get(
                id=procedure_secondaire.id
            )

            assert not procedure_with_events.dernier_event_impactant
            assert not procedure_with_events.statut

    @pytest.mark.django_db
    def test_approuvee_quand_prescription_et_approbation_meme_jour(
        self, django_assert_num_queries: DjangoAssertNumQueries
    ) -> None:
        commune = create_commune()
        procedure = Procedure.objects.create(
            doc_type=TypeDocument.PLUI, collectivite_porteuse=commune
        )
        prescription_inseree_avant = procedure.event_set.create(
            type="Prescription", date_evenement_string="2023-04-26"
        )
        approbation = procedure.event_set.create(
            type="Délibération d'approbation", date_evenement_string="2023-04-26"
        )
        prescription_inseree_apres = procedure.event_set.create(
            type="Prescription", date_evenement_string="2023-04-26"
        )

        assert approbation.category == EventCategory.APPROUVE
        assert prescription_inseree_avant.category == EventCategory.PRESCRIPTION
        assert prescription_inseree_apres.category == EventCategory.PRESCRIPTION

        with django_assert_num_queries(2):
            procedure_with_events = Procedure.objects.with_events().first()

            assert procedure_with_events.dernier_event_impactant == approbation
            assert procedure_with_events.statut == EventCategory.APPROUVE

    @pytest.mark.django_db
    def test_abandon_quand_prescription_et_abandon_meme_jour(
        self, django_assert_num_queries: DjangoAssertNumQueries
    ) -> None:
        commune = create_commune()
        procedure = Procedure.objects.create(
            doc_type=TypeDocument.PLUI, collectivite_porteuse=commune
        )
        prescription_insere_avant = procedure.event_set.create(
            type="Prescription", date_evenement_string="2023-04-26"
        )
        abandon = procedure.event_set.create(
            type="Abandon", date_evenement_string="2023-04-26"
        )
        prescription_insere_apres = procedure.event_set.create(
            type="Prescription", date_evenement_string="2023-04-26"
        )

        assert abandon.category == EventCategory.ABANDON
        assert prescription_insere_avant.category == EventCategory.PRESCRIPTION
        assert prescription_insere_apres.category == EventCategory.PRESCRIPTION

        with django_assert_num_queries(2):
            procedure_with_events = Procedure.objects.with_events().first()

            assert procedure_with_events.dernier_event_impactant == abandon
            assert procedure_with_events.statut == EventCategory.ABANDON

    @pytest.mark.django_db
    def test_event_sans_date_ignore(
        self, django_assert_num_queries: DjangoAssertNumQueries
    ) -> None:
        commune = create_commune()
        procedure = Procedure.objects.create(
            doc_type=TypeDocument.PLUI, collectivite_porteuse=commune
        )
        event = procedure.event_set.create(type="Délibération d'approbation")

        assert event.category == EventCategory.APPROUVE
        with django_assert_num_queries(2):
            procedure_with_events = Procedure.objects.with_events().get(id=procedure.id)

            assert not procedure_with_events.dernier_event_impactant
            assert not procedure_with_events.statut


class TestEvent:
    @pytest.mark.parametrize(
        ("doc_type", "type_event", "category"),
        [
            ("PLU", "lol", None),
            (
                "PLU",
                "Délibération de prescription du conseil municipal ou communautaire",
                "prescription",
            ),
            (
                "PLUi",
                "Délibération de prescription du conseil municipal ou communautaire",
                "prescription",
            ),
            ("CC", "Délibération d'approbation", None),
        ],
    )
    def test_event_category(
        self, doc_type: str, type_event: str, category: EventCategory
    ) -> None:
        procedure = Procedure(doc_type=doc_type)
        assert Event(procedure=procedure, type=type_event).category == category

    def test_date_null(self) -> None:
        procedure = Procedure()
        assert Event(procedure=procedure).date is None


class TestCommuneProceduresPrincipales:
    @pytest.mark.django_db
    def test_exclut_secondaires(
        self, django_assert_num_queries: DjangoAssertNumQueries
    ) -> None:
        commune = create_commune()

        procedure_principale = commune.procedures.create(
            doc_type=TypeDocument.PLUI, collectivite_porteuse=commune
        )
        _procedure_secondaire = commune.procedures.create(
            parente=procedure_principale,
            doc_type=TypeDocument.PLUI,
            collectivite_porteuse=commune,
        )

        with django_assert_num_queries(3):
            commune = Commune.objects.with_procedures_principales().get()
            assert commune.procedures_principales == [procedure_principale]

    @pytest.mark.django_db
    def test_exclut_archivees(
        self, django_assert_num_queries: DjangoAssertNumQueries
    ) -> None:
        commune = create_commune()
        procedure_reelle = commune.procedures.create(
            doc_type=TypeDocument.PLUI, collectivite_porteuse=commune
        )

        _procedure_supprimee = commune.procedures.create(
            soft_delete=True, collectivite_porteuse=commune
        )

        _procedure_doublon = commune.procedures.create(
            doublon_cache_de=procedure_reelle, collectivite_porteuse=commune
        )

        with django_assert_num_queries(3):
            commune = Commune.objects.with_procedures_principales().get()
            assert commune.procedures_principales == [procedure_reelle]


class TestCommunePlanEnCours:
    """Ces tests devront être revus avec https://github.com/MTES-MCT/Docurba/issues/1174."""

    @pytest.mark.django_db
    def test_plus_recent_en_cours(
        self, django_assert_num_queries: DjangoAssertNumQueries
    ) -> None:
        commune = create_commune()

        procedure_saisie_avant = commune.procedures.create(
            doc_type=TypeDocument.PLU, collectivite_porteuse=commune
        )
        procedure_saisie_avant.event_set.create(
            type="Prescription", date_evenement_string="2022-12-01"
        )

        procedure_en_cours = commune.procedures.create(
            doc_type=TypeDocument.PLUI, collectivite_porteuse=commune
        )
        procedure_en_cours.event_set.create(
            type="Prescription", date_evenement_string="2024-12-01"
        )

        procedure_saisie_apres = commune.procedures.create(
            doc_type=TypeDocument.PLU, collectivite_porteuse=commune
        )
        procedure_saisie_apres.event_set.create(
            type="Prescription", date_evenement_string="2023-12-01"
        )

        with django_assert_num_queries(3):
            commune = Commune.objects.with_procedures_principales().get()
            assert commune.procedures_principales_en_cours == [
                procedure_en_cours,
                procedure_saisie_apres,
                procedure_saisie_avant,
            ]
            assert commune.plan_en_cours == procedure_en_cours

    @pytest.mark.django_db
    def test_exclut_abrogation(
        self, django_assert_num_queries: DjangoAssertNumQueries
    ) -> None:
        commune = create_commune()

        procedure_principale = commune.procedures.create(
            doc_type=TypeDocument.PLUI, collectivite_porteuse=commune
        )
        procedure_principale.event_set.create(
            type="Prescription", date_evenement_string="2024-12-01"
        )

        procedure_abrogation = commune.procedures.create(
            doc_type=TypeDocument.PLUI,
            type="Abrogation",
            collectivite_porteuse=commune,
        )
        procedure_abrogation.event_set.create(
            type="Prescription", date_evenement_string="2024-12-01"
        )

        with django_assert_num_queries(3):
            commune = Commune.objects.with_procedures_principales().get()
            assert commune.procedures_principales_en_cours == [procedure_principale]
            assert commune.plan_en_cours == procedure_principale


class TestCommune:
    @pytest.mark.django_db
    def test_is_pas_nouvelle(self) -> None:
        commune = create_commune()

        assert not commune.is_nouvelle

    @pytest.mark.django_db
    def test_is_nouvelle(self) -> None:
        commune_nouvelle = create_commune()
        _commune_deleguee = create_commune(nouvelle=commune_nouvelle)

        assert commune_nouvelle.is_nouvelle


class TestCommuneCollectivitePorteuse:
    @pytest.mark.parametrize(
        ("plan_opposable", "plan_en_cours", "collectivite_attendue"),
        [
            (False, True, "EN COURS"),
            (True, False, "OPPOSABLE"),
            (True, True, "EN COURS"),
            (False, False, "SOI MÊME"),
        ],
    )
    @pytest.mark.django_db
    def test_retourne_collectivite_portant_plan_en_cours(
        self, plan_opposable: bool, plan_en_cours: bool, collectivite_attendue: str
    ) -> None:
        commune = create_commune(code_insee="SOI MÊME")

        if plan_en_cours:
            groupement = create_groupement(code_insee="EN COURS")
            procedure = commune.procedures.create(
                doc_type=TypeDocument.PLU, collectivite_porteuse=groupement
            )
            procedure.event_set.create(
                type="Prescription", date_evenement_string="2022-12-01"
            )

        if plan_opposable:
            groupement = create_groupement(code_insee="OPPOSABLE")
            procedure = commune.procedures.create(
                doc_type=TypeDocument.PLU, collectivite_porteuse=groupement
            )
            procedure.event_set.create(
                type="Délibération d'approbation", date_evenement_string="2022-12-01"
            )

        commune = Commune.objects.with_procedures_principales().first()
        assert commune.collectivite_porteuse.code_insee == collectivite_attendue


class TestCommuneOpposabilite:
    @pytest.mark.django_db
    def test_plus_recente_opposable(
        self, django_assert_num_queries: DjangoAssertNumQueries
    ) -> None:
        commune = create_commune()
        procedure_precedente_saisie_avant = commune.procedures.create(
            doc_type=TypeDocument.PLU, collectivite_porteuse=commune
        )
        procedure_precedente_saisie_avant.event_set.create(
            type="Délibération d'approbation", date_evenement_string="2022-12-01"
        )

        procedure_opposable = commune.procedures.create(
            doc_type=TypeDocument.PLUI, collectivite_porteuse=commune
        )
        procedure_opposable.event_set.create(
            type="Délibération d'approbation", date_evenement_string="2024-12-01"
        )

        procedure_precedente_saisie_apres = commune.procedures.create(
            doc_type=TypeDocument.PLU, collectivite_porteuse=commune
        )
        procedure_precedente_saisie_apres.event_set.create(
            type="Délibération d'approbation", date_evenement_string="2023-12-01"
        )

        with django_assert_num_queries(3):
            commune = Commune.objects.with_procedures_principales().get()
            assert commune.procedures_principales_approuvees == [
                procedure_opposable,
                procedure_precedente_saisie_apres,
                procedure_precedente_saisie_avant,
            ]

            assert commune.plan_opposable == procedure_opposable
            assert not commune.schema_opposable

            assert commune.is_opposable(procedure_opposable)
            assert not commune.is_opposable(procedure_precedente_saisie_apres)

    @pytest.mark.django_db
    def test_plans_et_schemas_opposable(
        self, django_assert_num_queries: DjangoAssertNumQueries
    ) -> None:
        commune = create_commune()

        plan_opposable = commune.procedures.create(
            doc_type=TypeDocument.PLUI, collectivite_porteuse=commune
        )
        plan_opposable.event_set.create(
            type="Délibération d'approbation", date_evenement_string="2024-01-02"
        )

        schema_opposable = commune.procedures.create(
            doc_type=TypeDocument.SCOT, collectivite_porteuse=commune
        )
        schema_opposable.event_set.create(
            type="Délibération d'approbation", date_evenement_string="2024-01-01"
        )

        with django_assert_num_queries(3):
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
            doc_type=TypeDocument.PLUI, collectivite_porteuse=commune
        )
        procedure_opposable.event_set.create(
            type="Délibération d'approbation", date_evenement_string="2024-12-01"
        )

        with django_assert_num_queries(3):
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
            doc_type=TypeDocument.PLUI, collectivite_porteuse=commune
        )
        procedure_en_cours.event_set.create(
            type="Délibération de prescription du conseil municipal ou communautaire",
            date_evenement_string="2024-12-01",
        )

        with django_assert_num_queries(3):
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
            doc_type=TypeDocument.PLUI,
            type="Abrogation",
            collectivite_porteuse=commune,
        )
        procedure_approuvee.event_set.create(
            type="Délibération d'approbation", date_evenement_string="2024-12-01"
        )

        with django_assert_num_queries(3):
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
            doc_type=TypeDocument.PLUI, collectivite_porteuse=commune
        )
        procedure_secondaire = commune.procedures.create(
            parente=procedure_principale,
            doc_type=TypeDocument.PLUI,
            collectivite_porteuse=commune,
        )
        procedure_secondaire.event_set.create(
            type="Délibération d'approbation", date_evenement_string="2024-12-01"
        )

        with django_assert_num_queries(3):
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
        procedure_supprimee.event_set.create(
            type="Délibération d'approbation", date_evenement_string="2024-12-01"
        )

        procedure_doublon = commune.procedures.create(
            doublon_cache_de=procedure_reelle, collectivite_porteuse=commune
        )
        procedure_doublon.event_set.create(
            type="Délibération d'approbation", date_evenement_string="2024-12-01"
        )

        with django_assert_num_queries(3):
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
            doc_type=TypeDocument.PLUI, collectivite_porteuse=commune
        )
        procedure_opposable_fevrier.event_set.create(
            type="Délibération d'approbation", date_evenement_string="2024-02-01"
        )

        procedure_opposable_janvier = commune.procedures.create(
            doc_type=TypeDocument.PLU, collectivite_porteuse=commune
        )
        procedure_opposable_janvier.event_set.create(
            type="Délibération d'approbation", date_evenement_string="2024-01-01"
        )

        with django_assert_num_queries(2):
            procedures = Procedure.objects.with_events()

            assert all(
                procedure.statut == EventCategory.APPROUVE for procedure in procedures
            )

        with django_assert_num_queries(3):
            commune = Commune.objects.with_procedures_principales(
                avant=date(2024, 2, 1)
            ).get()

        with django_assert_num_queries(0):
            assert set(commune.procedures_principales) == {
                procedure_opposable_fevrier,
                procedure_opposable_janvier,
            }
            assert commune.procedures_principales_approuvees == [
                procedure_opposable_janvier,
            ]
            assert commune.plan_opposable == procedure_opposable_janvier
            assert not commune.schema_opposable

            assert commune.is_opposable(procedure_opposable_janvier)
            assert not commune.is_opposable(procedure_opposable_fevrier)
