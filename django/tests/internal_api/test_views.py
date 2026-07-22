from urllib.parse import urlencode

import pytest
from django.urls import reverse
from pytest_django.asserts import assertNumQueries
from rest_framework.test import APIClient
from syrupy import SnapshotAssertion

from docurba.core.enums import EventScope, ProcedureType
from docurba.core.models import (
    EventType,
    Procedure,
    Topic,
    TypeCollectivite,
    TypeDocument,
)

# Refactor
from tests.conftest import SupabaseApiClient
from tests.core.factories import (
    CollectiviteFactory,
    CommuneFactory,
    EventTypeFactory,
    ProcedureFactory,
)

BASE_QUERIES_COUNT = 1  # Count made by DRF for the pagination.


@pytest.mark.django_db
class TestCollectivitesAPI:
    @pytest.mark.parametrize(
        ("query_params", "expected_num_queries"),
        [
            pytest.param(
                {},
                BASE_QUERIES_COUNT + 1,
                id="no_filter",
            ),
            pytest.param(
                {"departement": "84"},
                BASE_QUERIES_COUNT + 2,
                id="one_department",
            ),
            pytest.param(
                {"departement": ["84", "13"]},
                BASE_QUERIES_COUNT + 2,
                id="many_departments",
            ),
            pytest.param(
                {"region": "93", "type": "CC"},
                BASE_QUERIES_COUNT + 2,
                id="region_and_type",
            ),
            pytest.param(
                {"region": "93"},
                BASE_QUERIES_COUNT + 2,
                id="region",
            ),
            pytest.param(
                {"type": ["CC", "SMO"]},
                BASE_QUERIES_COUNT + 1,
                id="many_types",
            ),
        ],
    )
    def test_list_filters(
        self,
        api_client: APIClient,
        expected_num_queries: int,
        query_params: str,
        snapshot: SnapshotAssertion,
    ) -> None:
        CollectiviteFactory(
            siren="987654321",
            type=TypeCollectivite.CC,
            departement__code_insee="13",
            nom="Groupement 1",
        )
        CollectiviteFactory(
            siren="123456789",
            type=TypeCollectivite.SIVOM,
            departement__code_insee="84",
            nom="Groupement 2",
        )
        CollectiviteFactory(
            siren="132435465",
            type=TypeCollectivite.SMO,
            departement__code_insee="30",
            nom="Groupement 3",
        )

        url = f"{reverse('internal_api:collectivites-list')}?{urlencode(query_params, doseq=True)}"
        with assertNumQueries(expected_num_queries):
            response = api_client.get(url, format="json")

        assert response.status_code == 200
        assert response.json()["results"] == snapshot()

    @pytest.mark.parametrize(
        ("query_params"),
        [
            pytest.param(
                {"without_communes": "true"},
                id="without_communes",
            ),
            pytest.param(
                {"without_communes": "false"},
                id="with_communes",
            ),
            pytest.param(
                {},
                id="default_value",
            ),
        ],
    )
    def test_without_communes_from_list(
        self, api_client: APIClient, query_params: dict, snapshot: SnapshotAssertion
    ) -> None:
        CollectiviteFactory(
            type=TypeCollectivite.COM,
            departement__code_insee="13",
            nom="Groupement 1",
            siren="123456789",
        )
        CollectiviteFactory(
            type=TypeCollectivite.CC,
            departement__code_insee="13",
            nom="Groupement 2",
            siren="123456778",
        )
        url = f"{reverse('internal_api:collectivites-list')}?{urlencode(query_params)}"
        with assertNumQueries(BASE_QUERIES_COUNT + 1):
            response = api_client.get(url, format="json")

        assert response.status_code == 200
        assert response.json()["results"] == snapshot()

    @pytest.mark.parametrize(
        ("query_params"),
        [
            pytest.param(
                {"avec_membres_niveaux_inferieurs": "true"},
                id="avec_membres_niveaux_inferieurs",
            ),
            pytest.param(
                {"avec_groupements_niveaux_superieurs": "true"},
                id="avec_groupements_niveaux_superieurs",
            ),
            pytest.param(
                {"avec_groupements": "true"},
                id="avec_groupements",
            ),
            pytest.param(
                {"avec_membres": "true"},
                id="avec_membres",
            ),
        ],
    )
    def test_with_groupements_and_members(
        self,
        api_client: APIClient,
        query_params: dict,
        snapshot: SnapshotAssertion,
    ) -> None:
        CollectiviteFactory(
            for_snapshot=True,
            with_flat_members=True,
            with_flat_members__for_snapshot=True,
            departement__code_insee="30",
        )
        url = f"{reverse('internal_api:collectivites-list')}?{urlencode(query_params)}"
        with assertNumQueries(3):
            response = api_client.get(url, format="json")

        assert response.status_code == 200
        assert response.json()["results"] == snapshot()

    @pytest.mark.parametrize(
        ("query_params"),
        [
            pytest.param(
                {"competence": "schema"},
                id="competence_schema",
            ),
            pytest.param(
                {"competence": "plan"},
                id="competence_plan",
            ),
            pytest.param(
                {},
                id="sans_competence",
            ),
            pytest.param(
                {"competence": ["plan", "schema"]},
                id="competence_schema_ou_plan",
            ),
        ],
    )
    def test_competences_list(
        self, api_client: APIClient, query_params: dict, snapshot: SnapshotAssertion
    ) -> None:
        CollectiviteFactory(
            type=TypeCollectivite.CC,
            departement__code_insee="13",
            nom="Groupement 1",
            siren="123456789",
            competence_schema=True,
        )
        CollectiviteFactory(
            type=TypeCollectivite.CC,
            departement__code_insee="13",
            nom="Groupement 2",
            siren="123456778",
            competence_plan=True,
        )
        CollectiviteFactory(
            type=TypeCollectivite.CC,
            departement__code_insee="30",
            nom="Groupement 3",
            siren="987654321",
            competence_plan=True,
            competence_schema=True,
        )
        url = f"{reverse('internal_api:collectivites-list')}?{urlencode(query_params, doseq=True)}"
        with assertNumQueries(BASE_QUERIES_COUNT + 1):
            response = api_client.get(url, format="json")

        assert response.status_code == 200
        assert response.json()["results"] == snapshot()

    def test_detail(self, api_client: APIClient) -> None:
        groupement = CollectiviteFactory(
            siren="987654321",
            type=TypeCollectivite.CC,
            departement__code_insee="13",
            nom="Groupement 1",
        )

        url = reverse("internal_api:collectivites-detail", args=[groupement.pk])
        with assertNumQueries(1):
            response = api_client.get(url, format="json")

        assert response.status_code == 200
        assert response.json() == {
            "codeInsee": "",
            "siren": "987654321",
            "type": "CC",
            "intitule": "Groupement 1",
            "regionCode": "93",
            "departementCode": "13",
            "intercommunaliteCode": "",
        }

    def test_intercommunalite_code(self, api_client: APIClient) -> None:
        intercommunalite = CollectiviteFactory(
            type=TypeCollectivite.CC, siren="253000020"
        )
        commune = CommuneFactory(
            code_insee="30840",
            type=TypeCollectivite.COM,
            departement__code_insee="30",
            nom="Commune 1",
            intercommunalite=intercommunalite,
        )
        url = reverse("internal_api:collectivites-detail", args=[commune.pk])
        with assertNumQueries(1):
            response = api_client.get(url, format="json")

        assert response.status_code == 200
        assert response.json() == {
            "codeInsee": "30840",
            "siren": "",
            "type": "COM",
            "intitule": "Commune 1",
            "regionCode": "76",
            "departementCode": "30",
            "intercommunaliteCode": "253000020",
        }


