from urllib.parse import urlencode

import pytest
from django.urls import reverse
from pytest_django.asserts import assertNumQueries
from rest_framework.test import APIClient

from docurba.core.models import Collectivite, TypeCollectivite
from tests.core.factories import (
    CollectiviteFactory,
    CommuneFactory,
)

BASE_QUERIES_COUNT = 1  # Count made by DRF for the pagination.


@pytest.mark.django_db
class TestCollectivitesAPI:
    @pytest.mark.parametrize(
        ("query_params", "expected"),
        [
            pytest.param(
                {},
                [
                    {
                        "code": "123456789",
                        "type": "SIVOM",
                        "intitule": "Groupement 2",
                        "regionCode": "93",
                        "departementCode": "84",
                    },
                    {
                        "code": "132435465",
                        "type": "SMO",
                        "intitule": "Groupement 3",
                        "regionCode": "76",
                        "departementCode": "30",
                    },
                    {
                        "code": "987654321",
                        "type": "CC",
                        "intitule": "Groupement 1",
                        "regionCode": "93",
                        "departementCode": "13",
                    },
                ],
                id="no_filter",
            ),
            pytest.param(
                {"departement": "84"},
                [
                    {
                        "code": "123456789",
                        "type": "SIVOM",
                        "intitule": "Groupement 2",
                        "regionCode": "93",
                        "departementCode": "84",
                    },
                ],
                id="one_department",
            ),
            pytest.param(
                {"departement": "84,13"},
                [
                    {
                        "code": "123456789",
                        "type": "SIVOM",
                        "intitule": "Groupement 2",
                        "regionCode": "93",
                        "departementCode": "84",
                    },
                    {
                        "code": "987654321",
                        "type": "CC",
                        "intitule": "Groupement 1",
                        "regionCode": "93",
                        "departementCode": "13",
                    },
                ],
                id="many_departments",
            ),
            pytest.param(
                {"region": "93", "type": "CC"},
                [
                    {
                        "code": "987654321",
                        "type": "CC",
                        "intitule": "Groupement 1",
                        "regionCode": "93",
                        "departementCode": "13",
                    },
                ],
                id="region_and_type",
            ),
            pytest.param(
                {"region": "93"},
                [
                    {
                        "code": "123456789",
                        "type": "SIVOM",
                        "intitule": "Groupement 2",
                        "regionCode": "93",
                        "departementCode": "84",
                    },
                    {
                        "code": "987654321",
                        "type": "CC",
                        "intitule": "Groupement 1",
                        "regionCode": "93",
                        "departementCode": "13",
                    },
                ],
                id="region",
            ),
            pytest.param(
                {"type": "CC,SMO"},
                [
                    {
                        "code": "132435465",
                        "type": "SMO",
                        "intitule": "Groupement 3",
                        "regionCode": "76",
                        "departementCode": "30",
                    },
                    {
                        "code": "987654321",
                        "type": "CC",
                        "intitule": "Groupement 1",
                        "regionCode": "93",
                        "departementCode": "13",
                    },
                ],
                id="many_types",
            ),
        ],
    )
    def test_list_filters(
        self, api_client: APIClient, query_params: str, expected: list
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

        url = f"{reverse('internal_api:collectivites-list')}?{urlencode(query_params)}"
        with assertNumQueries(BASE_QUERIES_COUNT + 1):
            response = api_client.get(url, format="json")

        assert response.status_code == 200
        assert response.json()["results"] == expected

    @pytest.mark.parametrize(
        ("query_params", "expected"),
        [
            pytest.param(
                {"without_communes": "true"},
                [
                    {
                        "code": "123456778",
                        "type": "CC",
                        "intitule": "Groupement 2",
                        "regionCode": "93",
                        "departementCode": "13",
                    },
                ],
                id="without_communes",
            ),
            pytest.param(
                {"without_communes": "false"},
                [
                    {
                        "code": "123456778",
                        "type": "CC",
                        "intitule": "Groupement 2",
                        "regionCode": "93",
                        "departementCode": "13",
                    },
                    {
                        "code": "123456789",
                        "type": "COM",
                        "intitule": "Groupement 1",
                        "regionCode": "93",
                        "departementCode": "13",
                    },
                ],
                id="with_communes",
            ),
            pytest.param(
                {},
                [
                    {
                        "code": "123456778",
                        "type": "CC",
                        "intitule": "Groupement 2",
                        "regionCode": "93",
                        "departementCode": "13",
                    },
                    {
                        "code": "123456789",
                        "type": "COM",
                        "intitule": "Groupement 1",
                        "regionCode": "93",
                        "departementCode": "13",
                    },
                ],
                id="default_value",
            ),
        ],
    )
    def test_without_communes_from_list(
        self, api_client: APIClient, query_params: dict, expected: list
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
        assert response.json()["results"] == expected

    @pytest.mark.parametrize(
        ("query_params", "expected_num_queries", "expected"),
        [
            pytest.param(
                {"with_members": "true"},
                3,
                [
                    {
                        "code": "111111111",
                        "type": "SIVOM",
                        "intitule": "Grand parent",
                        "regionCode": "93",
                        "departementCode": "13",
                        "membres": [
                            {
                                "code": "22222222",
                                "type": "CC",
                                "intitule": "Parent",
                                "regionCode": "93",
                                "departementCode": "13",
                            },
                            {
                                "code": "12345",
                                "type": "COM",
                                "intitule": "Enfant",
                                "regionCode": "93",
                                "departementCode": "13",
                            },
                        ],
                    },
                    {
                        "code": "22222222",
                        "type": "CC",
                        "intitule": "Parent",
                        "regionCode": "93",
                        "departementCode": "13",
                        "membres": [
                            {
                                "code": "12345",
                                "type": "COM",
                                "intitule": "Enfant",
                                "regionCode": "93",
                                "departementCode": "13",
                            },
                        ],
                    },
                    {
                        "code": "12345",
                        "type": "COM",
                        "intitule": "Enfant",
                        "regionCode": "93",
                        "departementCode": "13",
                        "membres": [],
                    },
                ],
                id="with_members",
            ),
            # pytest.param(
            #     {"with_groupements": "true"},
            #     [
            #         {
            #             "code": "123456778",
            #             "type": "CC",
            #             "intitule": "Groupement 2",
            #             "regionCode": "93",
            #             "departementCode": "13",
            #         },
            #         {
            #             "code": "123456789",
            #             "type": "COM",
            #             "intitule": "Groupement 1",
            #             "regionCode": "93",
            #             "departementCode": "13",
            #         },
            #     ],
            #     id="with_groupements",
            # ),
        ],
    )
    def test_with_groupements_and_members(
        self,
        api_client: APIClient,
        expected_num_queries: int,
        query_params: dict,
        expected: list,
    ) -> None:
        grand_parent = CollectiviteFactory(
            type=TypeCollectivite.SIVOM,
            departement__code_insee="13",
            nom="Grand parent",
            code_insee_unique="111111111",
        )
        parent = CollectiviteFactory(
            type=TypeCollectivite.CC,
            departement__code_insee="13",
            nom="Parent",
            code_insee_unique="22222222",
        )
        child = CollectiviteFactory(
            type=TypeCollectivite.COM,
            departement__code_insee="13",
            nom="Enfant",
            code_insee_unique="12345",
        )
        grand_parent.adhesions.add(*[parent])
        parent.adhesions.add(*[child])

        url = f"{reverse('internal_api:collectivites-list')}?{urlencode(query_params)}"
        # with assertNumQueries(expected_num_queries):
        response = api_client.get(url, format="json")

        assert response.status_code == 200
        assert response.json()["results"] == expected

    @pytest.mark.parametrize(
        ("query_params", "expected"),
        [
            pytest.param(
                {"competence": "schema"},
                [
                    {
                        "code": "123456789",
                        "type": "CC",
                        "intitule": "Groupement 1",
                        "regionCode": "93",
                        "departementCode": "13",
                    },
                    {
                        "code": "987654321",
                        "type": "CC",
                        "intitule": "Groupement 3",
                        "regionCode": "76",
                        "departementCode": "30",
                    },
                ],
                id="competence_schema",
            ),
            pytest.param(
                {"competence": "plan"},
                [
                    {
                        "code": "123456778",
                        "type": "CC",
                        "intitule": "Groupement 2",
                        "regionCode": "93",
                        "departementCode": "13",
                    },
                    {
                        "code": "987654321",
                        "type": "CC",
                        "intitule": "Groupement 3",
                        "regionCode": "76",
                        "departementCode": "30",
                    },
                ],
                id="competence_plan",
            ),
            pytest.param(
                {},
                [
                    {
                        "code": "123456778",
                        "type": "CC",
                        "intitule": "Groupement 2",
                        "regionCode": "93",
                        "departementCode": "13",
                    },
                    {
                        "code": "123456789",
                        "type": "CC",
                        "intitule": "Groupement 1",
                        "regionCode": "93",
                        "departementCode": "13",
                    },
                    {
                        "code": "987654321",
                        "type": "CC",
                        "intitule": "Groupement 3",
                        "regionCode": "76",
                        "departementCode": "30",
                    },
                ],
                id="sans_competence",
            ),
            pytest.param(
                {"competence": ["plan", "schema"]},
                [
                    {
                        "code": "123456778",
                        "type": "CC",
                        "intitule": "Groupement 2",
                        "regionCode": "93",
                        "departementCode": "13",
                    },
                    {
                        "code": "123456789",
                        "type": "CC",
                        "intitule": "Groupement 1",
                        "regionCode": "93",
                        "departementCode": "13",
                    },
                    {
                        "code": "987654321",
                        "type": "CC",
                        "intitule": "Groupement 3",
                        "regionCode": "76",
                        "departementCode": "30",
                    },
                ],
                id="competence_schema_ou_plan",
            ),
        ],
    )
    def test_competences_list(
        self, api_client: APIClient, query_params: dict, expected: list
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
        assert response.json()["results"] == expected

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
            "type": "CC",
            "intitule": "Groupement 1",
            "regionCode": "93",
            "departementCode": "13",
        }


@pytest.mark.django_db
class TestCommunesAPI:
    @pytest.mark.parametrize(
        ("query_params", "expected"),
        [
            pytest.param(
                {},
                [
                    {
                        "code": "13150",
                        "type": "COM",
                        "intitule": "Commune 1",
                        "regionCode": "93",
                        "departementCode": "13",
                    },
                    {
                        "code": "30000",
                        "type": "COM",
                        "intitule": "Commune 2",
                        "regionCode": "76",
                        "departementCode": "30",
                    },
                    {
                        "code": "84000",
                        "type": "COMD",
                        "intitule": "Commune 3",
                        "regionCode": "93",
                        "departementCode": "84",
                    },
                ],
                id="no_filter",
            ),
            pytest.param(
                {"departement": 13},
                [
                    {
                        "code": "13150",
                        "type": "COM",
                        "intitule": "Commune 1",
                        "regionCode": "93",
                        "departementCode": "13",
                    },
                ],
                id="one_department",
            ),
            pytest.param(
                {"departement": "30,13"},
                [
                    {
                        "code": "13150",
                        "type": "COM",
                        "intitule": "Commune 1",
                        "regionCode": "93",
                        "departementCode": "13",
                    },
                    {
                        "code": "30000",
                        "type": "COM",
                        "intitule": "Commune 2",
                        "regionCode": "76",
                        "departementCode": "30",
                    },
                ],
                id="many_departments",
            ),
            pytest.param(
                {"region": "93", "type": "COMD"},
                [
                    {
                        "code": "84000",
                        "type": "COMD",
                        "intitule": "Commune 3",
                        "regionCode": "93",
                        "departementCode": "84",
                    },
                ],
                id="region_and_type",
            ),
            pytest.param(
                {"region": "93"},
                [
                    {
                        "code": "13150",
                        "type": "COM",
                        "intitule": "Commune 1",
                        "regionCode": "93",
                        "departementCode": "13",
                    },
                    {
                        "code": "84000",
                        "type": "COMD",
                        "intitule": "Commune 3",
                        "regionCode": "93",
                        "departementCode": "84",
                    },
                ],
                id="region",
            ),
        ],
    )
    def test_list(
        self, api_client: APIClient, query_params: dict, expected: list
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
        url = f"{reverse('internal_api:communes-list')}?{urlencode(query_params)}"

        with assertNumQueries(BASE_QUERIES_COUNT + 1):
            response = api_client.get(url, format="json")

        assert response.status_code == 200
        assert response.json()["results"] == expected

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
