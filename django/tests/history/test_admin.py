import pytest
from django.test import Client
from django.urls import reverse

from tests.core.factories import EventFactory


@pytest.mark.django_db
class TestEventSnapshotAdmin:
    def test_eventssnapshot_changelist(self, admin_session_client: Client) -> None:
        EventFactory()

        url = reverse("admin:history_eventsnapshot_changelist")
        response = admin_session_client.get(url)
        assert response.status_code == 200
        assert response.context_data["cl"].result_count == 1
