from datetime import timedelta
from urllib.parse import urlencode

import pytest
from django.conf import settings
from django.urls import reverse
from django.utils import timezone
from freezegun import freeze_time
from pytest_django import DjangoAssertNumQueries
from rest_framework.test import APIClient
from syrupy import SnapshotAssertion
from syrupy.matchers import path_value

from docurba.core.enums import EventScope, VisibilityType
from docurba.core.models import Event, EventType
from tests.conftest import SupabaseApiTestClient
from tests.core.factories import (
    EventFactory,
    EventTypeFactory,
    ProcedureFactory,
)
from tests.users.factories import ProfileFactory

BASE_QUERIES_COUNT = 1  # Count made by DRF for the pagination.


@pytest.mark.django_db
class TestEventTypesAPI:
    @pytest.mark.parametrize(
        ("query_params", "expected"),
        [
            pytest.param(
                {},
                [
                    {
                        "id": "00000000-0000-0000-1111-000000000000",
                        "documentType": "CC",
                        "name": "Déroulement des plans de test",
                        "scopeList": [],
                        "scopeSugg": [],
                        "isStructuring": False,
                    },
                    {
                        "id": "00000000-0000-0000-2222-000000000000",
                        "documentType": "PLU",
                        "name": "Echec du déroulement des plans de test",
                        "scopeList": [],
                        "scopeSugg": [],
                        "isStructuring": False,
                    },
                    {
                        "id": "00000000-0000-0000-3333-000000000000",
                        "documentType": "CC",
                        "name": "Succès du déroulement des plans de test",
                        "scopeList": ["pp"],
                        "scopeSugg": ["pp", "ppi"],
                        "isStructuring": False,
                    },
                ],
                id="no_filter",
            ),
            pytest.param(
                {"document_type": "CC"},
                [
                    {
                        "id": "00000000-0000-0000-1111-000000000000",
                        "documentType": "CC",
                        "name": "Déroulement des plans de test",
                        "scopeList": [],
                        "scopeSugg": [],
                        "isStructuring": False,
                    },
                    {
                        "id": "00000000-0000-0000-3333-000000000000",
                        "documentType": "CC",
                        "name": "Succès du déroulement des plans de test",
                        "scopeList": ["pp"],
                        "scopeSugg": ["pp", "ppi"],
                        "isStructuring": False,
                    },
                ],
                id="document_type",
            ),
        ],
    )
    def test_list(
        self,
        api_client: APIClient,
        query_params: dict,
        expected: list,
        django_assert_num_queries: DjangoAssertNumQueries,
    ) -> None:
        EventTypeFactory(
            id="00000000-0000-0000-1111-000000000000",
            document_type=EventType.DocumentType.CC,
            name="Déroulement des plans de test",
        )
        EventTypeFactory(
            id="00000000-0000-0000-2222-000000000000",
            document_type=EventType.DocumentType.PLU,
            name="Echec du déroulement des plans de test",
        )
        EventTypeFactory(
            id="00000000-0000-0000-3333-000000000000",
            document_type=EventType.DocumentType.CC,
            name="Succès du déroulement des plans de test",
            scope_list=[EventScope.PP],
            scope_sugg=[EventScope.PP, EventScope.PPI],
        )
        EventTypeFactory(
            id="00000000-0000-0000-FFFF-000000000000",
            document_type=EventType.DocumentType.CC,
            name="Je suis invisible car désactivé",
            is_active=False,
        )
        url = f"{reverse('internal_api:event_types-list')}?{urlencode(query_params, doseq=True)}"

        with django_assert_num_queries(BASE_QUERIES_COUNT + 1):
            response = api_client.get(url, format="json")

        assert response.status_code == 200
        assert response.json()["results"] == expected

    def test_detail(
        self, api_client: APIClient, django_assert_num_queries: DjangoAssertNumQueries
    ) -> None:
        event_type = EventTypeFactory(
            id="00000000-0000-0000-1111-000000000000",
            document_type=EventType.DocumentType.CC,
            name="Déroulement des plans de test",
            scope_list=[EventScope.PP],
            scope_sugg=[EventScope.PP, EventScope.PPI],
        )

        url = reverse("internal_api:event_types-detail", args=[event_type.pk])
        with django_assert_num_queries(1):
            response = api_client.get(url, format="json")

        assert response.status_code == 200
        assert response.json()
        assert response.json() == {
            "id": "00000000-0000-0000-1111-000000000000",
            "documentType": "CC",
            "name": "Déroulement des plans de test",
            "scopeList": ["pp"],
            "scopeSugg": ["pp", "ppi"],
            "isStructuring": False,
        }