@pytest.mark.django_db
class TestCommunesAPI:
    @pytest.mark.parametrize(
        ("query_params", "expected_num_queries"),
        [
            pytest.param(
                {},
                BASE_QUERIES_COUNT + 1,
                id="no_filter",
            ),
            pytest.param(
                {"departement": "13"},
                BASE_QUERIES_COUNT + 2,
                id="one_department",
            ),
            pytest.param(
                {"departement": ["30", "13"]},
                BASE_QUERIES_COUNT + 2,
                id="many_departments",
            ),
            pytest.param(
                {"region": "93", "type": "COMD"},
                BASE_QUERIES_COUNT + 2,
                id="region_and_type",
            ),
            pytest.param(
                {"region": "93"},
                BASE_QUERIES_COUNT + 2,
                id="region",
            ),
            pytest.param(
                {"type": ["COM"]},
                BASE_QUERIES_COUNT + 1,
                id="type_commune",
            ),
        ],
    )
    def test_list(
        self,
        api_client: APIClient,
        expected_num_queries: int,
        query_params: dict,
        snapshot: SnapshotAssertion,
    ) -> None:
        CommuneFactory(
            code_insee="13150",
            type=TypeCollectivite.COM,
            departement__code_insee="13",
            nom="Commune 1",
        )
        CommuneFactory(
            code_insee="30000",
            type=TypeCollectivite.COM,
            departement__code_insee="30",
            nom="Commune 2",
        )
        CommuneFactory(
            code_insee="84000",
            type=TypeCollectivite.COMD,
            departement__code_insee="84",
            nom="Commune 3",
        )
        url = f"{reverse('internal_api:communes-list')}?{urlencode(query_params, doseq=True)}"

        with assertNumQueries(expected_num_queries):
            response = api_client.get(url, format="json")

        assert response.status_code == 200
        assert response.json()["results"] == snapshot()

    def test_detail(self, api_client: APIClient) -> None:
        commune = CommuneFactory(
            code_insee="30840",
            type=TypeCollectivite.COM,
            departement__code_insee="13",
            nom="Groupement 1",
        )

        url = reverse("internal_api:communes-detail", args=[commune.pk])
        with assertNumQueries(1):
            response = api_client.get(url, format="json")

        assert response.status_code == 200
        assert response.json() == {
            "code": "30840",
            "type": "COM",
            "intitule": "Groupement 1",
            "regionCode": "93",
            "departementCode": "13",
            "intercommunaliteCode": "",
        }

    def test_intercommunalite_code(self, api_client: APIClient) -> None:
        intercommunalite = CollectiviteFactory(
            type=TypeCollectivite.CC, siren="253000020"
        )
        commune = CommuneFactory(
            code_insee="30840",
            type=TypeCollectivite.COM,
            departement__code_insee="13",
            nom="Groupement 1",
            intercommunalite=intercommunalite,
        )

        url = reverse("internal_api:communes-detail", args=[commune.pk])
        with assertNumQueries(1):
            response = api_client.get(url, format="json")

        assert response.status_code == 200
        assert response.json() == {
            "code": "30840",
            "type": "COM",
            "intitule": "Groupement 1",
            "regionCode": "93",
            "departementCode": "13",
            "intercommunaliteCode": "253000020",
        }


