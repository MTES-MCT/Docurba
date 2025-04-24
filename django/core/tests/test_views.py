from csv import DictReader

import pytest
from django.test import Client
from pytest_django import DjangoAssertNumQueries

from core.models import Commune, Region, TypeDocument


def create_commune_et_procedure(
    *, code_insee: str = "12345", type_collectivite: str = "COM"
) -> Commune:
    region, _ = Region.objects.get_or_create(code_insee=12)
    departement = region.departements.create(code_insee=code_insee[:2])
    commune = Commune.objects.create(
        id=f"{code_insee}_{type_collectivite}",
        code_insee_unique=code_insee,
        type=type_collectivite,
        departement=departement,
    )
    commune.procedures.create(doc_type=TypeDocument.PLU, collectivite_porteuse=commune)
    return commune


class TestAPIPerimetres:
    @pytest.mark.django_db
    def test_format_csv(
        self, client: Client, django_assert_num_queries: DjangoAssertNumQueries
    ) -> None:
        commune = create_commune_et_procedure()
        with django_assert_num_queries(2):
            response = client.get("/api/perimetres", {"departement": "12"})

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
        create_commune_et_procedure(code_insee="12345", type_collectivite="COM")
        create_commune_et_procedure(code_insee="34567", type_collectivite="COM")

        response = client.get("/api/perimetres", {"departement": "12"})
        reader = DictReader(response.content.decode().splitlines())
        assert len(list(reader)) == 1

    @pytest.mark.django_db
    def test_retourne_tout_sans_filtre_departement(self, client: Client) -> None:
        create_commune_et_procedure(code_insee="12345", type_collectivite="COM")
        create_commune_et_procedure(code_insee="34567", type_collectivite="COM")

        response = client.get("/api/perimetres")
        reader = DictReader(response.content.decode().splitlines())
        assert len(list(reader)) == 2

    @pytest.mark.django_db
    def test_ignore_event_apres(self, client: Client) -> None:
        commune = create_commune_et_procedure()
        commune.procedures.first().event_set.create(
            type="Caractère exécutoire", date_evenement_string="2023-01-01"
        )

        response = client.get("/api/perimetres", {"avant": "2023-01-01"})
        reader = DictReader(response.content.decode().splitlines())
        assert [cp["opposable"] for cp in reader] == ["False"]

    @pytest.mark.django_db
    @pytest.mark.parametrize(
        "invalid_avant",
        ["2023-1-01", "2023-02-30", "invalid-date", "2023/01/01"],
    )
    def test_parsing_avant(self, client: Client, invalid_avant: str) -> None:
        response = client.get("/api/perimetres", {"avant": invalid_avant})

        assert response.status_code == 400
        assert (
            response.content.decode()
            == "Le paramètre 'avant' doit être une date valide au format YYYY-MM-DD."
        )
