from csv import DictReader
from itertools import product

import pytest
from django.test import Client
from django.urls import reverse
from pytest_django import DjangoAssertNumQueries

from docurba.core.models import TypeDocument
from tests.core.factories import (
    CollectiviteFactory,
    CommuneFactory,
    EventFactory,
    ProcedureFactory,
)


class TestAPI:
    @pytest.mark.parametrize(
        ("invalid_avant", "path"),
        product(
            ("2023-1-01", "2023-02-30", "invalid-date", "2023/01/01"),
            ("/api/perimetres", reverse("api_scots")),
        ),
    )
    def test_parsing_avant(self, client: Client, invalid_avant: str, path: str) -> None:
        response = client.get(path, {"avant": invalid_avant})

        assert response.status_code == 400
        assert (
            response.content.decode()
            == "Le paramètre 'avant' doit être une date valide au format YYYY-MM-DD."
        )


class TestAPIPerimetres:
    @pytest.mark.django_db
    def test_format_csv(
        self, client: Client, django_assert_num_queries: DjangoAssertNumQueries
    ) -> None:
        commune = CommuneFactory(type="COM")
        ProcedureFactory(
            collectivite_porteuse=commune,
            doc_type=TypeDocument.PLU,
            with_perimetre=[commune],
        )

        with django_assert_num_queries(3):
            response = client.get(
                "/api/perimetres", {"departement": commune.departement.code_insee}
            )

        assert response.status_code == 200
        assert response["content-type"] == "text/csv;charset=utf-8"

        reader = DictReader(response.content.decode().splitlines())

        assert list(reader) == [
            {
                "annee_cog": "2024",
                "collectivite_code": commune.code_insee_unique,
                "collectivite_type": "COM",
                "procedure_id": str(commune.procedures.first().id),
                "opposable": "False",
                "type_document": commune.procedures.first().type_document,
            }
        ]

    @pytest.mark.parametrize(
        ("is_filtering", "expected_lignes"), [(False, 2), (True, 1)]
    )
    @pytest.mark.django_db
    def test_filtre_par_department(
        self,
        is_filtering: bool,  # noqa: FBT001
        expected_lignes: int,
        client: Client,
    ) -> None:
        commune_a = CommuneFactory(departement__code_insee="13")
        commune_b = CommuneFactory(departement__code_insee="84")

        ProcedureFactory(
            collectivite_porteuse=commune_a,
            doc_type=TypeDocument.PLU,
            with_perimetre=[commune_a],
        )
        ProcedureFactory(
            collectivite_porteuse=commune_b,
            doc_type=TypeDocument.PLU,
            with_perimetre=[commune_b],
        )

        filtre = {}
        if is_filtering:
            filtre = {"departement": commune_a.departement.code_insee}
        response = client.get("/api/perimetres", filtre)
        reader = DictReader(response.content.decode().splitlines())
        assert len(list(reader)) == expected_lignes

    @pytest.mark.django_db
    @pytest.mark.parametrize(
        ("avant", "opposable"),
        [
            ("", "True"),
            ("2023-01-01", "False"),
        ],
    )
    def test_ignore_event_apres(
        self,
        client: Client,
        avant: str,
        opposable: str,
        django_assert_num_queries: DjangoAssertNumQueries,
    ) -> None:
        commune = CommuneFactory()
        procedure = ProcedureFactory(
            collectivite_porteuse=commune,
            doc_type=TypeDocument.PLU,
            with_perimetre=[commune],
        )
        procedure.event_set.create(
            type="Délibération d'approbation", date_evenement="2023-01-02"
        )

        with django_assert_num_queries(3):
            response = client.get("/api/perimetres", {"avant": avant})
        reader = DictReader(response.content.decode().splitlines())
        assert [cp["opposable"] for cp in reader] == [opposable]


