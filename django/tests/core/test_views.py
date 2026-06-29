import datetime
from csv import DictReader
from functools import partial
from itertools import product

import pytest
from django.test import Client
from django.urls import reverse
from pytest_django import DjangoAssertNumQueries

from docurba.core.models import (
    EVENT_TYPE_BY_EVENT_CATEGORY,
    EventCategory,
    Procedure,
    Topic,
    TypeCollectivite,
    TypeDocument,
)
from tests.core.factories import (
    CollectiviteFactory,
    CommuneFactory,
    EventFactory,
    ProcedureFactory,
)


@pytest.mark.parametrize(
    "view_name",
    ["api_perimetres", "api_scots", "api_communes"],
)
@pytest.mark.django_db
# NOTE(cms): this should be refactored when Syrupy will be part of the project.
def test_vaut_PLH_consolide(client: Client, view_name: str) -> None:  # noqa: N802
    collectivite = CollectiviteFactory()
    communes = CommuneFactory.create_batch(3)
    collectivite.adhesions.add(*communes)
    ProcedureFactory(
        with_perimetre=communes[1:],
        doc_type=TypeDocument.PLUIH,
        with_event=True,
        with_event__category=EventCategory.APPROUVE,
    )
    response = client.get(reverse(view_name))
    assert response.status_code == 200


class TestAPI:
    @pytest.mark.parametrize(
        ("invalid_avant", "reverse_view"),
        list(
            product(
                ("2023-1-01", "2023-02-30", "invalid-date", "2023/01/01"),
                (partial(reverse, "api_perimetres"), partial(reverse, "api_scots")),
            )
        ),
    )
    def test_parsing_avant(
        self, client: Client, invalid_avant: str, reverse_view: str
    ) -> None:
        response = client.get(reverse_view(), {"avant": invalid_avant})

        assert response.status_code == 400
        assert (
            response.content.decode()
            == "Le paramètre 'avant' doit être une date valide au format YYYY-MM-DD."
        )


@pytest.mark.django_db
class TestAPIPerimetres:
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
                reverse("api_perimetres"),
                {"departement": commune.departement.code_insee},
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
        response = client.get(reverse("api_perimetres"), filtre)
        reader = DictReader(response.content.decode().splitlines())
        assert len(list(reader)) == expected_lignes

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
            response = client.get(reverse("api_perimetres"), {"avant": avant})
        reader = DictReader(response.content.decode().splitlines())
        assert [cp["opposable"] for cp in reader] == [opposable]


