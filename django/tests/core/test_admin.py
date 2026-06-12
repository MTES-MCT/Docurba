import pytest
from django.test import Client
from django.urls import reverse
from pytest_django import DjangoAssertNumQueries
from pytest_django.asserts import assertContains, assertNotContains

from docurba.core.models import (
    Procedure,
    Topic,
    TypeCollectivite,
    TypeDocument,
)
from tests.core.factories import (
    EventFactory,
    ProcedureFactory,
)
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
def test_procedure_change_page(
    admin_session_client: Client, doc_type: TypeDocument
) -> None:
    procedure = ProcedureFactory(doc_type=doc_type)
    response = admin_session_client.get(
        reverse("admin:core_procedure_change", kwargs={"object_id": procedure.pk})
    )
    assert response.status_code == 200


@pytest.mark.django_db
class TestProcedureList:
    def test_topics_filter(self, admin_session_client: Client) -> None:
        topic = Topic.objects.first()
        procedure_with_topic = Procedure.objects.create()
        procedure_with_topic.topics.add(topic)
        procedure_without_topics = Procedure.objects.create()

        response = admin_session_client.get(
            f"{reverse('admin:core_procedure_changelist')}?topic={topic.name}"
        )
        assertNotContains(response, procedure_without_topics.pk)
        assertContains(response, procedure_with_topic.pk)

        response = admin_session_client.get(reverse("admin:core_procedure_changelist"))
        assertContains(response, procedure_without_topics.pk)
        assertContains(response, procedure_with_topic.pk)

    def test_collectivite_porteuse_type_filter(
        self,
        admin_session_client: Client,
        django_assert_num_queries: DjangoAssertNumQueries,
    ) -> None:
        procedure_polem = ProcedureFactory(
            collectivite_porteuse__type=TypeCollectivite.POLEM
        )
        procedure_cc = ProcedureFactory(collectivite_porteuse__type=TypeCollectivite.CC)

        response = admin_session_client.get(
            f"{reverse('admin:core_procedure_changelist')}?collectivite_type={procedure_polem.collectivite_porteuse.type}"
        )
        assertNotContains(response, procedure_cc.pk)
        assertContains(response, procedure_polem.pk)

        with django_assert_num_queries(8):
            response = admin_session_client.get(
                reverse("admin:core_procedure_changelist")
            )
        assertContains(response, procedure_polem.pk)
        assertContains(response, procedure_cc.pk)

    def test_huwart_law_filter(self, admin_session_client: Client) -> None:
        huwart = ProcedureFactory(started_before_huwart_law=True)
        not_huwart = ProcedureFactory(started_before_huwart_law=False)

        response = admin_session_client.get(
            f"{reverse('admin:core_procedure_changelist')}?started_before_huwart_law__exact=1"
        )
        assertNotContains(response, not_huwart.pk)
        assertContains(response, huwart.pk)

        response = admin_session_client.get(reverse("admin:core_procedure_changelist"))
        assertContains(response, not_huwart.pk)
        assertContains(response, huwart.pk)


@pytest.mark.django_db
class TestEventChange:
    def test_nominal_case(
        self,
        admin_session_client: Client,
<<<<<<< HEAD
        # django_assert_num_queries: DjangoAssertNumQueries,
        snapshot,  # noqa: ANN001
    ) -> None:
        event = EventFactory()
        with assertSnapshotQueries(snapshot(name="events_test_nominal_case_response")):
=======
        django_assert_num_queries: DjangoAssertNumQueries,
    ) -> None:
        event = EventFactory()
        with django_assert_num_queries(6):
>>>>>>> c372a6a4 (Revert "WIP with itoutils: not working")
            response = admin_session_client.get(
                reverse("admin:core_event_change", kwargs={"object_id": event.pk})
            )
        assert response.status_code == 200
        assertContains(response, "Enregistrer et continuer les modifications")

        new_user = ProfileFactory()
        with assertSnapshotQueries(
            snapshot(name="events_test_nominal_case_response_second")
        ):
            response = admin_session_client.post(
                reverse("admin:core_event_change", kwargs={"object_id": event.pk}),
                data={
                    "profile": new_user.pk,
                    "_continue": "Enregistrer et continuer les modifications",
                },
                follow=True,
            )
        assert response.status_code == 200

    def test_sudocuh_event_is_read_only(self, admin_session_client: Client) -> None:
        event = EventFactory(from_sudocuh=123456)
        response = admin_session_client.get(
            reverse("admin:core_event_change", kwargs={"object_id": event.pk})
        )
        assert response.status_code == 200
        assertNotContains(response, "Enregistrer et continuer les modifications")

        new_user = ProfileFactory()
        response = admin_session_client.post(
            reverse("admin:core_event_change", kwargs={"object_id": event.pk}),
            data={
                "profile": new_user.pk,
                "_continue": "Enregistrer et continuer les modifications",
            },
        )
        assert response.status_code == 403
