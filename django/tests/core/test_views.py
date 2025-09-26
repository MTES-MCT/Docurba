from csv import DictReader
from itertools import product

import pytest
from django.test import Client
from django.urls import reverse
from pytest_django import DjangoAssertNumQueries

from core.models import (
    EventCategory,
    Procedure,
    TypeDocument,
    ViewCommuneAdhesionsDeep,
)
from core.views import TypeCollectivite
from tests.factories import (
    create_commune,
    create_departement,
    create_groupement,
    create_procedure,
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
        commune = create_commune(code_insee="12345", commune_type="COM")
        commune.procedures.create(
            doc_type=TypeDocument.PLU, collectivite_porteuse=commune
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
                "collectivite_code": "12345",
                "collectivite_type": "COM",
                "procedure_id": str(commune.procedures.first().id),
                "opposable": "False",
                "type_document": commune.procedures.first().type_document,
            }
        ]

    @pytest.mark.django_db
    def test_filtre_par_department(self, client: Client) -> None:
        commune_a = create_commune()
        commune_b = create_commune()

        commune_a.procedures.create(
            doc_type=TypeDocument.PLU, collectivite_porteuse=commune_a
        )
        commune_b.procedures.create(
            doc_type=TypeDocument.PLU, collectivite_porteuse=commune_b
        )

        response = client.get(
            "/api/perimetres", {"departement": commune_a.departement.code_insee}
        )
        reader = DictReader(response.content.decode().splitlines())
        assert len(list(reader)) == 1

    @pytest.mark.django_db
    def test_retourne_tout_sans_filtre_departement(self, client: Client) -> None:
        commune_a = create_commune()
        commune_b = create_commune()

        commune_a.procedures.create(
            doc_type=TypeDocument.PLU, collectivite_porteuse=commune_a
        )
        commune_b.procedures.create(
            doc_type=TypeDocument.PLU, collectivite_porteuse=commune_b
        )

        response = client.get("/api/perimetres")
        reader = DictReader(response.content.decode().splitlines())
        assert len(list(reader)) == 2

    @pytest.mark.django_db
    @pytest.mark.parametrize(
        ("avant", "opposable"),
        [
            ("", "True"),
            ("2023-01-01", "False"),
        ],
    )
    def test_ignore_event_apres(
        self, client: Client, avant: str, opposable: str
    ) -> None:
        commune = create_commune()
        procedure = commune.procedures.create(
            doc_type=TypeDocument.PLU, collectivite_porteuse=commune
        )

        procedure.event_set.create(
            type="Délibération d'approbation", date_evenement="2023-01-02"
        )

        response = client.get("/api/perimetres", {"avant": avant})
        reader = DictReader(response.content.decode().splitlines())
        assert [cp["opposable"] for cp in reader] == [opposable]