@pytest.mark.django_db
class TestEventTypesAPI:
    @pytest.mark.parametrize(
        ("query_params", "expected"),
        [
            pytest.param(
                {},
                [
                    {
                        "id": "00000000-0000-0000-1111-000000000000",
                        "documentType": "CC",
                        "name": "Déroulement des plans de test",
                        "scopeList": [],
                        "scopeSugg": [],
                        "isStructuring": False,
                        "sudocuhName": "",
                    },
                    {
                        "id": "00000000-0000-0000-2222-000000000000",
                        "documentType": "PLU",
                        "name": "Echec du déroulement des plans de test",
                        "scopeList": [],
                        "scopeSugg": [],
                        "isStructuring": False,
                        "sudocuhName": "",
                    },
                    {
                        "id": "00000000-0000-0000-3333-000000000000",
                        "documentType": "CC",
                        "name": "Succès du déroulement des plans de test",
                        "scopeList": ["pp"],
                        "scopeSugg": ["pp", "ppi"],
                        "isStructuring": False,
                        "sudocuhName": "",
                    },
                ],
                id="no_filter",
            ),
            pytest.param(
                {"document_type": "CC"},
                [
                    {
                        "id": "00000000-0000-0000-1111-000000000000",
                        "documentType": "CC",
                        "name": "Déroulement des plans de test",
                        "scopeList": [],
                        "scopeSugg": [],
                        "isStructuring": False,
                        "sudocuhName": "",
                    },
                    {
                        "id": "00000000-0000-0000-3333-000000000000",
                        "documentType": "CC",
                        "name": "Succès du déroulement des plans de test",
                        "scopeList": ["pp"],
                        "scopeSugg": ["pp", "ppi"],
                        "isStructuring": False,
                        "sudocuhName": "",
                    },
                ],
                id="document_type",
            ),
        ],
    )
    def test_list(
        self,
        api_client: APIClient,
        query_params: dict,
        expected: list,
    ) -> None:
        EventTypeFactory(
            id="00000000-0000-0000-1111-000000000000",
            document_type=EventType.DocumentType.CC,
            name="Déroulement des plans de test",
        )
        EventTypeFactory(
            id="00000000-0000-0000-2222-000000000000",
            document_type=EventType.DocumentType.PLU,
            name="Echec du déroulement des plans de test",
        )
        EventTypeFactory(
            id="00000000-0000-0000-3333-000000000000",
            document_type=EventType.DocumentType.CC,
            name="Succès du déroulement des plans de test",
            scope_list=[EventScope.PP],
            scope_sugg=[EventScope.PP, EventScope.PPI],
        )
        EventTypeFactory(
            id="00000000-0000-0000-FFFF-000000000000",
            document_type=EventType.DocumentType.CC,
            name="Je suis invisible car désactivé",
            is_active=False,
        )
        url = f"{reverse('internal_api:event_types-list')}?{urlencode(query_params, doseq=True)}"

        with assertNumQueries(BASE_QUERIES_COUNT + 1):
            response = api_client.get(url, format="json")

        assert response.status_code == 200
        assert response.json()["results"] == expected

    def test_detail(self, api_client: APIClient) -> None:
        event_type = EventTypeFactory(
            id="00000000-0000-0000-1111-000000000000",
            document_type=EventType.DocumentType.CC,
            name="Déroulement des plans de test",
            scope_list=[EventScope.PP],
            scope_sugg=[EventScope.PP, EventScope.PPI],
        )

        url = reverse("internal_api:event_types-detail", args=[event_type.pk])
        with assertNumQueries(1):
            response = api_client.get(url, format="json")

        assert response.status_code == 200
        assert response.json()
        assert response.json() == {
            "id": "00000000-0000-0000-1111-000000000000",
            "documentType": "CC",
            "name": "Déroulement des plans de test",
            "scopeList": ["pp"],
            "scopeSugg": ["pp", "ppi"],
            "isStructuring": False,
            "sudocuhName": "",
        }


