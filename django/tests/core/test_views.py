from csv import DictReader
from itertools import product

import pytest
from django.test import Client
from django.urls import reverse
from pytest_django import DjangoAssertNumQueries

from core.models import TypeDocument, ViewCommuneAdhesionsDeep
from tests.factories import (
    create_commune,
    create_groupement,
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
    def test_format_csv(
        self, client: Client, django_assert_num_queries: DjangoAssertNumQueries
    ) -> None:
        groupement = create_groupement()
        scot_en_cours = groupement.procedure_set.create(doc_type=TypeDocument.SCOT)
        scot_en_cours.event_set.create(
            type="Publication périmètre", date_evenement="2024-12-01"
        )

        with django_assert_num_queries(4):
            response = client.get(reverse("api_scots"))

        assert response.status_code == 200
        assert response["content-type"] == "text/csv;charset=utf-8"

        reader = DictReader(response.content.decode().splitlines())

        assert list(reader) == [
            {
                "annee_cog": "2024",
                # Collectivité
                "scot_code_region": groupement.departement.region.code_insee,
                "scot_libelle_region": "",
                "scot_code_departement": groupement.departement.code_insee,
                "scot_lib_departement": "",
                "scot_codecollectivite": groupement.code_insee,
                "scot_code_type_collectivite": groupement.type,
                "scot_nom_collectivite": groupement.nom,
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
                "pc_id": str(scot_en_cours.id),
                "pc_nom_schema": "",
                "pc_noserie_procedure": "",
                "pc_proc_elaboration_revision": "",
                "pc_scot_interdepartement": "False",
                "pc_date_publication_perimetre": "2024-12-01",
                "pc_date_prescription": "",
                "pc_date_arret_projet": "",
                "pc_nombre_communes": "0",
            }
        ]

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


class TestPourNuxtCollectivite:
    @pytest.mark.django_db
    def test_commune_vide(
        self, client: Client, django_assert_num_queries: DjangoAssertNumQueries
    ) -> None:
        commune = create_commune()

        ViewCommuneAdhesionsDeep._refresh_materialized_view()  # noqa: SLF001

        with django_assert_num_queries(3):
            response = client.get(
                reverse("pour_nuxt_collectivite", args=[commune.code_insee_unique])
            )
        assert response.json() == {
            "collectivite": {
                "intitule": commune.nom,
                "code": commune.code_insee,
                "departementCode": commune.departement.code_insee,
                "departement": {
                    "code": commune.departement.code_insee,
                    "intitule": commune.departement.nom,
                },
                "region": {
                    "code": commune.departement.region.code_insee,
                    "intitule": commune.departement.region.nom,
                },
                "intercommunalite": {
                    "departementCode": commune.intercommunalite.departement.code_insee,
                    "intitule": commune.intercommunalite.nom,
                },
                "intercommunaliteCode": commune.intercommunalite.code_insee,
                "membres": [
                    {
                        "code": commune.code_insee,
                        "intitule": commune.nom,
                        "type": commune.type,
                    }
                ],
                "warn_commune_nouvelle": False,
            },
            "plans": [],
            "schemas": [],
        }

    @pytest.mark.django_db
    def test_404_collectivite_inconnue(self, client: Client) -> None:
        response = client.get(reverse("pour_nuxt_collectivite", args=["00000000"]))
        assert response.status_code == 404

    @pytest.mark.django_db
    def test_commune_sans_intercommunalite_ne_crashe_pas(
        self, client: Client, django_assert_num_queries: DjangoAssertNumQueries
    ) -> None:
        """
        4 îles n'ont pas d'intercommunalité.

        https://fr.wikipedia.org/wiki/Catégorie:Commune_hors_intercommunalité_à_fiscalité_propre_en_France
        """
        commune = create_commune(intercommunalite=None)

        ViewCommuneAdhesionsDeep._refresh_materialized_view()  # noqa: SLF001

        with django_assert_num_queries(3):
            response = client.get(
                reverse("pour_nuxt_collectivite", args=[commune.code_insee_unique])
            )
        assert response.json() == {
            "collectivite": {
                "intitule": commune.nom,
                "code": commune.code_insee,
                "departementCode": commune.departement.code_insee,
                "departement": {
                    "code": commune.departement.code_insee,
                    "intitule": commune.departement.nom,
                },
                "region": {
                    "code": commune.departement.region.code_insee,
                    "intitule": commune.departement.region.nom,
                },
                "membres": [
                    {
                        "code": commune.code_insee,
                        "intitule": commune.nom,
                        "type": commune.type,
                    }
                ],
                "warn_commune_nouvelle": False,
            },
            "plans": [],
            "schemas": [],
        }

    @pytest.mark.django_db
    def test_groupement_vide(
        self, client: Client, django_assert_num_queries: DjangoAssertNumQueries
    ) -> None:
        groupement = create_groupement()

        ViewCommuneAdhesionsDeep._refresh_materialized_view()  # noqa: SLF001

        with django_assert_num_queries(2):
            response = client.get(
                reverse("pour_nuxt_collectivite", args=[groupement.code_insee_unique])
            )
        assert response.json() == {
            "collectivite": {
                "intitule": groupement.nom,
                "code": groupement.code_insee,
                "departementCode": groupement.departement.code_insee,
                "departement": {
                    "code": groupement.departement.code_insee,
                    "intitule": groupement.departement.nom,
                },
                "region": {
                    "code": groupement.departement.region.code_insee,
                    "intitule": groupement.departement.region.nom,
                },
                "membres": [],
            },
            "plans": [],
            "schemas": [],
        }

    @pytest.mark.django_db
    def test_groupement_avec_membres(
        self, client: Client, django_assert_num_queries: DjangoAssertNumQueries
    ) -> None:
        groupement = create_groupement()
        commune_a = create_commune()
        commune_b = create_commune()
        groupement.collectivites_adherentes.add(commune_a, commune_b)

        ViewCommuneAdhesionsDeep._refresh_materialized_view()  # noqa: SLF001

        with django_assert_num_queries(3):
            response = client.get(
                reverse("pour_nuxt_collectivite", args=[groupement.code_insee_unique])
            )
        assert response.json() == {
            "collectivite": {
                "intitule": groupement.nom,
                "code": groupement.code_insee,
                "departementCode": groupement.departement.code_insee,
                "departement": {
                    "code": groupement.departement.code_insee,
                    "intitule": groupement.departement.nom,
                },
                "region": {
                    "code": groupement.departement.region.code_insee,
                    "intitule": groupement.departement.region.nom,
                },
                "membres": [
                    {
                        "code": commune_a.code_insee,
                        "intitule": commune_a.nom,
                        "type": commune_a.type,
                    },
                    {
                        "code": commune_b.code_insee,
                        "intitule": commune_b.nom,
                        "type": commune_b.type,
                    },
                ],
            },
            "plans": [],
            "schemas": [],
        }

    @pytest.mark.django_db
    def test_avec_principales(
        self, client: Client, django_assert_num_queries: DjangoAssertNumQueries
    ) -> None:
        commune = create_commune()
        plan = commune.procedures.create(
            collectivite_porteuse=commune, doc_type=TypeDocument.PLU, type="Elaboration"
        )
        scot = commune.procedures.create(
            collectivite_porteuse=commune, doc_type=TypeDocument.SCOT, type="Révision"
        )

        ViewCommuneAdhesionsDeep._refresh_materialized_view()  # noqa: SLF001

        with django_assert_num_queries(8):
            response = client.get(
                reverse("pour_nuxt_collectivite", args=[commune.code_insee_unique])
            )
        assert response.json()["plans"] == [
            {
                "id": str(plan.id),
                "from_sudocuh": None,
                "name": "Elaboration PLU " + commune.nom,
                "status": "en cours",
                "type": plan.type,
                "commentaire": None,
                "procedures_perimetres": [
                    {
                        "intitule": commune.nom,
                        "code": commune.code_insee,
                        "collectivite_type": commune.type,
                    }
                ],
                "procSecs": [],
            }
        ]
        assert response.json()["schemas"] == [
            {
                "id": str(scot.id),
                "from_sudocuh": None,
                "name": "Révision SCOT " + commune.nom,
                "status": "en cours",
                "type": scot.type,
                "commentaire": None,
                "procedures_perimetres": [
                    {
                        "intitule": commune.nom,
                        "code": commune.code_insee,
                        "collectivite_type": commune.type,
                    }
                ],
                "procSecs": [],
            }
        ]

    @pytest.mark.django_db
    def test_avec_secondaires(
        self, client: Client, django_assert_num_queries: DjangoAssertNumQueries
    ) -> None:
        commune = create_commune()

        plan_principal = commune.procedures.create(
            collectivite_porteuse=commune, doc_type=TypeDocument.PLU, type="Elaboration"
        )
        plan_secondaire = commune.procedures.create(
            collectivite_porteuse=commune,
            doc_type=TypeDocument.PLU,
            type="Modification",
            parente=plan_principal,
        )

        scot_principal = commune.procedures.create(
            collectivite_porteuse=commune, doc_type=TypeDocument.SCOT, type="Révision"
        )
        scot_secondaire = commune.procedures.create(
            collectivite_porteuse=commune,
            doc_type=TypeDocument.SCOT,
            type="Modification",
            parente=scot_principal,
        )

        ViewCommuneAdhesionsDeep._refresh_materialized_view()  # noqa: SLF001

        with django_assert_num_queries(9):
            response = client.get(
                reverse("pour_nuxt_collectivite", args=[commune.code_insee_unique])
            )
        assert response.json()["plans"] == [
            {
                "id": str(plan_principal.id),
                "from_sudocuh": None,
                "name": "Elaboration PLU " + commune.nom,
                "status": "en cours",
                "type": plan_principal.type,
                "commentaire": None,
                "procedures_perimetres": [
                    {
                        "intitule": commune.nom,
                        "code": commune.code_insee,
                        "collectivite_type": commune.type,
                    }
                ],
                "procSecs": [
                    {
                        "id": str(plan_secondaire.id),
                        "from_sudocuh": None,
                        "name": "Modification PLU " + commune.nom,
                        "status": "en cours",
                        "type": plan_secondaire.type,
                        "commentaire": None,
                        "procedures_perimetres": [
                            {
                                "intitule": commune.nom,
                                "code": commune.code_insee,
                                "collectivite_type": commune.type,
                            }
                        ],
                    }
                ],
            }
        ]
        assert response.json()["schemas"] == [
            {
                "id": str(scot_principal.id),
                "from_sudocuh": None,
                "name": "Révision SCOT " + commune.nom,
                "status": "en cours",
                "type": scot_principal.type,
                "commentaire": None,
                "procedures_perimetres": [
                    {
                        "intitule": commune.nom,
                        "code": commune.code_insee,
                        "collectivite_type": commune.type,
                    }
                ],
                "procSecs": [
                    {
                        "id": str(scot_secondaire.id),
                        "from_sudocuh": None,
                        "name": "Modification SCOT " + commune.nom,
                        "status": "en cours",
                        "type": scot_secondaire.type,
                        "commentaire": None,
                        "procedures_perimetres": [
                            {
                                "intitule": commune.nom,
                                "code": commune.code_insee,
                                "collectivite_type": commune.type,
                            }
                        ],
                    }
                ],
            }
        ]

    @pytest.mark.django_db
    def test_nb_queries_commune(
        self, client: Client, django_assert_num_queries: DjangoAssertNumQueries
    ) -> None:
        commune = create_commune()
        ViewCommuneAdhesionsDeep._refresh_materialized_view()  # noqa: SLF001

        for _ in range(2):
            plan_principal = commune.procedures.create(
                collectivite_porteuse=commune,
                doc_type=TypeDocument.PLU,
                type="Elaboration",
            )
            _plan_secondaire = commune.procedures.create(
                collectivite_porteuse=commune,
                doc_type=TypeDocument.PLU,
                type="Modification",
                parente=plan_principal,
            )

            scot_principal = commune.procedures.create(
                collectivite_porteuse=commune,
                doc_type=TypeDocument.SCOT,
                type="Révision",
            )
            _scot_secondaire = commune.procedures.create(
                collectivite_porteuse=commune,
                doc_type=TypeDocument.SCOT,
                type="Modification",
                parente=scot_principal,
            )

            with django_assert_num_queries(9):
                response = client.get(
                    reverse("pour_nuxt_collectivite", args=[commune.code_insee_unique])
                )

        assert len(response.json()["plans"]) == 2
        assert len(response.json()["schemas"]) == 2

    @pytest.mark.django_db
    def test_nb_queries_groupement(
        self, client: Client, django_assert_num_queries: DjangoAssertNumQueries
    ) -> None:
        groupement = create_groupement()
        commune_a = create_commune()
        commune_b = create_commune()
        groupement.collectivites_adherentes.add(commune_a, commune_b)

        ViewCommuneAdhesionsDeep._refresh_materialized_view()  # noqa: SLF001

        for _ in range(2):
            plan_principal = groupement.procedure_set.create(
                doc_type=TypeDocument.PLU,
                type="Elaboration",
            )
            plan_principal.perimetre.add(commune_a, commune_b)
            plan_principal.event_set.create(
                type="Délibération d'approbation", date_evenement="2023-01-02"
            )
            plan_secondaire = groupement.procedure_set.create(
                doc_type=TypeDocument.PLU,
                type="Modification",
                parente=plan_principal,
            )
            plan_secondaire.perimetre.add(commune_a, commune_b)

            scot_principal = groupement.procedure_set.create(
                doc_type=TypeDocument.SCOT,
                type="Révision",
            )
            scot_principal.perimetre.add(commune_a, commune_b)
            scot_principal.event_set.create(
                type="Délibération d'approbation", date_evenement="2023-01-02"
            )
            scot_secondaire = groupement.procedure_set.create(
                doc_type=TypeDocument.SCOT,
                type="Modification",
                parente=scot_principal,
            )
            scot_secondaire.perimetre.add(commune_a, commune_b)

            with django_assert_num_queries(9):
                response = client.get(
                    reverse(
                        "pour_nuxt_collectivite", args=[groupement.code_insee_unique]
                    )
                )

        assert len(response.json()["plans"]) == 2
        assert len(response.json()["schemas"]) == 2