class TestAPICommunes:
    @pytest.mark.django_db
    def test_format_csv(
        self, client: Client, django_assert_num_queries: DjangoAssertNumQueries
    ) -> None:
        collectivite = CollectiviteFactory()
        commune = CommuneFactory()
        plan_en_cours = ProcedureFactory(
            collectivite_porteuse=collectivite,
            doc_type=TypeDocument.PLU,
            with_perimetre=[commune],
        )
        plan_en_cours.event_set.create(type="Prescription", date_evenement="2024-12-01")
        plan_opposable = ProcedureFactory(
            collectivite_porteuse=collectivite,
            doc_type=TypeDocument.PLU,
            with_perimetre=[commune],
        )

        plan_opposable.event_set.create(
            type="Délibération d'approbation", date_evenement="2024-12-01"
        )

        with django_assert_num_queries(4):
            response = client.get("/api/communes")

        assert response.status_code == 200
        assert response["content-type"] == "text/csv;charset=utf-8"

        reader = DictReader(response.content.decode().splitlines())

        communes = list(reader)
        assert len(communes) == 1
        assert communes[0]["pc_docurba_id"] == str(plan_en_cours.id)
        assert communes[0]["pa_docurba_id"] == str(plan_opposable.id)

    @pytest.mark.django_db
    def test_commune_sans_intercommunalite_ne_crashe_pas(self, client: Client) -> None:
        """
        4 îles n'ont pas d'intercommunalité.

        https://fr.wikipedia.org/wiki/Catégorie:Commune_hors_intercommunalité_à_fiscalité_propre_en_France
        """
        CommuneFactory(intercommunalite=None)

        response = client.get("/api/communes")

        assert response.status_code == 200

        reader = DictReader(response.content.decode().splitlines())

        assert len(list(reader)) == 1

    @pytest.mark.parametrize(
        ("is_filtering", "expected_lignes"), [(False, 2), (True, 1)]
    )
    @pytest.mark.django_db
    def test_filtre_par_department(
        self,
        is_filtering: bool,  # noqa: FBT001
        expected_lignes: int,
        client: Client,
    ) -> None:
        commune_a = CommuneFactory(departement__code_insee="13")
        CommuneFactory(departement__code_insee="84")

        filtre = {}
        if is_filtering:
            filtre = {"departement": commune_a.departement.code_insee}

        response = client.get("/api/communes", filtre)
        reader = DictReader(response.content.decode().splitlines())

        assert len(list(reader)) == expected_lignes

    @pytest.mark.django_db
    @pytest.mark.parametrize(
        ("avant", "champ_procedure_id"),
        [
            ("", "pa_docurba_id"),
            ("2023-01-01", "pc_docurba_id"),
        ],
    )
    def test_ignore_event_apres(
        self, client: Client, avant: str, champ_procedure_id: str
    ) -> None:
        collectivite = CollectiviteFactory()
        commune = CommuneFactory()
        procedure = ProcedureFactory(
            collectivite_porteuse=collectivite,
            doc_type=TypeDocument.PLU,
            with_perimetre=[commune],
        )

        procedure.event_set.create(type="Prescription", date_evenement="2021-12-01")
        procedure.event_set.create(
            type="Délibération d'approbation", date_evenement="2024-01-01"
        )

        response = client.get("/api/communes", {"avant": avant})

        reader = DictReader(response.content.decode().splitlines())
        assert [collectivite[champ_procedure_id] for collectivite in reader] == [
            str(procedure.id)
        ]

    @pytest.mark.django_db
    def test_nb_queries(
        self, client: Client, django_assert_num_queries: DjangoAssertNumQueries
    ) -> None:
        for _ in range(2):
            collectivite = CollectiviteFactory()
            commune = CommuneFactory()
            plan_en_cours = ProcedureFactory(
                collectivite_porteuse=collectivite,
                doc_type=TypeDocument.PLU,
                with_perimetre=[commune],
            )
            plan_en_cours.event_set.create(
                type="Prescription", date_evenement="2024-12-01"
            )

            with django_assert_num_queries(4):
                response = client.get("/api/communes")

        reader = DictReader(response.content.decode().splitlines())
        assert [cp["pc_type_document"] for cp in reader] == ["PLU", "PLU"]