@pytest.mark.django_db
class TestAPICommunes:
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
            response = client.get(reverse("api_communes"))

        assert response.status_code == 200
        assert response["content-type"] == "text/csv;charset=utf-8"

        reader = DictReader(response.content.decode().splitlines())

        communes = list(reader)
        assert len(communes) == 1
        assert communes[0]["pc_docurba_id"] == str(plan_en_cours.id)
        assert communes[0]["pa_docurba_id"] == str(plan_opposable.id)

    def test_commune_sans_intercommunalite_ne_crashe_pas(self, client: Client) -> None:
        """
        4 îles n'ont pas d'intercommunalité.

        https://fr.wikipedia.org/wiki/Catégorie:Commune_hors_intercommunalité_à_fiscalité_propre_en_France
        """
        CommuneFactory(intercommunalite=None)

        response = client.get(reverse("api_communes"))

        assert response.status_code == 200

        reader = DictReader(response.content.decode().splitlines())

        assert len(list(reader)) == 1

    @pytest.mark.parametrize(
        ("is_filtering", "expected_lignes"), [(False, 2), (True, 1)]
    )
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

        response = client.get(reverse("api_communes"), filtre)
        reader = DictReader(response.content.decode().splitlines())

        assert len(list(reader)) == expected_lignes

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

        response = client.get(reverse("api_communes"), {"avant": avant})

        reader = DictReader(response.content.decode().splitlines())
        assert [collectivite[champ_procedure_id] for collectivite in reader] == [
            str(procedure.id)
        ]

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
                response = client.get(reverse("api_communes"))

        reader = DictReader(response.content.decode().splitlines())
        assert [cp["pc_type_document"] for cp in reader] == ["PLU", "PLU"]

    @pytest.mark.parametrize(
        ("procedure_status", "expected_filled_key", "expected_empty_key"),
        [
            pytest.param(
                EventCategory.PUBLICATION_PERIMETRE,
                "pc_objets",
                "pa_objets",
                id="ongoing_procedure",
            ),
            pytest.param(
                EventCategory.APPROUVE,
                "pa_objets",
                "pc_objets",
                id="approved_procedure",
            ),
        ],
    )
    @pytest.mark.parametrize(
        ("procedure_topics_to_add", "expected_result"),
        [
            pytest.param("", "", id="no_topic"),
            pytest.param(["zan"], "Trajectoire ZAN", id="one_topic"),
            pytest.param(
                ["zan", "forest_fire"],
                "Feu de forêt,Trajectoire ZAN",
                id="several_topics",
            ),
        ],
    )
    def test_with_topics(
        self,
        procedure_status: EventCategory,
        expected_filled_key: str,
        expected_empty_key: str,
        procedure_topics_to_add: str,
        expected_result: str,
        client: Client,
        django_assert_num_queries: DjangoAssertNumQueries,
    ) -> None:
        procedure = ProcedureFactory(
            doc_type=TypeDocument.PLU,
            with_perimetre=[CommuneFactory()],
            collectivite_porteuse=CollectiviteFactory(),
            with_event=True,
            with_event__category=procedure_status,
        )
        if procedure_topics_to_add:
            topics = Topic.objects.filter(name__in=procedure_topics_to_add)
            procedure.topics.add(*topics)

        with django_assert_num_queries(4):
            response = client.get(reverse("api_communes"))

        results = list(DictReader(response.content.decode().splitlines()))
        assert results[0][expected_filled_key] == expected_result
        assert results[0][expected_empty_key] == ""

    @pytest.mark.parametrize(
        ("event_category", "expected_filled_key", "expected_empty_key"),
        [
            pytest.param(
                EventCategory.PUBLICATION_PERIMETRE,
                "pc_date_pac_comp",
                "pa_date_pac_comp",
                id="ongoing_procedure",
            ),
            pytest.param(
                EventCategory.APPROUVE,
                "pa_date_pac_comp",
                "pc_date_pac_comp",
                id="approved_procedure",
            ),
        ],
    )
    def test_date_pac_comp(
        self,
        event_category: EventCategory,
        expected_filled_key: str,
        expected_empty_key: str,
        client: Client,
        django_assert_num_queries: DjangoAssertNumQueries,
    ) -> None:
        perimetre = [CommuneFactory()]
        # Create an ongoing procedure.
        procedure = ProcedureFactory(
            doc_type=TypeDocument.PLU,
            with_perimetre=perimetre,
            collectivite_porteuse=CollectiviteFactory(),
            with_event=True,
            with_event__category=event_category,
            with_event__date_evenement=datetime.date(2025, 10, 10),
        )

        EventFactory(
            type=EVENT_TYPE_BY_EVENT_CATEGORY[procedure.doc_type][
                EventCategory.PORTER_A_CONNAISSANCE_COMPLEMENTAIRE
            ][0],
            date_evenement=datetime.date(2025, 11, 11),
            procedure=procedure,
        )
        with django_assert_num_queries(4):
            response = client.get(reverse("api_communes"))
        results = list(DictReader(response.content.decode().splitlines()))
        assert results[0][expected_filled_key] == "2025-11-11"
        assert results[0][expected_empty_key] == ""

    @pytest.mark.parametrize(
        ("event_category", "expected_filled_key", "expected_empty_key"),
        [
            pytest.param(
                EventCategory.PUBLICATION_PERIMETRE,
                "pc_date_pac",
                "pa_date_pac",
                id="ongoing_procedure",
            ),
            pytest.param(
                EventCategory.APPROUVE,
                "pa_date_pac",
                "pc_date_pac",
                id="approved_procedure",
            ),
        ],
    )
    def test_date_pac(
        self,
        event_category: EventCategory,
        expected_filled_key: str,
        expected_empty_key: str,
        client: Client,
        django_assert_num_queries: DjangoAssertNumQueries,
    ) -> None:
        perimetre = [CommuneFactory()]
        # Create an ongoing procedure.
        procedure = ProcedureFactory(
            doc_type=TypeDocument.PLU,
            with_perimetre=perimetre,
            collectivite_porteuse=CollectiviteFactory(),
            with_event=True,
            with_event__category=event_category,
            with_event__date_evenement=datetime.date(2025, 10, 10),
        )

        EventFactory(
            type=EVENT_TYPE_BY_EVENT_CATEGORY[procedure.doc_type][
                EventCategory.PORTER_A_CONNAISSANCE
            ][0],
            date_evenement=datetime.date(2025, 11, 11),
            procedure=procedure,
        )
        with django_assert_num_queries(4):
            response = client.get(reverse("api_communes"))
        results = list(DictReader(response.content.decode().splitlines()))
        assert results[0][expected_filled_key] == "2025-11-11"
        assert results[0][expected_empty_key] == ""


