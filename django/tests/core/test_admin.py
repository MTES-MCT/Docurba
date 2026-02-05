import pytest
from django.test import Client
from django.urls import reverse

from core.models import TypeDocument
from tests.factories import create_procedure


@pytest.mark.parametrize("doc_type", TypeDocument.values)
@pytest.mark.django_db
def test_procedure_change_page(admin_client: Client, doc_type: TypeDocument) -> None:
    procedure = create_procedure(doc_type=doc_type)
    response = admin_client.get(
        reverse("admin:core_procedure_change", kwargs={"object_id": procedure.pk})
    )
    assert response.status_code == 200
