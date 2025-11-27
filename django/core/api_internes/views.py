# ruff: noqa: ARG002, RUF012, N815
from rest_framework import viewsets

from core.admin import Commune
from core.api_internes import filters as custom_filters
from core.api_internes.serializers import CollectiviteSerializer, CommuneSerializer
from core.models import Collectivite


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
