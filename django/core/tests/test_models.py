# ruff: noqa: FBT001, N803
import logging
from datetime import date

import pytest
from pytest_django import DjangoAssertNumQueries

from core.models import (
    EVENT_IMPACT_BY_DOC_TYPE,
    Collectivite,
    Commune,
    Event,
    EventImpact,
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


def test_tous_document_types_ont_event_impact() -> None:
    assert list(TypeDocument) == list(EVENT_IMPACT_BY_DOC_TYPE.keys())


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
            type="Délibération de l'établissement public qui prescrit"
        )

        _groupement_sans_procedure = create_groupement()

        groupement_avec_plan = create_groupement()
        groupement_avec_plan.procedure_set.create(doc_type=TypeDocument.PLU)

        with django_assert_num_queries(3):
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

        with django_assert_num_queries(4):
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
                type="Délibération de l'établissement public qui prescrit"
            )
            scots_en_cours.append(scot_en_cours)

        with django_assert_num_queries(3):
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

        with django_assert_num_queries(3):
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

        with django_assert_num_queries(4):
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
            type="Délibération de l'établissement public qui prescrit"
        )

        scots_opposables = []
        for commune in [commune_a, commune_b]:
            scot_opposable = groupement_avec_scot.procedure_set.create(
                doc_type=TypeDocument.SCOT
            )
            scot_opposable.event_set.create(type="Délibération d'approbation")
            scot_opposable.perimetre.add(commune)
            scots_opposables.append(scot_opposable)

        with django_assert_num_queries(4):
            groupements = list(Collectivite.objects.portant_scot())
            assert groupements == [groupement_avec_scot]

            assert groupements[0].scots_pour_csv == [
                (scots_opposables[0], scot_en_cours),
                (scots_opposables[1], scot_en_cours),
            ]

    @pytest.mark.django_db
    def test_retourne_dates_notables(
        self,
        django_assert_num_queries: DjangoAssertNumQueries,
    ) -> None:
        groupement_avec_scot = create_groupement()
        scot_en_cours = groupement_avec_scot.procedure_set.create(
            doc_type=TypeDocument.SCOT
        )

        with django_assert_num_queries(3):
            groupements = list(Collectivite.objects.portant_scot())
            assert groupements == [groupement_avec_scot]
            assert groupements[0].scots_pour_csv == [(None, scot_en_cours)]

            assert hasattr(
                groupements[0].scots_pour_csv[0][1], "date_publication_perimetre"
            )
            assert hasattr(groupements[0].scots_pour_csv[0][1], "date_arret_projet")
            assert hasattr(groupements[0].scots_pour_csv[0][1], "date_fin_echeance")


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
            type="Délibération de l'établissement public qui prescrit"
        )
        scot_en_cours.perimetre.add(commune_a, commune_b)

        with django_assert_num_queries(4):
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
            type="Délibération de l'établissement public qui prescrit"
        )
        scot_en_cours.perimetre.add(commune_a, commune_b)

        with django_assert_num_queries(4):
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


