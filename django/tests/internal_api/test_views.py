import pytest
from django.urls import reverse
from pytest_django.asserts import assertNumQueries
from rest_framework.test import APIClient

from docurba.core.models import TypeCollectivite
from tests.core.factories import (
    CollectiviteFactory,
    CommuneFactory,
)


@pytest.mark.django_db
class TestCollectivitesAPI:
    def test_list(self, api_client: APIClient) -> None:
        CollectiviteFactory(
            code_insee_unique="987654321",
            type=TypeCollectivite.CC,
            departement__code_insee="13",
            nom="Groupement 1",
        )
        CollectiviteFactory(
            code_insee_unique="123456789",
            type=TypeCollectivite.CC,
            departement__code_insee="13",
            nom="Groupement 2",
        )
        url = reverse("internal_api:collectivites-list")
        with assertNumQueries(1):
            response = api_client.get(url, format="json")

        assert response.status_code == 200
        assert response.json() == [
            {
                "code": "123456789",
                "type": "CC",
                "intitule": "Groupement 2",
                "regionCode": "93",
                "departementCode": "13",
            },
            {
                "code": "987654321",
                "type": "CC",
                "intitule": "Groupement 1",
                "regionCode": "93",
                "departementCode": "13",
            },
        ]

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
    def test_list(self, api_client: APIClient) -> None:
        CommuneFactory(
            code_insee_unique="13150",
            type=TypeCollectivite.COM,
            departement__code_insee="13",
            nom="Commune 1",
        )
        CommuneFactory(
            code_insee_unique="13490",
            type=TypeCollectivite.COM,
            departement__code_insee="13",
            nom="Commune 2",
        )
        url = reverse("internal_api:communes-list")
        with assertNumQueries(1):
            response = api_client.get(url, format="json")

        assert response.status_code == 200
        assert response.json() == [
            {
                "code": "13150",
                "type": "COM",
                "intitule": "Commune 1",
                "regionCode": "93",
                "departementCode": "13",
            },
            {
                "code": "13490",
                "type": "COM",
                "intitule": "Commune 2",
                "regionCode": "93",
                "departementCode": "13",
            },
        ]

    def test_details(self, api_client: APIClient) -> None:
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
