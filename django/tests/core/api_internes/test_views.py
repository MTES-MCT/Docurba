from urllib.parse import urlencode

import pytest
from django.urls import reverse
from pytest_django.asserts import assertNumQueries
from rest_framework.test import APIClient

from core.models import TypeCollectivite
from core.tests.factories import (
    create_commune,
    create_departement,
    create_groupement,
    create_region,
)


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
                        "regionCode": "76",
                        "departementCode": "30",
                    },
                    {
                        "code": "132435465",
                        "type": "SMO",
                        "intitule": "Groupement 3",
                        "regionCode": "53",
                        "departementCode": "35",
                    },
                    {
                        "code": "987654321",
                        "type": "CC",
                        "intitule": "Groupement 1",
                        "regionCode": "53",
                        "departementCode": "29",
                    },
                ],
                id="no_filter",
            ),
            pytest.param(
                {"departement": "30"},
                [
                    {
                        "code": "123456789",
                        "type": "SIVOM",
                        "intitule": "Groupement 2",
                        "regionCode": "76",
                        "departementCode": "30",
                    },
                ],
                id="one_department",
            ),
            pytest.param(
                {"departement": "30,29"},
                [
                    {
                        "code": "123456789",
                        "type": "SIVOM",
                        "intitule": "Groupement 2",
                        "regionCode": "76",
                        "departementCode": "30",
                    },
                    {
                        "code": "987654321",
                        "type": "CC",
                        "intitule": "Groupement 1",
                        "regionCode": "53",
                        "departementCode": "29",
                    },
                ],
                id="many_departments",
            ),
            pytest.param(
                {"region": "53", "type": "CC"},
                [
                    {
                        "code": "987654321",
                        "type": "CC",
                        "intitule": "Groupement 1",
                        "regionCode": "53",
                        "departementCode": "29",
                    },
                ],
                id="region_and_type",
            ),
            pytest.param(
                {"region": "53"},
                [
                    {
                        "code": "132435465",
                        "type": "SMO",
                        "intitule": "Groupement 3",
                        "regionCode": "53",
                        "departementCode": "35",
                    },
                    {
                        "code": "987654321",
                        "type": "CC",
                        "intitule": "Groupement 1",
                        "regionCode": "53",
                        "departementCode": "29",
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
                        "regionCode": "53",
                        "departementCode": "35",
                    },
                    {
                        "code": "987654321",
                        "type": "CC",
                        "intitule": "Groupement 1",
                        "regionCode": "53",
                        "departementCode": "29",
                    },
                ],
                id="many_types",
            ),
        ],
    )
    def test_list_filters(
        self, api_client: APIClient, query_params: str, expected: list
    ) -> None:
        region_bretagne = create_region(code_insee="53")
        region_occitanie = create_region(code_insee="76")
        finistere = create_departement(
            code_insee="29", nom="Finistère", region=region_bretagne
        )
        gard = create_departement(code_insee="30", nom="Gard", region=region_occitanie)
        ille_et_vilaine = create_departement(
            code_insee="35", nom="Ille-et-Vilaine", region=region_bretagne
        )
        create_groupement(
            code_insee="987654321",
            groupement_type=TypeCollectivite.CC,
            departement=finistere,
            nom="Groupement 1",
        )
        create_groupement(
            departement=ille_et_vilaine,
            groupement_type=TypeCollectivite.SMO,
            code_insee="132435465",
            nom="Groupement 3",
        )
        create_groupement(
            code_insee="123456789",
            groupement_type=TypeCollectivite.SIVOM,
            departement=gard,
            nom="Groupement 2",
        )
        url = f"{reverse('api_internes:collectivites-list')}?{urlencode(query_params)}"
        with assertNumQueries(1):
            response = api_client.get(url, format="json")

        assert response.status_code == 200
        assert response.json() == expected

    @pytest.mark.parametrize(
        ("query_params", "expected"),
        [
            pytest.param(
                {"exclude_communes": "true"},
                [
                    {
                        "code": "123456778",
                        "type": "CC",
                        "intitule": "Groupement 2",
                        "regionCode": "53",
                        "departementCode": "29",
                    },
                ],
                id="without_communes",
            ),
            pytest.param(
                {"exclude_communes": "false"},
                [
                    {
                        "code": "123456778",
                        "type": "CC",
                        "intitule": "Groupement 2",
                        "regionCode": "53",
                        "departementCode": "29",
                    },
                    {
                        "code": "123456789",
                        "type": "COM",
                        "intitule": "Groupement 1",
                        "regionCode": "53",
                        "departementCode": "29",
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
                        "regionCode": "53",
                        "departementCode": "29",
                    },
                    {
                        "code": "123456789",
                        "type": "COM",
                        "intitule": "Groupement 1",
                        "regionCode": "53",
                        "departementCode": "29",
                    },
                ],
                id="default_value",
            ),
        ],
    )
    def test_exclude_communes_from_list(
        self, api_client: APIClient, query_params: dict, expected: list
    ) -> None:
        region_bretagne = create_region(code_insee="53")
        finistere = create_departement(
            code_insee="29", nom="Finistère", region=region_bretagne
        )
        create_groupement(
            groupement_type=TypeCollectivite.COM,
            departement=finistere,
            nom="Groupement 1",
            code_insee="123456789",
        )
        create_groupement(
            groupement_type=TypeCollectivite.CC,
            departement=finistere,
            nom="Groupement 2",
            code_insee="123456778",
        )
        url = f"{reverse('api_internes:collectivites-list')}?{urlencode(query_params)}"
        with assertNumQueries(1):
            response = api_client.get(url, format="json")

        assert response.status_code == 200
        assert response.json() == expected

    def test_detail(self, api_client: APIClient) -> None:
        region = create_region(code_insee="53")  # Bretagne
        departement = create_departement(
            code_insee="29", nom="Finistère", region=region
        )
        groupement = create_groupement(
            code_insee="987654321",
            groupement_type=TypeCollectivite.CC,
            departement=departement,
            nom="Groupement 1",
        )

        url = reverse("api_internes:collectivites-detail", args=[groupement.pk])
        with assertNumQueries(1):
            response = api_client.get(url, format="json")

        assert response.status_code == 200
        assert response.json() == {
            "code": "987654321",
            "type": "CC",
            "intitule": "Groupement 1",
            "regionCode": "53",
            "departementCode": "29",
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
                        "code": "29001",
                        "type": "COM",
                        "intitule": "Commune 1",
                        "regionCode": "53",
                        "departementCode": "29",
                    },
                    {
                        "code": "30000",
                        "type": "COM",
                        "intitule": "Commune 2",
                        "regionCode": "76",
                        "departementCode": "30",
                    },
                    {
                        "code": "35000",
                        "type": "COMD",
                        "intitule": "Commune 3",
                        "regionCode": "53",
                        "departementCode": "35",
                    },
                ],
                id="no_filter",
            ),
            pytest.param(
                {"departement": 29},
                [
                    {
                        "code": "29001",
                        "type": "COM",
                        "intitule": "Commune 1",
                        "regionCode": "53",
                        "departementCode": "29",
                    },
                ],
                id="one_department",
            ),
            pytest.param(
                {"departement": "30,35"},
                [
                    {
                        "code": "30000",
                        "type": "COM",
                        "intitule": "Commune 2",
                        "regionCode": "76",
                        "departementCode": "30",
                    },
                    {
                        "code": "35000",
                        "type": "COMD",
                        "intitule": "Commune 3",
                        "regionCode": "53",
                        "departementCode": "35",
                    },
                ],
                id="many_departments",
            ),
            pytest.param(
                {"region": "53", "type": "COMD"},
                [
                    {
                        "code": "35000",
                        "type": "COMD",
                        "intitule": "Commune 3",
                        "regionCode": "53",
                        "departementCode": "35",
                    },
                ],
                id="region_and_type",
            ),
            pytest.param(
                {"region": "53"},
                [
                    {
                        "code": "29001",
                        "type": "COM",
                        "intitule": "Commune 1",
                        "regionCode": "53",
                        "departementCode": "29",
                    },
                    {
                        "code": "35000",
                        "type": "COMD",
                        "intitule": "Commune 3",
                        "regionCode": "53",
                        "departementCode": "35",
                    },
                ],
                id="region",
            ),
        ],
    )
    def test_list(
        self, api_client: APIClient, query_params: dict, expected: list
    ) -> None:
        region_bretagne = create_region(code_insee="53")
        region_occitanie = create_region(code_insee="76")
        finistere = create_departement(
            code_insee="29", nom="Finistère", region=region_bretagne
        )
        gard = create_departement(code_insee="30", nom="Gard", region=region_occitanie)
        ille_et_vilaine = create_departement(
            code_insee="35", nom="Ille-et-Vilaine", region=region_bretagne
        )
        create_commune(
            code_insee="29001",
            commune_type=TypeCollectivite.COM,
            departement=finistere,
            nom="Commune 1",
        )
        create_commune(
            code_insee="30000",
            commune_type=TypeCollectivite.COM,
            departement=gard,
            nom="Commune 2",
        )
        create_commune(
            code_insee="35000",
            commune_type=TypeCollectivite.COMD,
            departement=ille_et_vilaine,
            nom="Commune 3",
        )
        url = f"{reverse('api_internes:communes-list')}?{urlencode(query_params)}"

        with assertNumQueries(1):
            response = api_client.get(url, format="json")

        assert response.status_code == 200
        assert response.json() == expected

    def test_details(self, api_client: APIClient) -> None:
        region = create_region(code_insee="53")  # Bretagne
        departement = create_departement(
            code_insee="29", nom="Finistère", region=region
        )
        commune = create_commune(
            code_insee="987654321",
            commune_type=TypeCollectivite.COM,
            departement=departement,
            nom="Groupement 1",
        )

        url = reverse("api_internes:communes-detail", args=[commune.pk])
        with assertNumQueries(1):
            response = api_client.get(url, format="json")

        assert response.status_code == 200
        assert response.json()
        assert response.json() == {
            "code": "987654321",
            "type": "COM",
            "intitule": "Groupement 1",
            "regionCode": "53",
            "departementCode": "29",
        }
