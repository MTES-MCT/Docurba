import pytest
from django.test import Client
from django.urls import reverse
from pytest_django.asserts import assertContains, assertNotContains

from docurba.core.models import Procedure, Topic, TypeCollectivite, TypeDocument
from tests.core.factories import ProcedureFactory


@pytest.mark.parametrize("doc_type", TypeDocument.values)
@pytest.mark.django_db
def test_procedure_change_page(admin_client: Client, doc_type: TypeDocument) -> None:
    procedure = ProcedureFactory(doc_type=doc_type)
    response = admin_client.get(
        reverse("admin:core_procedure_change", kwargs={"object_id": procedure.pk})
    )
    assert response.status_code == 200


@pytest.mark.django_db
class TestProcedureList:
    def test_topics_filter(self, admin_client: Client) -> None:
        topic = Topic.objects.first()
        procedure_with_topic = Procedure.objects.create()
        procedure_with_topic.topics.add(topic)
        procedure_without_topics = Procedure.objects.create()

        response = admin_client.get(
            f"{reverse('admin:core_procedure_changelist')}?topic={topic.name}"
        )
        assertNotContains(response, procedure_without_topics.pk)
        assertContains(response, procedure_with_topic.pk)

        response = admin_client.get(reverse("admin:core_procedure_changelist"))
        assertContains(response, procedure_without_topics.pk)
        assertContains(response, procedure_with_topic.pk)

    def test_collectivite_porteuse_type_filter(self, admin_client: Client) -> None:
        procedure_polem = ProcedureFactory(
            collectivite_porteuse__type=TypeCollectivite.POLEM
        )
        procedure_cc = ProcedureFactory(collectivite_porteuse__type=TypeCollectivite.CC)

        response = admin_client.get(
            f"{reverse('admin:core_procedure_changelist')}?collectivite_type={procedure_polem.collectivite_porteuse.type}"
        )
        assertNotContains(response, procedure_cc.pk)
        assertContains(response, procedure_polem.pk)

        response = admin_client.get(reverse("admin:core_procedure_changelist"))
        assertContains(response, procedure_polem.pk)
        assertContains(response, procedure_cc.pk)
