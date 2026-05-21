import pytest
from django.test import Client
from django.urls import reverse
from pytest_django import DjangoAssertNumQueries
from pytest_django.asserts import assertContains, assertNotContains

from docurba.core.models import Procedure, Topic, TypeCollectivite, TypeDocument
from tests.core.factories import EventFactory, ProcedureFactory
from tests.users.factories import ProfileFactory

UPDATE_BASE_EXPECTED_NUM_QUERIES = (
    1  # django_session
    + 1  # get authenticated user info
    + 1  # savepoint
    + 1  # insert into django_admin_log
    + 1  # release savepoint
    + 1  # django session
    + 1  # get authenticated user info
)


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

    def test_huwart_law_filter(self, admin_client: Client) -> None:
        huwart = ProcedureFactory(started_before_huwart_law=True)
        not_huwart = ProcedureFactory(started_before_huwart_law=False)

        response = admin_client.get(
            f"{reverse('admin:core_procedure_changelist')}?started_before_huwart_law__exact=1"
        )
        assertNotContains(response, not_huwart.pk)
        assertContains(response, huwart.pk)

        response = admin_client.get(reverse("admin:core_procedure_changelist"))
        assertContains(response, not_huwart.pk)
        assertContains(response, huwart.pk)


def test_event_change_page(
    admin_client: Client, django_assert_num_queries: DjangoAssertNumQueries
) -> None:
    event = EventFactory()
    with django_assert_num_queries(5):
        response = admin_client.get(
            reverse("admin:core_event_change", kwargs={"object_id": event.pk})
        )
    assert response.status_code == 200

    new_user = ProfileFactory()
    num_queries = (
        1  # select doc_frise _event
        + 1  # select procedures_perimetres
        + 2  # select profile
        + 1  # update doc_frise_events
        + 1  # select doc_frise_events
        + 1  # select procedures_perimetres
        + 1  # select profiles
    )
    with django_assert_num_queries(UPDATE_BASE_EXPECTED_NUM_QUERIES + num_queries):
        response = admin_client.post(
            reverse("admin:core_event_change", kwargs={"object_id": event.pk}),
            data={
                "profile": new_user.pk,
                "_continue": "Enregistrer et continuer les modifications",
            },
            follow=True,
        )
    assert response.status_code == 200