# TODO: create a folder to split test_views and to create test_views_procedure.py


@pytest.mark.django_db
class TestProcedureCreation:
    # InsertForm.vue
    def test_principal_procedure(self, api_client_with_auth: SupabaseApiClient) -> None:
        url = reverse("internal_api:procedures-list")
        collectivite = CollectiviteFactory(
            with_flat_members=True, with_flat_members__for_snapshot=True
        )
        perimetre = collectivite.flat_members.order_by("code_insee").values_list(
            "code_insee", flat=True
        )
        topics = Topic.objects.filter(name__in=["zan", "coastline"])
        assert Procedure.objects.count() == 0
        data = {
            # "shareable": True,
            # "secondary_procedure_of": "",  # just in case of secondary procedure,
            "type": ProcedureType.ABROGATION,  # this.typeProcedure
            # collectivitePorteuseCode () {
            #   if (this.collectivite[this.typeCompetence]) {
            #     // return the collectivite if it has the competence
            #     return this.collectivite.code
            #   } else if (this.collectivite.intercommunalite) {
            #     // return the interco if it exist.
            #     return this.collectivite.intercommunalite.code
            #   } else {
            #     // Return the collectivite code if there is no groupement available.
            #     // This can create an anomaly with Banatic but is better than nothing.
            #     return this.collectivite.code
            #   }
            # },
            "collectivite_porteuse_id": collectivite.pk,
            # "is_principale": True,
            # "status": "en cours",
            # "is_sectoriel": None,
            "is_scot": False,  # or True, this.typeDu
            "is_pluih": False,  # or True, this.typeDu
            "is_pdu": None,  # or True, this.typeDu
            "current_perimetre": perimetre,  # oldFomattedPerimetre,
            "doc_type": TypeDocument.PLUI,  # this.procedureCategory === 'principale' ? this.typeDu : this.procedureParentDocType,
            # "departements": ["TODO"],  # departements = [...new Set(detailedPerimetre.map(e => e.departementCode))]
            "numero": "",  # this.procedureCategory === 'principale' ? '1' : this.numberProcedure,
            # "project_id": "TODO",  # project_id: insertedProject,
            "name": "Computed name",  # TODO later: compute the name in Django.
            # "owner_id": "TODO",  # this.$user.id
            "started_before_huwart_law": False,  # this.startedBeforeHuwartLaw
            # "testing": True,  # TODO: remove me
            "topics_id": topics.values_list("id", flat=True),
        }
        response = api_client_with_auth.post(url, data=data)
        assert response.status_code == 201
        assert Procedure.objects.count() == 1
        procedure = Procedure.objects.first()

        # Check project creation
        # Only for principal procedures.
        assert procedure.project
        # name: `${this.typeProcedure} ${this.typeDu}`,
        # doc_type: this.typeDu,
        # region: this.collectivite.regionCode,
        # current_perimetre: oldFomattedPerimetre,
        # collectivite_id: this.collectivite.intercommunaliteCode || this.collectivite.code,
        # collectivite_porteuse_id: this.collectivitePorteuseCode,
        # test: true,
        # owner: this.$user.id

        #   shareable: true, # OK
        assert procedure.shareable
        #   secondary_procedure_of: this.procedureParent, # OK
        assert not procedure.secondary_procedure_of
        #   type: this.typeProcedure, # OK
        assert procedure.type == "TODO"
        #   collectivite_porteuse_id: this.collectivitePorteuseCode, # OK
        assert procedure.collectivite_porteuse_id == collectivite.pk
        #   is_principale: this.procedureCategory === 'principale', # OK
        assert procedure.is_principale
        #   status: 'en cours', # OK
        assert procedure.status == "en cours"
        #   is_sectoriel: null, # OK
        assert procedure.is_sectoriel is None
        #   is_scot: this.typeDu === 'SCOT', # OK
        assert procedure.vaut_SCoT is False
        #   is_pluih: this.typeDu === 'PLUiH', # OK
        assert procedure.vaut_PLH is False
        #   is_pdu: null, # OK
        assert procedure.vaut_PDM is False
        #   current_perimetre: oldFomattedPerimetre,  # OK
        assert (
            procedure.perimetre.order_by("code_insee").values_list(
                "code_insee", flat=True
            )
            == perimetre
        )
        # [{"name": "Thoissey", "inseeCode": "01420"}]
        assert procedure.current_perimetre == [
            {"name": name, "inseeCode": code_insee}
            for name, code_insee in procedure.perimetre.values("intitule", "code_insee")
        ]
        #   doc_type: this.procedureCategory === 'principale' ? this.typeDu : this.procedureParentDocType, # OK
        assert procedure.doc_type == TypeDocument.PLUI
        assert procedure.type_document == TypeDocument.PLUI
        #   departements, # OK
        assert sorted(procedure.departements) == sorted(
            procedure.perimetre.values_list("departement__code", flat=True)
        )  # check this
        #   numero: this.procedureCategory === 'principale' ? '1' : this.numberProcedure, # OK
        assert procedure.numero == "1"
        #   project_id: insertedProject, # OK
        assert procedure.project_id is not None
        #   name: (this.baseName + ' ' + this.nameComplement).trim(), # OK
        assert procedure.name == "Computed name"
        #   owner_id: this.$user.id, # OK
        assert procedure.owner_id == response.request.user.pk
        #   started_before_huwart_law: this.startedBeforeHuwartLaw, # OK
        assert procedure.started_before_huwart_law is False
        #   testing: true # OK
        #   TODO: remove me
        assert procedure.testing is True

        assert procedure.perimetre.all()
        # const fomattedPerimetre = detailedPerimetre.map(e => ({ collectivite_code: e.code, collectivite_type: e.type, procedure_id: insertedProcedure[0].id, opposable: false, departement: e.departementCode }))
        # List of selected municipalities in the intermunicipality area.
        # await this.$supabase.from('procedures_perimetres').insert(fomattedPerimetre)
        for commune_procedure in procedure.perimetre_through.select_related(
            "departement"
        ).all():
            assert commune_procedure.collectivite_code == collectivite.siren
            assert commune_procedure.collectivite_type == collectivite.type
            assert (
                commune_procedure.departement == commune_procedure.commune.departement
            )
            assert commune_procedure.opposable is False

        assert procedure.topics.all() == topics.all()
        # const topicsToInsert = this.topics.map((e) => {
        #   return {
        #     topic_id: e.value,
        #     procedure_id: insertedProcedure[0].id,
        #     comment: e.text === 'Autre' ? this.topicOtherComment : ''
        #   }
        # })
        # await this.$supabase.from('core_proceduretopic').insert(topicsToInsert).select()

    def test_secondary_procedure(self):
        pass

    def test_pp_not_allowed(self):
        pass

    def test_sp_not_allowed(self):
        pass


class TestProcedureList:
    pass


class TestProcedureDetail:
    pass


class TestReadOnly:
    # Impossible to delete.
    # Impossible to update.
    pass