class TestProcedureDateImpactantes:
    @pytest.mark.django_db
    def test_zero_quand_inexistantes(
        self, django_assert_num_queries: DjangoAssertNumQueries
    ) -> None:
        commune = create_commune()
        procedure = Procedure.objects.create(
            doc_type=TypeDocument.PLUI, collectivite_porteuse=commune
        )

        with django_assert_num_queries(1):
            procedure_with_events = Procedure.objects.with_events().get(id=procedure.id)

            assert procedure_with_events.date_approbation == "0000-00-00"
            assert procedure_with_events.date_prescription == "0000-00-00"

    @pytest.mark.django_db
    @pytest.mark.parametrize(
        ("event_type", "date_impactante"),
        [
            ("Délibération d'approbation", "date_approbation"),
            (
                "Délibération de prescription du conseil municipal ou communautaire",
                "date_prescription",
            ),
        ],
    )
    def test_retourne_plus_recent(
        self,
        event_type: str,
        date_impactante: str,
        django_assert_num_queries: DjangoAssertNumQueries,
    ) -> None:
        commune = create_commune()
        procedure = Procedure.objects.create(
            doc_type=TypeDocument.PLUI,
            collectivite_porteuse=commune,
        )
        for date_string in ("2022-12-01", "2024-12-01", "2023-12-01"):
            procedure.event_set.create(
                type=event_type, date_evenement_string=date_string
            )

        with django_assert_num_queries(1):
            procedure_with_events = Procedure.objects.with_events().get(id=procedure.id)

            assert getattr(procedure_with_events, date_impactante) == "2024-12-01"

    @pytest.mark.django_db
    @pytest.mark.parametrize(
        ("event_type", "date_impactante"),
        [
            ("Délibération d'approbation", "date_approbation"),
            (
                "Délibération de prescription du conseil municipal ou communautaire",
                "date_prescription",
            ),
        ],
    )
    def test_ignore_autre_event_impactant(
        self,
        event_type: str,
        date_impactante: str,
        django_assert_num_queries: DjangoAssertNumQueries,
    ) -> None:
        commune = create_commune()
        procedure = Procedure.objects.create(
            doc_type=TypeDocument.PLUI, collectivite_porteuse=commune
        )
        procedure.event_set.create(type="Gloubi", date_evenement_string="2023-12-01")
        procedure.event_set.create(type=event_type, date_evenement_string="2024-12-01")
        procedure.event_set.create(type="Gloubi", date_evenement_string="2025-12-01")

        with django_assert_num_queries(1):
            procedure_with_events = Procedure.objects.with_events().get(id=procedure.id)

            assert getattr(procedure_with_events, date_impactante) == "2024-12-01"

    @pytest.mark.django_db
    @pytest.mark.parametrize(
        ("event_type", "date_impactante"),
        [
            ("Délibération d'approbation", "date_approbation"),
            (
                "Délibération de prescription du conseil municipal ou communautaire",
                "date_prescription",
            ),
        ],
    )
    def test_ignore_event_pas_valid(
        self,
        event_type: str,
        date_impactante: str,
        django_assert_num_queries: DjangoAssertNumQueries,
    ) -> None:
        commune = create_commune()
        procedure = Procedure.objects.create(
            doc_type=TypeDocument.PLUI, collectivite_porteuse=commune
        )
        procedure.event_set.create(
            type=event_type, date_evenement_string="2024-12-01", is_valid=False
        )

        with django_assert_num_queries(1):
            procedure_with_events = Procedure.objects.with_events().get(id=procedure.id)

            assert getattr(procedure_with_events, date_impactante) == "0000-00-00"

    @pytest.mark.django_db
    @pytest.mark.parametrize(
        ("event_type", "date_impactante"),
        [
            ("Délibération d'approbation", "date_approbation"),
            (
                "Délibération de prescription du conseil municipal ou communautaire",
                "date_prescription",
            ),
        ],
    )
    def test_ignore_event_apres(
        self,
        event_type: str,
        date_impactante: str,
        django_assert_num_queries: DjangoAssertNumQueries,
    ) -> None:
        commune = create_commune()
        procedure = Procedure.objects.create(
            doc_type=TypeDocument.PLUI, collectivite_porteuse=commune
        )
        procedure.event_set.create(type=event_type, date_evenement_string="2022-12-01")

        with django_assert_num_queries(1):
            procedure_with_events = Procedure.objects.with_events(
                avant="2022-11-30"
            ).first()
            assert getattr(procedure_with_events, date_impactante) == "0000-00-00"
        with django_assert_num_queries(1):
            procedure_with_events = Procedure.objects.with_events(
                avant="2022-12-01"
            ).first()
            assert getattr(procedure_with_events, date_impactante) == "0000-00-00"
        with django_assert_num_queries(1):
            procedure_with_events = Procedure.objects.with_events(
                avant="2022-12-02"
            ).first()
            assert getattr(procedure_with_events, date_impactante) == "2022-12-01"


class TestProcedureDatesNotables:
    @pytest.mark.django_db
    def test_none_quand_inexistantes(
        self,
        django_assert_num_queries: DjangoAssertNumQueries,
    ) -> None:
        groupement = create_groupement()
        groupement.procedure_set.create(doc_type=TypeDocument.SCOT)

        with django_assert_num_queries(1):
            procedure = Procedure.objects.with_dates_notables().first()
            assert procedure.date_publication_perimetre is None
            assert procedure.date_arret_projet is None
            assert procedure.date_fin_echeance is None

    @pytest.mark.django_db
    @pytest.mark.parametrize(
        ("event_type", "date_notable"),
        [
            ("Publication périmètre", "date_publication_perimetre"),
            ("Arrêt de projet", "date_arret_projet"),
            ("Fin d'échéance", "date_fin_echeance"),
        ],
    )
    def test_retourne_plus_recent(
        self,
        event_type: str,
        date_notable: str,
        django_assert_num_queries: DjangoAssertNumQueries,
    ) -> None:
        groupement = create_groupement()
        scot = groupement.procedure_set.create(doc_type=TypeDocument.SCOT)
        for date_string in ("2024-01-10", "2024-01-30", "2024-01-20"):
            scot.event_set.create(type=event_type, date_evenement_string=date_string)

        with django_assert_num_queries(1):
            procedure = Procedure.objects.with_dates_notables().first()
            assert getattr(procedure, date_notable) == "2024-01-30"

    @pytest.mark.django_db
    @pytest.mark.parametrize(
        ("event_type", "date_notable"),
        [
            ("Publication périmètre", "date_publication_perimetre"),
            ("Arrêt de projet", "date_arret_projet"),
            ("Fin d'échéance", "date_fin_echeance"),
        ],
    )
    def test_ignore_event_pas_valid(
        self,
        event_type: str,
        date_notable: str,
        django_assert_num_queries: DjangoAssertNumQueries,
    ) -> None:
        groupement = create_groupement()
        scot = groupement.procedure_set.create(doc_type=TypeDocument.SCOT)
        scot.event_set.create(
            type=event_type,
            date_evenement_string="2024-01-30",
            is_valid=False,
        )

        with django_assert_num_queries(1):
            procedure = Procedure.objects.with_dates_notables().first()
            assert getattr(procedure, date_notable) is None

    @pytest.mark.django_db
    @pytest.mark.parametrize(
        ("event_type", "date_notable"),
        [
            ("Publication périmètre", "date_publication_perimetre"),
            ("Arrêt de projet", "date_arret_projet"),
            ("Fin d'échéance", "date_fin_echeance"),
        ],
    )
    def test_ignore_event_apres(
        self,
        event_type: str,
        date_notable: str,
        django_assert_num_queries: DjangoAssertNumQueries,
    ) -> None:
        groupement = create_groupement()
        scot = groupement.procedure_set.create(doc_type=TypeDocument.SCOT)
        scot.event_set.create(type=event_type, date_evenement_string="2024-01-30")

        with django_assert_num_queries(1):
            procedure = Procedure.objects.with_dates_notables(
                avant="2024-01-29"
            ).first()
            assert getattr(procedure, date_notable) is None
        with django_assert_num_queries(1):
            procedure = Procedure.objects.with_dates_notables(
                avant="2024-01-30"
            ).first()
            assert getattr(procedure, date_notable) is None
        with django_assert_num_queries(1):
            procedure = Procedure.objects.with_dates_notables(
                avant="2024-01-31"
            ).first()
            assert getattr(procedure, date_notable) == "2024-01-30"


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


