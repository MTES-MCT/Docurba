from uuid import UUID

from django.db import models
from django.test import Client
from django.test.client import HTTPStatus
from django.urls import reverse

from core.models import Event, EventsSnapshot
from tests.factories import create_procedure


def admin_url(model_or_instance: models.Model, page: str) -> str:
    kwargs = None

    if isinstance(model_or_instance.pk, (UUID, int)):
        kwargs = {"object_id": model_or_instance.pk}
    return reverse(
        f"admin:{model_or_instance._meta.app_label}_{model_or_instance._meta.model_name}_{page}",  # noqa: SLF001
        kwargs=kwargs,
    )


class TestEventAdmin:
    def test_event_changelist(self, admin_client: Client) -> None:
        procedure = create_procedure()
        _dummy_event = procedure.event_set.create(type="Dummy", attachements=[])

        url = admin_url(Event, "changelist")
        response = admin_client.get(url)
        assert response.status_code == HTTPStatus.OK

    def test_event_change(self, admin_client: Client) -> None:
        procedure = create_procedure()
        dummy_event = procedure.event_set.create(type="Dummy", attachements=[])

        url = admin_url(dummy_event, "change")
        response = admin_client.get(url)
        assert response.status_code == HTTPStatus.OK


class TestEventSnapshotAdmin:
    def test_event_changelist(self, admin_client: Client) -> None:
        procedure = create_procedure()
        _dummy_event = procedure.event_set.create(type="Dummy", attachements=[])

        url = admin_url(EventsSnapshot, "changelist")
        response = admin_client.get(url)
        assert response.status_code == HTTPStatus.OK

    def test_event_change(self, admin_client: Client) -> None:
        procedure = create_procedure()
        dummy_event = procedure.event_set.create(type="Dummy", attachements=[])
        snapshot = dummy_event.events.first()

        url = admin_url(snapshot, "change")

        response = admin_client.get(url)
        assert response.status_code == HTTPStatus.OK