class TestAPIScots:
    @pytest.mark.django_db
    @pytest.mark.parametrize(
        (
            "nb_communes",
            "event_category",
            "dict_attendu_dans_resultat",
        ),
        [
            pytest.param(
                3,
                "Délibération d'approbation",
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
                "Publication de périmètre",
                {
                    "pc_nombre_communes": "3",
                    "pc_date_publication_perimetre": "2024-12-01",
                    "pc_scot_interdepartement": "False",
                    "pc_proc_elaboration_revision": "Élaboration",
                },
                id="scot_en_cours_plusieurs_communes",
            ),
            pytest.param(
                0,
                "Publication de périmètre",
                {
                    "pc_nombre_communes": "0",
                    "pc_date_publication_perimetre": "2024-12-01",
                    "pc_scot_interdepartement": "False",
                    "pc_proc_elaboration_revision": "Élaboration",
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
        event_category: dict[str, EventCategory],
        dict_attendu_dans_resultat: dict[str, str],
    ) -> None:
        perimetre_initial = CommuneFactory.create_batch(
            nb_communes, departement__code_insee="13"
        )
        collectivite_porteuse = CollectiviteFactory(
            type=TypeCollectivite.CC,
            with_members=True,
            with_members__list=perimetre_initial,
        )

        event = EventFactory(
            type=event_category,
            date_evenement="2024-12-01",
            procedure__doc_type=TypeDocument.SCOT,
            procedure__with_perimetre=perimetre_initial,
            procedure__collectivite_porteuse=collectivite_porteuse,
        )
        # .with_events() is required to call scot.statut
        scot = Procedure.objects.with_events().get(pk=event.procedure_id)

        with django_assert_num_queries(6 if nb_communes else 4):
            response = client.get(reverse("api_scots"))
        result = list(DictReader(response.content.decode().splitlines()))
        resultat_par_defaut = {
            "annee_cog": "2024",
            # Collectivité
            "scot_code_region": collectivite_porteuse.departement.region.code_insee,
            "scot_libelle_region": collectivite_porteuse.departement.region.nom,
            "scot_code_departement": collectivite_porteuse.departement.code_insee,
            "scot_lib_departement": collectivite_porteuse.departement.nom,
            "scot_codecollectivite": collectivite_porteuse.code_insee,
            "scot_code_type_collectivite": collectivite_porteuse.type.value,
            "scot_nom_collectivite": scot.collectivite_porteuse.nom,
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
            "pa_objets": "",
            # En cours
            "pc_id": "",
            "pc_nom_schema": "",
            "pc_noserie_procedure": "",
            "pc_proc_elaboration_revision": "",
            "pc_scot_interdepartement": "",
            "pc_date_publication_perimetre": "",
            "pc_date_prescription": "",
            "pc_date_arret_projet": "",
            "pc_nombre_communes": "",
            "pc_objets": "",
        }
        if scot.statut == EventCategory.APPROUVE:
            resultat_par_defaut = resultat_par_defaut | {
                "pa_id": str(scot.id),
                "pa_nom_schema": str(scot.name),
                "pa_noserie_procedure": "",
                "pa_scot_interdepartement": "",
                "pa_date_publication_perimetre": "",
                "pa_date_prescription": "",
                "pa_date_arret_projet": "",
                "pa_date_approbation": "",
                "pa_annee_approbation": "",
                "pa_date_fin_echeance": "",
                "pa_nombre_communes": "",
            }
        elif scot.statut == EventCategory.PUBLICATION_PERIMETRE:
            resultat_par_defaut = resultat_par_defaut | {
                "pc_id": str(scot.id),
                "pc_nom_schema": str(scot.name),
                "pc_noserie_procedure": "",
                "pc_proc_elaboration_revision": "Élaboration",
                "pc_scot_interdepartement": "False",
                "pc_date_publication_perimetre": str(event.date_evenement),
                "pc_date_prescription": "",
                "pc_date_arret_projet": "",
                "pc_nombre_communes": "",
            }
        expected_result = resultat_par_defaut | dict_attendu_dans_resultat
        assert result[0] == expected_result

    @pytest.mark.parametrize(
        ("procedure_status", "expected_filled_key", "expected_empty_key"),
        [
            pytest.param(
                EventCategory.PUBLICATION_PERIMETRE,
                "pc_objets",
                "pa_objets",
                id="ongoing_procedure",
            ),
            pytest.param(
                EventCategory.APPROUVE,
                "pa_objets",
                "pc_objets",
                id="approved_procedure",
            ),
        ],
    )
    @pytest.mark.parametrize(
        ("procedure_topics_to_add", "expected_result"),
        [
            pytest.param("", "", id="no_topic"),
            pytest.param(["zan"], "Trajectoire ZAN", id="one_topic"),
            pytest.param(
                ["zan", "forest_fire"],
                "Feu de forêt,Trajectoire ZAN",
                id="several_topics",
            ),
        ],
    )
    @pytest.mark.django_db
    def test_with_topics(
        self,
        procedure_status: EventCategory,
        expected_filled_key: str,
        expected_empty_key: str,
        procedure_topics_to_add: str,
        expected_result: str,
        client: Client,
        django_assert_num_queries: DjangoAssertNumQueries,
    ) -> None:
        procedure = ProcedureFactory(
            doc_type=TypeDocument.SCOT,
            with_perimetre=[CommuneFactory()],
            with_event=True,
            with_event__category=procedure_status,
        )

        if procedure_topics_to_add:
            topics = Topic.objects.filter(name__in=procedure_topics_to_add)
            procedure.topics.add(*topics)

        with django_assert_num_queries(6):
            response = client.get(reverse("api_scots"))

        results = list(DictReader(response.content.decode().splitlines()))
        assert results[0][expected_filled_key] == expected_result
        assert results[0][expected_empty_key] == ""

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