class TestProcedureStatut:
    @pytest.mark.django_db
    def test_principale_opposable(
        self, django_assert_num_queries: DjangoAssertNumQueries
    ) -> None:
        commune = create_commune()
        procedure = Procedure.objects.create(
            doc_type=TypeDocument.PLUI, collectivite_porteuse=commune
        )
        event = procedure.event_set.create(type="Délibération d'approbation")

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
            doc_type=TypeDocument.PLUI, collectivite_porteuse=commune
        )
        event_prescription = procedure.event_set.create(
            type="Délibération de prescription du conseil municipal ou communautaire",
            date_evenement_string="2024-12-03",
        )
        event_approbation = procedure.event_set.create(
            type="Délibération d'approbation", date_evenement_string="2024-12-05"
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
            doc_type=TypeDocument.PLUI, collectivite_porteuse=commune
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
            doc_type=TypeDocument.PLUI, collectivite_porteuse=commune
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
            doc_type=TypeDocument.PLUI, collectivite_porteuse=commune
        )
        event = procedure.event_set.create(
            type="Délibération d'approbation", is_valid=False
        )

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
            doc_type=TypeDocument.CC, collectivite_porteuse=commune
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
            doc_type=TypeDocument.PLUI, collectivite_porteuse=commune
        )
        procedure_secondaire = Procedure.objects.create(
            parente=procedure_principale,
            doc_type=TypeDocument.PLUI,
            collectivite_porteuse=commune,
        )
        procedure_secondaire.event_set.create(type="Délibération d'approbation")

        with django_assert_num_queries(1):
            procedure_with_events = Procedure.objects.with_events().get(
                id=procedure_secondaire.id
            )
            assert not procedure_with_events.statut


class TestEvent:
    @pytest.mark.parametrize(
        ("doc_type", "type_event", "impact"),
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
        self, doc_type: str, type_event: str, impact: EventImpact
    ) -> None:
        procedure = Procedure(doc_type=doc_type)
        assert Event(procedure=procedure, type=type_event).impact == impact


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

        with django_assert_num_queries(2):
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
            doc_type=TypeDocument.PLUI, collectivite_porteuse=commune
        )
        procedure_opposable.event_set.create(
            type="Délibération d'approbation", date_evenement_string="2024-12-01"
        )

        procedure_precedente = commune.procedures.create(
            doc_type=TypeDocument.PLU, collectivite_porteuse=commune
        )
        procedure_precedente.event_set.create(
            type="Délibération d'approbation", date_evenement_string="2023-12-01"
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
            doc_type=TypeDocument.PLUI, collectivite_porteuse=commune
        )
        procedure_opposable.event_set.create(type="Délibération d'approbation")

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
            doc_type=TypeDocument.PLUI, collectivite_porteuse=commune
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
            doc_type=TypeDocument.PLUI,
            type="Abrogation",
            collectivite_porteuse=commune,
        )
        procedure_approuvee.event_set.create(type="Délibération d'approbation")

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
            doc_type=TypeDocument.PLUI, collectivite_porteuse=commune
        )
        procedure_secondaire = commune.procedures.create(
            parente=procedure_principale,
            doc_type=TypeDocument.PLUI,
            collectivite_porteuse=commune,
        )
        procedure_secondaire.event_set.create(type="Délibération d'approbation")

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
        procedure_supprimee.event_set.create(type="Délibération d'approbation")

        procedure_doublon = commune.procedures.create(
            doublon_cache_de=procedure_reelle, collectivite_porteuse=commune
        )
        procedure_doublon.event_set.create(type="Délibération d'approbation")

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
