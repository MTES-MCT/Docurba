from urllib.parse import urlencode

import pytest
from django.urls import reverse
from pytest_django.asserts import assertNumQueries
from rest_framework.test import APIClient
from syrupy.data import Snapshot

from docurba.core.enums import EventScope
from docurba.core.models import (
    EventType,
    TypeCollectivite,
)
from tests.core.factories import (
    CollectiviteFactory,
    CommuneFactory,
    EventTypeFactory,
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
        snapshot: Snapshot,
    ) -> None:
        CollectiviteFactory(
            code_insee_unique="987654321",
            type=TypeCollectivite.CC,
            departement__code_insee="13",
            nom="Groupement 1",
        )
        CollectiviteFactory(
            code_insee_unique="123456789",
            type=TypeCollectivite.SIVOM,
            departement__code_insee="84",
            nom="Groupement 2",
        )
        CollectiviteFactory(
            code_insee_unique="132435465",
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
        self, api_client: APIClient, query_params: dict, snapshot: Snapshot
    ) -> None:
        CollectiviteFactory(
            type=TypeCollectivite.COM,
            departement__code_insee="13",
            nom="Groupement 1",
            code_insee_unique="123456789",
        )
        CollectiviteFactory(
            type=TypeCollectivite.CC,
            departement__code_insee="13",
            nom="Groupement 2",
            code_insee_unique="123456778",
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
        snapshot: Snapshot,
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
        self, api_client: APIClient, query_params: dict, snapshot: Snapshot
    ) -> None:
        CollectiviteFactory(
            type=TypeCollectivite.CC,
            departement__code_insee="13",
            nom="Groupement 1",
            code_insee_unique="123456789",
            competence_schema=True,
        )
        CollectiviteFactory(
            type=TypeCollectivite.CC,
            departement__code_insee="13",
            nom="Groupement 2",
            code_insee_unique="123456778",
            competence_plan=True,
        )
        CollectiviteFactory(
            type=TypeCollectivite.CC,
            departement__code_insee="30",
            nom="Groupement 3",
            code_insee_unique="987654321",
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
            code_insee_unique="987654321",
            type=TypeCollectivite.CC,
            departement__code_insee="13",
            nom="Groupement 1",
        )

        url = reverse("internal_api:collectivites-detail", args=[groupement.pk])
        with assertNumQueries(1):
            response = api_client.get(url, format="json")

        assert response.status_code == 200
        assert response.json() == {
            "code": "987654321",
            "siren": "987654321",
            "type": "CC",
            "intitule": "Groupement 1",
            "regionCode": "93",
            "departementCode": "13",
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
            pytest.param(
                {"code": "13150"},
                [
                    {
                        "code": "13150",
                        "type": "COM",
                        "intitule": "Commune 1",
                        "regionCode": "93",
                        "departementCode": "13",
                    },
                ],
                id="code_insee",
            ),
        ],
    )
    def test_list(
        self,
        api_client: APIClient,
        expected_num_queries: int,
        query_params: dict,
        snapshot: Snapshot,
    ) -> None:
        CommuneFactory(
            code_insee_unique="13150",
            type=TypeCollectivite.COM,
            departement__code_insee="13",
            nom="Commune 1",
        )
        CommuneFactory(
            code_insee_unique="30000",
            type=TypeCollectivite.COM,
            departement__code_insee="30",
            nom="Commune 2",
        )
        CommuneFactory(
            code_insee_unique="84000",
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
            code_insee_unique="987654321",
            type=TypeCollectivite.COM,
            departement__code_insee="13",
            nom="Groupement 1",
        )

        url = reverse("internal_api:communes-detail", args=[commune.pk])
        with assertNumQueries(1):
            response = api_client.get(url, format="json")

        assert response.status_code == 200
        assert response.json()
        assert response.json() == {
            "code": "987654321",
            "type": "COM",
            "intitule": "Groupement 1",
            "regionCode": "93",
            "departementCode": "13",
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