class TestAPICommunes:
    @pytest.mark.django_db
    def test_format_csv(
        self, client: Client, django_assert_num_queries: DjangoAssertNumQueries
    ) -> None:
        groupement = create_groupement()
        commune = create_commune()
        plan_en_cours = commune.procedures.create(
            doc_type=TypeDocument.PLU, collectivite_porteuse=groupement
        )
        plan_en_cours.event_set.create(type="Prescription", date_evenement="2024-12-01")
        plan_opposable = commune.procedures.create(
            doc_type=TypeDocument.PLU, collectivite_porteuse=groupement
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
        create_commune(intercommunalite=None)

        response = client.get("/api/communes")

        assert response.status_code == 200

        reader = DictReader(response.content.decode().splitlines())

        assert len(list(reader)) == 1

    @pytest.mark.django_db
    def test_filtre_par_department(self, client: Client) -> None:
        groupement = create_groupement()

        commune_a = create_commune()
        commune_b = create_commune()

        commune_a.procedures.create(
            doc_type=TypeDocument.PLU, collectivite_porteuse=groupement
        )
        commune_b.procedures.create(
            doc_type=TypeDocument.PLU, collectivite_porteuse=groupement
        )

        response = client.get(
            "/api/communes", {"departement": commune_a.departement.code_insee}
        )
        reader = DictReader(response.content.decode().splitlines())
        assert len(list(reader)) == 1

    @pytest.mark.django_db
    def test_retourne_tout_sans_filtre_departement(self, client: Client) -> None:
        groupement = create_groupement()
        commune_a = create_commune()
        commune_b = create_commune()

        commune_a.procedures.create(
            doc_type=TypeDocument.PLU, collectivite_porteuse=groupement
        )
        commune_b.procedures.create(
            doc_type=TypeDocument.PLU, collectivite_porteuse=groupement
        )

        response = client.get("/api/communes")
        reader = DictReader(response.content.decode().splitlines())
        assert len(list(reader)) == 2

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
        groupement = create_groupement()
        commune = create_commune()
        procedure = commune.procedures.create(
            doc_type=TypeDocument.PLU, collectivite_porteuse=groupement
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
            groupement = create_groupement()
            commune = create_commune()
            plan_en_cours = commune.procedures.create(
                doc_type=TypeDocument.PLU, collectivite_porteuse=groupement
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
    @pytest.mark.parametrize(
        (
            "nb_communes",
            "procedure_factory_params",
            "dict_attendu_dans_resultat",
        ),
        [
            pytest.param(
                3,
                {"statut": EventCategory.APPROUVE},
                {
                    "pa_nombre_communes": "3",
                    "pa_annee_approbation": "2024",
                    "pa_date_approbation": "2024-12-01",
                    "pa_scot_interdepartement": "False",
                },
                id="scot_approuve_plusieurs_communes",
            ),
            pytest.param(
                3,
                {"statut": EventCategory.PUBLICATION_PERIMETRE},
                {
                    "pc_nombre_communes": "3",
                    "pc_date_publication_perimetre": "2024-12-01",
                    "pc_scot_interdepartement": "False",
                },
                id="scot_en_cours_plusieurs_communes",
            ),
            pytest.param(
                0,
                {"statut": EventCategory.APPROUVE},
                {},
                id="scot_approuve_sans_commune",
            ),
            pytest.param(
                0,
                {"statut": EventCategory.PUBLICATION_PERIMETRE},
                {
                    "pc_nombre_communes": "0",
                    "pc_date_publication_perimetre": "2024-12-01",
                    "pc_scot_interdepartement": "False",
                },
                id="scot_en_cours_sans_commune",
            ),
        ],
    )
    def test_scot_cas_differents(
        self,
        client: Client,
        django_assert_num_queries: DjangoAssertNumQueries,
        nb_communes: int,
        procedure_factory_params: dict[str, EventCategory],
        dict_attendu_dans_resultat: dict[str, str],
    ) -> None:
        departement = create_departement()
        perimetre_initial = [
            create_commune(departement=departement) for _ in range(nb_communes)
        ]
        groupement = create_groupement(groupement_type=TypeCollectivite.CC)
        groupement.collectivites_adherentes.add(*perimetre_initial)
        ViewCommuneAdhesionsDeep._refresh_materialized_view()  # noqa: SLF001

        scot = create_procedure(
            collectivite_porteuse=groupement,
            doc_type=TypeDocument.SCOT,
            **dict(procedure_factory_params),
        )
        scot = Procedure.objects.with_events().get(pk=scot.pk)
        scot.perimetre.add(*groupement.communes_adherentes_deep.all())
        last_event = scot.event_set.last()
        last_event.date_evenement = "2024-12-01"
        last_event.save()

        with django_assert_num_queries(6 if nb_communes else 4):
            response = client.get(reverse("api_scots"))

        result = list(DictReader(response.content.decode().splitlines()))
        resultat_par_defaut = {
            "annee_cog": "2024",
            # Collectivité
            "scot_code_region": groupement.departement.region.code_insee,
            "scot_libelle_region": "",
            "scot_code_departement": groupement.departement.code_insee,
            "scot_lib_departement": "",
            "scot_codecollectivite": groupement.code_insee,
            "scot_code_type_collectivite": groupement.type.value,
            "scot_nom_collectivite": "",
            # Approuvée
            "pa_id": str(scot.id) if scot.statut == EventCategory.APPROUVE else "",
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
            "pc_id": str(scot.id)
            if scot.statut == EventCategory.PUBLICATION_PERIMETRE
            else "",
            "pc_nom_schema": "",
            "pc_noserie_procedure": "",
            "pc_proc_elaboration_revision": "",
            "pc_scot_interdepartement": "",
            "pc_date_publication_perimetre": "",
            "pc_date_prescription": "",
            "pc_date_arret_projet": "",
            "pc_nombre_communes": "",
        }
        expected_result = resultat_par_defaut | dict_attendu_dans_resultat
        assert result[0] == expected_result

    @pytest.mark.django_db
    def test_filtre_par_department(self, client: Client) -> None:
        groupement_a = create_groupement()
        groupement_b = create_groupement()

        procedure_a = groupement_a.procedure_set.create(doc_type=TypeDocument.SCOT)
        procedure_a.event_set.create(
            type="Publication périmètre", date_evenement="2024-12-01"
        )

        procedure_b = groupement_b.procedure_set.create(doc_type=TypeDocument.SCOT)
        procedure_b.event_set.create(
            type="Publication périmètre", date_evenement="2024-12-01"
        )

        response = client.get(
            reverse("api_scots"), {"departement": groupement_a.departement.code_insee}
        )
        reader = DictReader(response.content.decode().splitlines())
        assert len(list(reader)) == 1

    @pytest.mark.django_db
    def test_retourne_tout_sans_filtre_departement(self, client: Client) -> None:
        groupement_a = create_groupement()
        groupement_b = create_groupement()

        procedure_a = groupement_a.procedure_set.create(doc_type=TypeDocument.SCOT)
        procedure_a.event_set.create(
            type="Publication périmètre", date_evenement="2024-12-01"
        )

        procedure_b = groupement_b.procedure_set.create(doc_type=TypeDocument.SCOT)
        procedure_b.event_set.create(
            type="Publication périmètre", date_evenement="2024-12-01"
        )

        response = client.get(reverse("api_scots"))
        reader = DictReader(response.content.decode().splitlines())
        assert len(list(reader)) == 2

    @pytest.mark.django_db
    @pytest.mark.parametrize(
        ("avant", "champ_procedure_id"),
        [
            ("", "pa_id"),
            ("2023-01-01", "pc_id"),
        ],
    )
    def test_ignore_event_apres(
        self, client: Client, avant: str, champ_procedure_id: str
    ) -> None:
        groupement = create_groupement()
        commune = create_commune()
        procedure = groupement.procedure_set.create(doc_type=TypeDocument.SCOT)
        procedure.perimetre.add(commune)

        procedure.event_set.create(
            type="Publication périmètre", date_evenement="2022-12-01"
        )
        procedure.event_set.create(
            type="Délibération d'approbation", date_evenement="2024-01-01"
        )

        response = client.get(reverse("api_scots"), {"avant": avant})

        reader = DictReader(response.content.decode().splitlines())
        assert [collectivite[champ_procedure_id] for collectivite in reader] == [
            str(procedure.id)
        ]
