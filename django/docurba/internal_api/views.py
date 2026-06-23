from rest_framework import viewsets

from docurba.core.models import Collectivite, Commune, Event
from docurba.internal_api import filters as custom_filters
from docurba.internal_api.serializers import (
    CollectiviteSerializer,
    CommuneSerializer,
    EventCreateSerializer,
    EventDetailSerializer,
    EventListSerializer,
)


class CollectiviteViewSet(viewsets.ReadOnlyModelViewSet):
    """Collectivités en base."""

    queryset = (
        Collectivite.objects.select_related("departement", "departement__region")
        .order_by("code_insee_unique")
        .all()
    )
    serializer_class = CollectiviteSerializer
    filterset_class = custom_filters.CollectiviteFilter


class CommuneViewSet(viewsets.ReadOnlyModelViewSet):
    """Communes en base."""

    queryset = (
        Commune.objects.select_related(
            "departement",
            "departement__region",
        )
        .order_by("code_insee_unique")
        .all()
    )
    serializer_class = CommuneSerializer
    filterset_class = custom_filters.CommuneFilter


class EventViewSet(viewsets.ModelViewSet):
    """Evenements en base."""

    filterset_class = custom_filters.EventFilter

    def get_queryset(self):
        if self.action == "list":
            return Event.objects.all()
        return Event.full_objects.all()

    def get_serializer_class(self):
        if self.action == "list":
            return EventListSerializer
        if self.action == "create":
            return EventCreateSerializer
        return EventDetailSerializer

        return super().get_serializer_class()