@pytest.mark.django_db
class TestEventAPI:
    def test_event_api_is_forbidden_if_not_authenticated(
        self, api_client: APIClient
    ) -> None:
        list_url = reverse("internal_api:events-list")
        response = api_client.get(list_url, format="json")
        assert response.status_code == 403

        response = api_client.post(list_url, format="json")
        assert response.status_code == 403

        event = EventFactory()
        detail_url = reverse("internal_api:events-detail", args=[event.pk])

        response = api_client.get(detail_url, format="json")
        assert response.status_code == 403

        response = api_client.put(detail_url, format="json")
        assert response.status_code == 403

        response = api_client.patch(detail_url, format="json")
        assert response.status_code == 403

        response = api_client.delete(detail_url, format="json")
        assert response.status_code == 403

    @pytest.mark.parametrize(
        ("query_params", "expected_num_queries"),
        [
            pytest.param(
                {},
                BASE_QUERIES_COUNT + 3,
                id="no_filter",
            ),
            pytest.param(
                {"procedure": "00000000-0000-0000-1111-000000000000"},
                BASE_QUERIES_COUNT + 4,
                id="filter_procedure",
            ),
        ],
    )
    @freeze_time("2012-06-03")
    def test_event_api_list(
        self,
        api_client_with_auth: SupabaseApiTestClient,
        expected_num_queries: int,
        query_params: dict,
        snapshot: SnapshotAssertion,
        django_assert_num_queries: DjangoAssertNumQueries,
    ) -> None:
        now = timezone.now()
        profile = ProfileFactory(for_snapshot=True)
        procedure = ProcedureFactory(
            id="00000000-0000-0000-1111-000000000000",
            project__id="00000000-0000-0000-1111-000000000000",
        )
        EventFactory(
            id="00000000-0000-0000-1111-000000000000",
            procedure=procedure,
            type="",
            event_type=EventTypeFactory(
                id="00000000-0000-0000-1111-000000000000",
                name="test",
                document_type=EventType.DocumentType.CC,
            ),
            profile=profile,
            date_evenement=now - timedelta(days=30),
            description="Lorem ipsum dolor sit amet",
            attachements=[
                {"id": "00000000-1111-0000-0000-000000000000", "name": "test_1.pdf"},
                {"id": "00000000-2222-0000-0000-000000000000", "name": "test_2.pdf"},
            ],
        )
        EventFactory(
            id="00000000-0000-0000-2222-000000000000",
            procedure__id="00000000-0000-0000-2222-000000000000",
            procedure__project__id="00000000-0000-0000-2222-000000000000",
            type="Event Test 2",
            event_type=None,
            date_evenement=now - timedelta(days=25),
        )
        EventFactory(
            id="00000000-0000-0000-3333-000000000000",
            procedure=procedure,
            type="Event Test 3",
            event_type=None,
            date_evenement=now - timedelta(days=20),
        )
        EventFactory(
            id="00000000-0000-0000-4444-000000000000",
            procedure=procedure,
            type="Event Test 4",
            event_type=None,
            date_evenement=now - timedelta(days=15),
            visibility=VisibilityType.PRIVATE,
            from_sudocuh=4444,
            profile=ProfileFactory(
                for_snapshot=True,
                email="admin@docurba.test",
                user__id=settings.SYSTEM_PROFILE_IDS[0],
            ),
            attachements=[
                {"id": "sudocuh/0/00000000000000001.pdf", "name": "test_1.pdf"},
                {"id": "sudocuh/0/00000000000000002.pdf", "name": "test_2.pdf"},
            ],
        )
        EventFactory(procedure=procedure, archived=True)
        url = f"{reverse('internal_api:events-list')}?{urlencode(query_params, doseq=True)}"

        with (
            api_client_with_auth(profile) as api_client,
            django_assert_num_queries(expected_num_queries),
        ):
            response = api_client.get(url, format="json")

        assert response.status_code == 200
        assert response.json()["results"] == snapshot()

    @freeze_time("2012-06-03")
    def test_event_api_create(
        self,
        api_client_with_auth: SupabaseApiTestClient,
        snapshot: SnapshotAssertion,
        django_assert_num_queries: DjangoAssertNumQueries,
    ) -> None:
        profile = ProfileFactory(for_snapshot=True)
        procedure = ProcedureFactory(
            id="00000000-0000-0000-1111-000000000000",
            project__id="00000000-0000-0000-1111-000000000000",
        )
        event_type = EventTypeFactory(
            id="00000000-0000-0000-1111-000000000000",
            name="test",
            document_type=EventType.DocumentType.CC,
        )
        data = {
            "procedureId": procedure.id,
            "otherName": "",
            "eventTypeId": event_type.id,
            "dateEvenement": timezone.now(),
            "description": "Lorem ipsum dolor sit amet",
            "visibility": "public",
            "attachements": [
                {"id": "00000000-1111-0000-0000-000000000000", "name": "test_1.pdf"},
                {"id": "00000000-2222-0000-0000-000000000000", "name": "test_2.pdf"},
            ],
        }
        url = reverse("internal_api:events-list")

        with (
            api_client_with_auth(profile) as api_client,
            django_assert_num_queries(5),
        ):
            response = api_client.post(url, format="json", data=data)

        assert response.status_code == 201
        assert response.json() == snapshot(
            matcher=path_value(
                {
                    "id": r"(.*)",
                    r"attachements\..*\.path": r".*/(.*)/.*",
                },
                types=(str,),
                regex=True,
                replacer=lambda _, match: match[0].replace(
                    match[1], "00000000-1111-0000-0000-000000000000"
                ),
            )
        )

    @freeze_time("2012-06-03")
    def test_event_api_detail(
        self,
        api_client_with_auth: SupabaseApiTestClient,
        snapshot: SnapshotAssertion,
        django_assert_num_queries: DjangoAssertNumQueries,
    ) -> None:
        profile = ProfileFactory(for_snapshot=True)
        event = EventFactory(
            id="00000000-0000-0000-1111-000000000000",
            procedure__id="00000000-0000-0000-1111-000000000000",
            procedure__project__id="00000000-0000-0000-1111-000000000000",
            type="",
            event_type=EventTypeFactory(
                id="00000000-0000-0000-1111-000000000000",
                name="test",
                document_type=EventType.DocumentType.CC,
            ),
            profile=profile,
            date_evenement=timezone.now(),
            description="Lorem ipsum dolor sit amet",
            attachements=[
                {"id": "00000000-1111-0000-0000-000000000000", "name": "test_1.pdf"},
                {"id": "00000000-2222-0000-0000-000000000000", "name": "test_2.pdf"},
            ],
        )

        url = reverse("internal_api:events-detail", args=[event.pk])
        with (
            api_client_with_auth(profile) as api_client,
            django_assert_num_queries(3),
        ):
            response = api_client.get(url, format="json")

        assert response.status_code == 200
        assert response.json() == snapshot()

        event = EventFactory(archived=True)
        url = reverse("internal_api:events-detail", args=[event.pk])

        with (
            api_client_with_auth(profile) as api_client,
            django_assert_num_queries(3),
        ):
            response = api_client.get(url, format="json")

        assert response.status_code == 404

    @freeze_time("2012-06-03")
    def test_event_api_update(
        self,
        api_client_with_auth: SupabaseApiTestClient,
        snapshot: SnapshotAssertion,
        django_assert_num_queries: DjangoAssertNumQueries,
    ) -> None:
        now = timezone.now()
        profile = ProfileFactory(for_snapshot=True)
        event_type = EventTypeFactory(
            id="00000000-0000-0000-1111-000000000000",
            name="test",
            document_type=EventType.DocumentType.CC,
        )
        event = EventFactory(
            id="00000000-0000-0000-2222-000000000000",
            procedure__id="00000000-0000-0000-2222-000000000000",
            procedure__project__id="00000000-0000-0000-2222-000000000000",
            type="Event Test 1",
            date_evenement=now,
            visibility=VisibilityType.PUBLIC,
        )
        data = {
            "eventTypeId": event_type.id,
            "otherName": "",
            "dateEvenement": now - timedelta(days=30),
            "description": "Lorem ipsum dolor sit amet - updated",
            "visibility": "private",
            "attachements": [
                {"id": "00000000-1111-0000-0000-000000000000", "name": "test_1.pdf"},
                {"id": "00000000-2222-0000-0000-000000000000", "name": "test_2.pdf"},
            ],
        }
        url = reverse("internal_api:events-detail", args=[event.pk])
        with (
            api_client_with_auth(profile) as api_client,
            django_assert_num_queries(6),
        ):
            response = api_client.put(url, format="json", data=data)

        assert response.status_code == 200
        assert response.json() == snapshot()

        data = {
            "eventTypeId": None,
            "otherName": "Event Test 1 patched",
            "dateEvenement": now - timedelta(days=20),
            "description": "Lorem ipsum dolor sit amet - patched",
            "visibility": "public",
        }
        url = reverse("internal_api:events-detail", args=[event.pk])
        with (
            api_client_with_auth(profile) as api_client,
            django_assert_num_queries(5),
        ):
            response = api_client.patch(url, format="json", data=data)

        assert response.status_code == 200
        assert response.json() == snapshot()

        event = EventFactory(archived=True)
        url = reverse("internal_api:events-detail", args=[event.pk])
        with (
            api_client_with_auth(profile) as api_client,
            django_assert_num_queries(3),
        ):
            response = api_client.put(url, format="json")

        assert response.status_code == 404

    @freeze_time("2012-06-03")
    def test_event_api_update_procedure_is_not_updated(
        self,
        api_client_with_auth: SupabaseApiTestClient,
        snapshot: SnapshotAssertion,
        django_assert_num_queries: DjangoAssertNumQueries,
    ) -> None:
        profile = ProfileFactory(for_snapshot=True)
        now = timezone.now()
        procedure = ProcedureFactory(id="00000000-0000-0000-1111-000000000000")
        event_type = EventTypeFactory(
            id="00000000-0000-0000-1111-000000000000",
            name="test",
            document_type=EventType.DocumentType.CC,
        )
        event = EventFactory(
            id="00000000-0000-0000-2222-000000000000",
            procedure__id="00000000-0000-0000-2222-000000000000",
            type="Event Test 1",
            date_evenement=now,
            visibility=VisibilityType.PUBLIC,
        )
        data = {
            "procedureId": procedure.id,
            "eventTypeId": event_type.id,
            "otherName": "",
            "dateEvenement": now - timedelta(days=30),
            "description": "Lorem ipsum dolor sit amet - updated",
            "visibility": "private",
        }
        url = reverse("internal_api:events-detail", args=[event.pk])
        with (
            api_client_with_auth(profile) as api_client,
            django_assert_num_queries(6),
        ):
            response = api_client.put(url, format="json", data=data)

        assert response.status_code == 200
        assert response.json() == snapshot()

        data = {
            "procedureId": procedure.id,
        }
        url = reverse("internal_api:events-detail", args=[event.pk])
        with (
            api_client_with_auth(profile) as api_client,
            django_assert_num_queries(5),
        ):
            response = api_client.patch(url, format="json", data=data)

        assert response.status_code == 200
        assert response.json() == snapshot()

    def test_event_api_delete(
        self,
        api_client_with_auth: SupabaseApiTestClient,
        django_assert_num_queries: DjangoAssertNumQueries,
    ) -> None:
        profile = ProfileFactory()
        procedure = ProcedureFactory(id="00000000-0000-0000-1111-000000000000")
        deleted_event = EventFactory(
            id="00000000-0000-0000-1111-000000000000",
            procedure=procedure,
            type="Event Test 1",
        )
        remaining_event = EventFactory(
            id="00000000-0000-0000-2222-000000000000",
            procedure=procedure,
            type="Event Test 2",
        )
        url = reverse("internal_api:events-detail", args=[deleted_event.pk])
        with (
            api_client_with_auth(profile) as api_client,
            django_assert_num_queries(5),
        ):
            response = api_client.delete(url, format="json")

        assert response.status_code == 204
        events = Event.objects.filter(procedure=procedure).exclude_archived()
        assert events.count() == 1
        assert events.first().id == remaining_event.id

        events = Event.full_objects.filter(archived_at__isnull=False)
        assert events.count() == 1
        assert events.first().id == deleted_event.id

        deleted_event = EventFactory(archived=True)
        url = reverse("internal_api:events-detail", args=[deleted_event.pk])
        with (
            api_client_with_auth(profile) as api_client,
            django_assert_num_queries(3),
        ):
            response = api_client.delete(url, format="json")

        assert response.status_code == 404

    @pytest.mark.parametrize(
        ("attachements", "valid"),
        [
            pytest.param([], True),
            pytest.param(
                [
                    {
                        "id": "00000000-0000-0000-1111-000000000000",
                        "name": "test.pdf",
                        "type": "file",
                    }
                ],
                True,
            ),
            pytest.param(
                [
                    {
                        "id": "00000000-0000-0000-1111-000000000000",
                        "name": "test.pdf",
                        "type": "link",
                    }
                ],
                True,
            ),
            pytest.param(
                [
                    {"id": "00000000-0000-0000-1111-000000000000", "name": "test.pdf"},
                    {
                        "id": "00000000-0000-0000-2222-000000000000",
                        "name": "test_2.pdf",
                    },
                ],
                True,
            ),
            pytest.param(None, False),
            pytest.param("None", False),
            pytest.param([None], False),
            pytest.param([{}], False),
            pytest.param(
                [{"id": "00000000-0000-0000-1111-000000000000", "type": "file"}], False
            ),
            pytest.param([{"name": "test.pdf", "type": "file"}], False),
            pytest.param([{"id": None, "name": "test.pdf"}], False),
            pytest.param(
                [
                    {
                        "id": "00000000-0000-0000-1111-000000000000",
                        "name": "test.pdf",
                        "type": "invalid_type",
                    }
                ],
                False,
            ),
        ],
    )
    @freeze_time("2012-06-03")
    def test_event_api_attachements(
        self,
        api_client_with_auth: SupabaseApiTestClient,
        attachements,  # noqa: ANN001
        valid: bool,  # noqa: FBT001
    ) -> None:

        procedure = ProcedureFactory(id="00000000-0000-0000-1111-000000000000")
        data = {
            "procedureId": procedure.id,
            "otherName": "Event Test 1",
            "eventTypeId": None,
            "dateEvenement": timezone.now(),
            "description": "Lorem ipsum dolor sit amet",
            "visibility": "public",
            "attachements": attachements,
        }
        url = reverse("internal_api:events-list")
        with api_client_with_auth(ProfileFactory()) as api_client:
            response = api_client.post(url, format="json", data=data)

        assert response.status_code == 201 if valid else 400


