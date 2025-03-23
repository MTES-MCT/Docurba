from csv import DictReader

import pytest
from django.test import Client

from core.models import CommuneProcedure, Procedure, TypeDocument


def create_commune_procedure(*, code: str, departement: str) -> CommuneProcedure:
    procedure = Procedure.objects.create(
        type_document=TypeDocument.PLU,
        is_principale=True,
        collectivite_porteuse_id=code,
    )
    return procedure.perimetre.create(
        collectivite_code=code,
        collectivite_type="COM",
        departement=departement,
    )


class TestAPIPerimetres:
    @pytest.mark.django_db
    def test_format_csv(self, client: Client) -> None:
        commune_procedure = create_commune_procedure(code="12345", departement="12")

        response = client.get("/api/perimetres", {"departement": "12"})

        assert response.status_code == 200
        assert response["content-type"] == "text/csv;charset=utf-8"

        reader = DictReader(response.content.decode().splitlines())

        assert list(reader) == [
            {
                "collectivite_code": commune_procedure.collectivite_code,
                "collectivite_type": commune_procedure.collectivite_type,
                "procedure_id": str(commune_procedure.procedure_id),
                "opposable": "False",
            }
        ]

    @pytest.mark.django_db
    def test_filtre_par_department(self, client: Client) -> None:
        create_commune_procedure(code="12345", departement="12")
        create_commune_procedure(code="34567", departement="34")

        response = client.get("/api/perimetres", {"departement": "12"})
        reader = DictReader(response.content.decode().splitlines())
        assert len(list(reader)) == 1

    @pytest.mark.django_db
    def test_retourne_tout_sans_filtre_departement(self, client: Client) -> None:
        create_commune_procedure(code="12345", departement="12")
        create_commune_procedure(code="34567", departement="34")

        response = client.get("/api/perimetres")
        reader = DictReader(response.content.decode().splitlines())
        assert len(list(reader)) == 2
