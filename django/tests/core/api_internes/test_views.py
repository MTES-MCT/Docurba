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
    def test_list(self, api_client: APIClient) -> None:
        region = create_region(code_insee="53")  # Bretagne
        departement = create_departement(
            code_insee="29", nom="Finistère", region=region
        )
        create_groupement(
            code_insee="987654321",
            groupement_type=TypeCollectivite.CC,
            departement=departement,
            nom="Groupement 1",
        )
        create_groupement(
            code_insee="123456789",
            groupement_type=TypeCollectivite.CC,
            departement=departement,
            nom="Groupement 2",
        )
        url = reverse("api_internes:collectivites-list")
        with assertNumQueries(1):
            response = api_client.get(url, format="json")

        assert response.status_code == 200
        assert response.json() == [
            {
                "code": "123456789",
                "type": "CC",
                "intitule": "Groupement 2",
                "regionCode": "53",
                "departementCode": "29",
            },
            {
                "code": "987654321",
                "type": "CC",
                "intitule": "Groupement 1",
                "regionCode": "53",
                "departementCode": "29",
            },
        ]

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
    def test_list(self, api_client: APIClient) -> None:
        region = create_region(code_insee="53")  # Bretagne
        departement = create_departement(
            code_insee="29", nom="Finistère", region=region
        )
        create_commune(
            code_insee="29001",
            commune_type=TypeCollectivite.COM,
            departement=departement,
            nom="Commune 1",
        )
        create_commune(
            code_insee="29000",
            commune_type=TypeCollectivite.COM,
            departement=departement,
            nom="Commune 2",
        )
        url = reverse("api_internes:communes-list")
        with assertNumQueries(1):
            response = api_client.get(url, format="json")

        assert response.status_code == 200
        assert response.json() == [
            {
                "code": "29000",
                "type": "COM",
                "intitule": "Commune 2",
                "regionCode": "53",
                "departementCode": "29",
            },
            {
                "code": "29001",
                "type": "COM",
                "intitule": "Commune 1",
                "regionCode": "53",
                "departementCode": "29",
            },
        ]

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