@pytest.mark.django_db
class TestPublicEventAPI:
    def test_public_event_api_is_readonly(self, api_client: APIClient) -> None:
        list_url = reverse("internal_api:events_public-list")

        response = api_client.post(list_url, format="json")
        assert response.status_code == 405

        event = EventFactory()
        detail_url = reverse("internal_api:events_public-detail", args=[event.pk])

        response = api_client.put(detail_url, format="json")
        assert response.status_code == 405

        response = api_client.patch(detail_url, format="json")
        assert response.status_code == 405

        response = api_client.delete(detail_url, format="json")
        assert response.status_code == 405

    @pytest.mark.parametrize(
        ("query_params", "expected_num_queries"),
        [
            pytest.param(
                {},
                BASE_QUERIES_COUNT + 1,
                id="no_filter",
            ),
            pytest.param(
                {"procedure": "00000000-0000-0000-1111-000000000000"},
                BASE_QUERIES_COUNT + 2,
                id="filter_procedure",
            ),
        ],
    )
    @freeze_time("2012-06-03")
    def test_public_event_api_list(
        self,
        api_client: APIClient,
        expected_num_queries: int,
        query_params: dict,
        snapshot: SnapshotAssertion,
        django_assert_num_queries: DjangoAssertNumQueries,
    ) -> None:
        now = timezone.now()
        profile = ProfileFactory(for_snapshot=True)
        procedure = ProcedureFactory(
            id="00000000-0000-0000-1111-000000000000",
            project__id="00000000-0000-0000-1111-000000000000",
        )
        EventFactory(
            id="00000000-0000-0000-1111-000000000000",
            procedure=procedure,
            event_type=EventTypeFactory(
                id="00000000-0000-0000-1111-000000000000",
                name="test",
                document_type=EventType.DocumentType.CC,
            ),
            profile=profile,
            date_evenement=now - timedelta(days=30),
            description="Lorem ipsum dolor sit amet",
            attachements=[
                {"id": "00000000-1111-0000-0000-000000000000", "name": "test_1.pdf"},
                {"id": "00000000-2222-0000-0000-000000000000", "name": "test_2.pdf"},
            ],
        )
        EventFactory(
            id="00000000-0000-0000-2222-000000000000",
            procedure__id="00000000-0000-0000-2222-000000000000",
            procedure__project__id="00000000-0000-0000-2222-000000000000",
            type="Event Test 2",
            event_type=None,
            date_evenement=now - timedelta(days=25),
        )
        EventFactory(
            id="00000000-0000-0000-3333-000000000000",
            procedure=procedure,
            type="Event Test 3",
            event_type=None,
            date_evenement=now - timedelta(days=20),
            profile=ProfileFactory(user__id=settings.SYSTEM_PROFILE_IDS[0]),
        )
        EventFactory(procedure=procedure, archived=True)  # Excluded : archived
        EventFactory(
            procedure=procedure, visibility=VisibilityType.PRIVATE
        )  # Excluded : is_public == False
        EventFactory(
            procedure=procedure,
            visibility=VisibilityType.PRIVATE,
            from_sudocuh=12,
            event_type=None,
        )  # Excluded : is_public == False
        EventFactory(
            procedure=procedure,
            visibility=VisibilityType.PRIVATE,
            from_sudocuh=None,
            event_type__is_structuring=True,
        )  # Excluded : is_public == False
        EventFactory(
            id="00000000-0000-0000-4444-000000000000",
            procedure=procedure,
            visibility=VisibilityType.PRIVATE,
            from_sudocuh=13,
            event_type__id="00000000-0000-0000-4444-000000000000",
            event_type__is_structuring=True,
            event_type__name="event 4444",
            date_evenement=now - timedelta(days=15),
        )  # Ok : is_public == True
        url = f"{reverse('internal_api:events_public-list')}?{urlencode(query_params, doseq=True)}"

        with (
            django_assert_num_queries(expected_num_queries),
        ):
            response = api_client.get(url, format="json")

        assert response.status_code == 200
        assert response.json()["results"] == snapshot()

    @freeze_time("2012-06-03")
    def test_public_event_api_detail(
        self,
        api_client: APIClient,
        snapshot: SnapshotAssertion,
        django_assert_num_queries: DjangoAssertNumQueries,
    ) -> None:
        profile = ProfileFactory(for_snapshot=True)
        event = EventFactory(
            id="00000000-0000-0000-1111-000000000000",
            procedure__id="00000000-0000-0000-1111-000000000000",
            procedure__project__id="00000000-0000-0000-1111-000000000000",
            event_type=EventTypeFactory(
                id="00000000-0000-0000-1111-000000000000",
                name="test",
                document_type=EventType.DocumentType.CC,
            ),
            profile=profile,
            date_evenement=timezone.now(),
            description="Lorem ipsum dolor sit amet",
            attachements=[
                {"id": "00000000-1111-0000-0000-000000000000", "name": "test_1.pdf"},
                {"id": "00000000-2222-0000-0000-000000000000", "name": "test_2.pdf"},
            ],
        )

        url = reverse("internal_api:events_public-detail", args=[event.pk])
        with (
            django_assert_num_queries(1),
        ):
            response = api_client.get(url, format="json")

        assert response.status_code == 200
        assert response.json() == snapshot()

        event = EventFactory(archived=True)
        url = reverse("internal_api:events_public-detail", args=[event.pk])

        with (
            django_assert_num_queries(1),
        ):
            response = api_client.get(url, format="json")

        assert response.status_code == 404
