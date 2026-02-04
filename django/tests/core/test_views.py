from csv import DictReader
from itertools import product
from typing import Any

import pytest
from django.test import Client
from django.urls import reverse
from pytest_django import DjangoAssertNumQueries
from sentry_sdk.profiler import has_profiling_enabled

from core.models import (
    Collectivite,
    Commune,
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


@pytest.mark.django_db
class TestAPICommunes:
    def _default_fields(
        self, commune: Commune
    ) -> dict[str, Any]:  # -> dict[str, Any]:# -> dict[str, Any]:
        # TODO: make it static.
        fields = {
            "annee_cog": "2024",
            "code_insee": commune.code_insee_unique,
            "com_nom": commune.nom,
            "com_code_departement": commune.departement.code_insee,
            "com_nom_departement": commune.departement.nom,
            "com_code_region": commune.departement.region.code_insee,
            "com_nom_region": commune.departement.region.nom,
            "com_nouvelle": commune.is_nouvelle,
            "collectivite_porteuse": commune.collectivite_porteuse.code_insee,
            "cp_type": commune.collectivite_porteuse.type,
            "cp_code_region": commune.collectivite_porteuse.departement.region.code_insee,
            "cp_lib_region": commune.collectivite_porteuse.departement.region.nom,
            "cp_code_departement": commune.collectivite_porteuse.departement.code_insee,
            "cp_nom_departement": commune.collectivite_porteuse.departement.nom,
            "cp_nom": commune.collectivite_porteuse.nom,
            "plan_code_etat_simplifie": commune.code_etat_simplifie,
            "plan_libelle_code_etat_simplifie": commune.libelle_code_etat_simplifie,
            "plan_code_etat_complet": commune.code_etat_complet,
            "plan_libelle_code_etat_complet": commune.libelle_code_etat_complet,
        }
        return {key: str(value) for key, value in fields.items()}

    def _intercommunalite_fields(
        self, intercommunalite: Collectivite
    ) -> dict[str, str]:
        # TODO: make it static.
        fields = {
            "epci_reg": intercommunalite.departement.region.code_insee,
            "epci_region": intercommunalite.departement.region.nom,
            "epci_dept": intercommunalite.departement.code_insee,
            "epci_departement": intercommunalite.departement.nom,
            "epci_type": intercommunalite.type,
            "epci_nom": intercommunalite.nom,
            "epci_siren": intercommunalite.code_insee,
        }
        return {key: str(value) for key, value in fields.items()}

    def _plan_en_cours_fields(self, procedure: Procedure) -> dict[str, str]:
        # TODO: make it static.
        fields = {
            "pc_docurba_id": procedure.id,
            "pc_num_procedure_sudocuh": "",
            "pc_nb_communes": procedure.perimetre__count,
            "pc_type_document": procedure.type_document,
            "pc_type_procedure": "",
            "pc_date_prescription": "",
            "pc_date_arret_projet": "",
            "pc_date_pac": "",
            "pc_date_pac_comp": "",
            "pc_plui_valant_scot": "",
            "pc_pluih": procedure.vaut_PLH_consolide,
            "pc_sectoriel": procedure.is_sectoriel_consolide,
            "pc_pdu_tient_lieu": procedure.vaut_PDM_consolide,
            "pc_pdu_obligatoire": "",
            "pc_nom_sst": "",
            "pc_cout_sst_ht": "",
            "pc_cout_sst_ttc": "",
        }
        return {key: str(value) for key, value in fields.items()}

    def _plan_opposable_fields(self, procedure: Procedure) -> dict[str, str]:
        # TODO: make it static.
        fields = {
            "pa_docurba_id": procedure.id,
            "pa_num_procedure_sudocuh": "",
            "pa_nb_communes": procedure.perimetre__count,
            "pa_type_document": procedure.type_document,
            "pa_type_procedure": "",
            "pa_sectoriel": procedure.is_sectoriel_consolide,
            "pa_date_prescription": "",
            "pa_date_arret_projet": "",
            "pa_date_pac": "",
            "pa_date_pac_comp": "",
            "pa_date_approbation": "2024-12-01",
            "pa_annee_prescription": "",
            "pa_annee_approbation": "2024",
            "pa_date_executoire": "",
            "pa_delai_approbation": "",
            "pa_plui_valant_scot": "",
            "pa_pluih": procedure.vaut_PLH_consolide,
            "pa_pdu_tient_lieu": procedure.vaut_PDM_consolide,
            "pa_pdu_obligatoire": "",
            "pa_nom_sst": "",
            "pa_cout_sst_ht": "",
            "pa_cout_sst_ttc": "",
        }
        return {key: str(value) for key, value in fields.items()}

    @pytest.mark.parametrize(
        ("is_commune", "dict_attendu_dans_resultat"),
        [
            pytest.param(
                True, {"cp_code_insee": "75056", "cp_siren": ""}, id="is_commune"
            ),
            pytest.param(
                False,
                {"cp_code_insee": "", "cp_siren": "12345678"},
                id="is_not_commune",
            ),
        ],
    )
    def test_commune_collectivite_porteuse_is_commune(
        self,
        client: Client,
        django_assert_num_queries: DjangoAssertNumQueries,
        is_commune: bool,  # noqa: FBT001
        dict_attendu_dans_resultat: dict[str, str],
    ) -> None:
        if is_commune:
            collectivite_porteuse = create_groupement(
                groupement_type=TypeCollectivite.COM, code_insee="75056"
            )
        else:
            collectivite_porteuse = create_groupement(
                groupement_type=TypeCollectivite.CC, code_insee="12345678"
            )
        commune = create_commune()
        procedure = create_procedure(
            perimetre=[commune],
            collectivite_porteuse=collectivite_porteuse,
            statut=EventCategory.APPROUVE,
        )
        # Mandatory today.
        commune = Commune.objects.with_procedures_principales().get(pk=commune.pk)
        procedure = (
            Procedure.objects.with_communes_counts().with_events().get(pk=procedure.pk)
        )
        assert procedure == commune.plan_opposable

        with django_assert_num_queries(4):
            response = client.get(reverse("api_communes"))

        result = list(DictReader(response.content.decode().splitlines()))
        expected_result = (
            self._default_fields(commune=commune) | dict_attendu_dans_resultat
        )
        # Delete keys tested separately.
        for key in self._intercommunalite_fields(intercommunalite=create_groupement()):
            del result[0][key]
        for key in self._plan_en_cours_fields(procedure=procedure):
            del result[0][key]
        for key in self._plan_opposable_fields(procedure=procedure):
            del result[0][key]
        assert result[0] == expected_result

    @pytest.mark.parametrize("is_member_of_interco", [True, False])
    def test_commune_member_of_intercommunalite(
        self,
        client: Client,
        django_assert_num_queries: DjangoAssertNumQueries,
        is_member_of_interco: bool,
    ) -> None:
        collectivite_porteuse = create_groupement(
            groupement_type=TypeCollectivite.CC, code_insee="12345678"
        )
        intercommunalite = None
        if is_member_of_interco:
            intercommunalite = create_groupement()
        commune = create_commune(intercommunalite=intercommunalite)
        procedure = create_procedure(
            perimetre=[commune],
            collectivite_porteuse=collectivite_porteuse,
            statut=EventCategory.APPROUVE,
        )
        # Mandatory today.
        commune = Commune.objects.with_procedures_principales().get(pk=commune.pk)
        procedure = (
            Procedure.objects.with_communes_counts().with_events().get(pk=procedure.pk)
        )
        assert procedure == commune.plan_opposable

        with django_assert_num_queries(4):
            response = client.get(reverse("api_communes"))

        result = list(DictReader(response.content.decode().splitlines()))
        expected_fields = {
            "epci_departement": "",
            "epci_dept": "",
            "epci_nom": "",
            "epci_reg": "",
            "epci_region": "",
            "epci_siren": "",
            "epci_type": "",
        }
        if is_member_of_interco:
            expected_fields = self._intercommunalite_fields(
                intercommunalite=intercommunalite
            )
        expected_result = self._default_fields(commune=commune) | expected_fields

        # Delete keys tested separately.
        for key in ["cp_code_insee", "cp_siren"]:
            del result[0][key]
        for key in self._plan_en_cours_fields(procedure=procedure):
            del result[0][key]
        for key in self._plan_opposable_fields(procedure=procedure):
            del result[0][key]
        assert result[0] == expected_result

    @pytest.mark.parametrize("has_plan_en_cours", [True, False])
    def test_commune_with_plan_en_cours(
        self,
        client: Client,
        django_assert_num_queries: DjangoAssertNumQueries,
        has_plan_en_cours: bool,
    ) -> None:
        collectivite_porteuse = create_groupement(
            groupement_type=TypeCollectivite.CC, code_insee="12345678"
        )
        commune = create_commune()
        statut = (
            EventCategory.PUBLICATION_PERIMETRE
            if has_plan_en_cours
            else EventCategory.APPROUVE
        )
        procedure = create_procedure(
            perimetre=[commune],
            collectivite_porteuse=collectivite_porteuse,
            statut=statut,
        )
        # Mandatory today.
        commune = Commune.objects.with_procedures_principales().get(pk=commune.pk)
        procedure = (
            Procedure.objects.with_communes_counts().with_events().get(pk=procedure.pk)
        )

        with django_assert_num_queries(4):
            response = client.get(reverse("api_communes"))

        result = list(DictReader(response.content.decode().splitlines()))
        expected_fields = {
            "pc_docurba_id": "",
            "pc_num_procedure_sudocuh": "",
            "pc_nb_communes": "",
            "pc_type_document": "",
            "pc_type_procedure": "",
            "pc_date_prescription": "",
            "pc_date_arret_projet": "",
            "pc_date_pac": "",
            "pc_date_pac_comp": "",
            "pc_plui_valant_scot": "",
            "pc_pluih": "",
            "pc_sectoriel": "",
            "pc_pdu_tient_lieu": "",
            "pc_pdu_obligatoire": "",
            "pc_nom_sst": "",
            "pc_cout_sst_ht": "",
            "pc_cout_sst_ttc": "",
        }
        if has_plan_en_cours:
            expected_fields = self._plan_en_cours_fields(procedure=procedure)
        expected_result = self._default_fields(commune=commune) | expected_fields

        # Delete keys tested separately.
        for key in ["cp_code_insee", "cp_siren"]:
            del result[0][key]
        for key in self._intercommunalite_fields(intercommunalite=create_groupement()):
            del result[0][key]
        for key in self._plan_opposable_fields(procedure=procedure):
            del result[0][key]
        assert result[0] == expected_result

    @pytest.mark.parametrize("has_plan_approuve", [True, False])
    def test_commune_with_plan_approuve(
        self,
        client: Client,
        django_assert_num_queries: DjangoAssertNumQueries,
        has_plan_approuve: bool,
    ) -> None:
        collectivite_porteuse = create_groupement(
            groupement_type=TypeCollectivite.CC, code_insee="12345678"
        )
        commune = create_commune()
        statut = (
            EventCategory.APPROUVE
            if has_plan_approuve
            else EventCategory.PUBLICATION_PERIMETRE
        )
        procedure = create_procedure(
            perimetre=[commune],
            collectivite_porteuse=collectivite_porteuse,
            statut=statut,
        )
        # Mandatory today.
        commune = Commune.objects.with_procedures_principales().get(pk=commune.pk)
        procedure = (
            Procedure.objects.with_communes_counts().with_events().get(pk=procedure.pk)
        )

        with django_assert_num_queries(4):
            response = client.get(reverse("api_communes"))

        result = list(DictReader(response.content.decode().splitlines()))
        expected_fields = {
            "pa_docurba_id": "",
            "pa_num_procedure_sudocuh": "",
            "pa_nb_communes": "",
            "pa_type_document": "",
            "pa_type_procedure": "",
            "pa_sectoriel": "",
            "pa_date_prescription": "",
            "pa_date_arret_projet": "",
            "pa_date_pac": "",
            "pa_date_pac_comp": "",
            "pa_date_approbation": "",
            "pa_annee_prescription": "",
            "pa_annee_approbation": "",
            "pa_date_executoire": "",
            "pa_delai_approbation": "",
            "pa_plui_valant_scot": "",
            "pa_pluih": "",
            "pa_pdu_tient_lieu": "",
            "pa_pdu_obligatoire": "",
            "pa_nom_sst": "",
            "pa_cout_sst_ht": "",
            "pa_cout_sst_ttc": "",
        }
        if has_plan_approuve:
            expected_fields = self._plan_opposable_fields(procedure=procedure)
        expected_result = self._default_fields(commune=commune) | expected_fields

        # Delete keys tested separately.
        for key in ["cp_code_insee", "cp_siren"]:
            del result[0][key]
        for key in self._intercommunalite_fields(intercommunalite=create_groupement()):
            del result[0][key]
        for key in self._plan_en_cours_fields(procedure=procedure):
            del result[0][key]
        assert result[0] == expected_result

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
