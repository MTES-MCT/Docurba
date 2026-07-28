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
    def test_nominal_case(
        self,
        admin_session_client: Client,
        django_assert_num_queries: DjangoAssertNumQueries,
    ) -> None:
        procedure = ProcedureFactory()
        with django_assert_num_queries(8):
            response = admin_session_client.get(
                reverse("admin:core_procedure_changelist")
            )
        assert response.status_code == 200
        link = f'<a href="{reverse("admin:core_event_changelist", query={"procedure": procedure.id})}" target="_blank">Voir</a>'
        assertContains(response, link)

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
class TestEventList:
    def test_procedure_filter(
        self,
        admin_session_client: Client,
        django_assert_num_queries: DjangoAssertNumQueries,
    ) -> None:
        procedure = ProcedureFactory()
        event_p1 = EventFactory(procedure=procedure)
        event_p2 = EventFactory()

        response = admin_session_client.get(
            f"{reverse('admin:core_event_changelist')}?q={procedure.id}"
        )
        assertNotContains(response, event_p2.pk)
        assertContains(response, event_p1.pk)

        response = admin_session_client.get(
            f"{reverse('admin:core_event_changelist')}?procedure={procedure.id}"
        )
        assertNotContains(response, event_p2.pk)
        assertContains(response, event_p1.pk)

        with django_assert_num_queries(6):
            response = admin_session_client.get(reverse("admin:core_event_changelist"))
        assertContains(response, event_p1.pk)
        assertContains(response, event_p2.pk)


@pytest.mark.django_db
class TestEventChange:
    def test_nominal_case(
        self,
        admin_session_client: Client,
        django_assert_num_queries: DjangoAssertNumQueries,
    ) -> None:
        event = EventFactory()
        with django_assert_num_queries(7):
            response = admin_session_client.get(
                reverse("admin:core_event_change", kwargs={"object_id": event.pk})
            )
        assert response.status_code == 200
        assertContains(response, "Enregistrer et continuer les modifications")

        new_user = ProfileFactory()
        with django_assert_num_queries(UPDATE_BASE_EXPECTED_NUM_QUERIES + 3):
            response = admin_session_client.post(
                reverse("admin:core_event_change", kwargs={"object_id": event.pk}),
                data={
                    "profile": new_user.pk,
                    "_continue": "Enregistrer et continuer les modifications",
                },
                follow=True,
            )
        assert response.status_code == 200

    def test_archive(
        self,
        staff_session_client: Client,
        django_assert_num_queries: DjangoAssertNumQueries,
    ) -> None:
        event = EventFactory()
        with django_assert_num_queries(8):
            response = staff_session_client.get(
                reverse("admin:core_event_change", kwargs={"object_id": event.pk})
            )
        assert response.status_code == 200
        assertContains(response, "Archiver")

        with django_assert_num_queries(UPDATE_BASE_EXPECTED_NUM_QUERIES + 7):
            response = staff_session_client.post(
                reverse("admin:core_event_change", kwargs={"object_id": event.pk}),
                data={
                    "procedure": event.procedure.id,  # required field
                    "_archive": "Archiver",
                },
            )
        assert response.status_code == 302
        event.refresh_from_db()
        assert event.is_archived

        with django_assert_num_queries(9):
            response = staff_session_client.get(
                reverse("admin:core_event_change", kwargs={"object_id": event.pk})
            )
        assert response.status_code == 200
        assertContains(response, "Désarchiver")

    def test_unarchive(
        self,
        staff_session_client: Client,
        django_assert_num_queries: DjangoAssertNumQueries,
    ) -> None:
        event = EventFactory(archived=True)
        with django_assert_num_queries(9):
            response = staff_session_client.get(
                reverse("admin:core_event_change", kwargs={"object_id": event.pk})
            )
        assert response.status_code == 200
        assertContains(response, "Désarchiver")

        with django_assert_num_queries(UPDATE_BASE_EXPECTED_NUM_QUERIES + 7):
            response = staff_session_client.post(
                reverse("admin:core_event_change", kwargs={"object_id": event.pk}),
                data={
                    "procedure": event.procedure.id,  # required field
                    "_unarchive": "Désarchiver",
                },
            )
        assert response.status_code == 302
        event.refresh_from_db()
        assert not event.is_archived

        with django_assert_num_queries(8):
            response = staff_session_client.get(
                reverse("admin:core_event_change", kwargs={"object_id": event.pk})
            )
        assert response.status_code == 200
        assertContains(response, "Archiver")