class TestAPIScots:
    @pytest.mark.django_db
    def test_format_csv(
        self, client: Client, django_assert_num_queries: DjangoAssertNumQueries
    ) -> None:
        event = EventFactory(
            type="Publication de périmètre", procedure__doc_type=TypeDocument.SCOT
        )
        collectivite = event.procedure.collectivite_porteuse

        with django_assert_num_queries(4):
            response = client.get(reverse("api_scots"))

        assert response.status_code == 200
        assert response["content-type"] == "text/csv;charset=utf-8"

        reader = DictReader(response.content.decode().splitlines())

        assert list(reader) == [
            {
                "annee_cog": "2024",
                # Collectivité
                "scot_code_region": collectivite.departement.region.code_insee,
                "scot_libelle_region": collectivite.departement.region.nom,
                "scot_code_departement": collectivite.departement.code_insee,
                "scot_lib_departement": collectivite.departement.nom,
                "scot_codecollectivite": collectivite.code_insee,
                "scot_code_type_collectivite": collectivite.type,
                "scot_nom_collectivite": collectivite.nom,
                # Approuvée
                "pa_id": "",
                "pa_nom_schema": "",
                "pa_noserie_procedure": "",
                "pa_scot_interdepartement": "",
                "pa_date_publication_perimetre": "",
                "pa_date_prescription": "",
                "pa_date_arret_projet": "",
                "pa_date_approbation": "",
                "pa_annee_approbation": "",
                "pa_date_fin_echeance": "",
                "pa_nombre_communes": "",
                # En cours
                "pc_id": str(event.procedure.id),
                "pc_nom_schema": event.procedure.name,
                "pc_noserie_procedure": "",
                "pc_proc_elaboration_revision": "Élaboration",
                "pc_scot_interdepartement": "False",
                "pc_date_publication_perimetre": str(event.date_evenement),
                "pc_date_prescription": "",
                "pc_date_arret_projet": "",
                "pc_nombre_communes": "0",
            }
        ]

    @pytest.mark.parametrize(
        ("is_filtering", "expected_lignes"), [(False, 2), (True, 1)]
    )
    @pytest.mark.django_db
    def test_filtre_par_department(
        self,
        is_filtering: bool,  # noqa: FBT001
        expected_lignes: int,
        client: Client,
    ) -> None:

        event_a = EventFactory(
            type="Publication de périmètre",
            procedure__doc_type=TypeDocument.SCOT,
            procedure__collectivite_porteuse__departement__code_insee="13",
        )
        EventFactory(
            type="Publication de périmètre",
            procedure__doc_type=TypeDocument.SCOT,
            procedure__collectivite_porteuse__departement__code_insee="84",
        )
        collectivite_a = event_a.procedure.collectivite_porteuse

        filtre = {}
        if is_filtering:
            filtre = {"departement": collectivite_a.departement.code_insee}
        response = client.get(reverse("api_scots"), filtre)
        reader = DictReader(response.content.decode().splitlines())
        assert len(list(reader)) == expected_lignes

    @pytest.mark.django_db
    @pytest.mark.parametrize(
        ("avant", "champ_procedure_id"),
        [
            ("", "pa_id"),
            ("2025-09-01", "pc_id"),
        ],
    )
    def test_ignore_event_apres(
        self, client: Client, avant: str, champ_procedure_id: str
    ) -> None:
        commune = CommuneFactory()
        event_a = EventFactory(
            type="Publication de périmètre",
            date_evenement="2024-12-01",
            procedure__doc_type=TypeDocument.SCOT,
            procedure__with_perimetre=[commune],
        )
        procedure = event_a.procedure
        EventFactory(
            type="Délibération d'approbation",
            date_evenement="2025-10-01",
            procedure=procedure,
        )

        response = client.get(reverse("api_scots"), {"avant": avant})

        reader = DictReader(response.content.decode().splitlines())
        assert [collectivite[champ_procedure_id] for collectivite in reader] == [
            str(procedure.id)
        ]
