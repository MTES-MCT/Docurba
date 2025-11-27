from rest_framework import viewsets

from docurba.core.models import Collectivite, Commune
from docurba.internal_api.serializers import CollectiviteSerializer, CommuneSerializer


class CollectiviteViewSet(viewsets.ReadOnlyModelViewSet):
    """Collectivités en base."""

    queryset = (
        Collectivite.objects.select_related("departement", "departement__region")
        .order_by("code_insee_unique")
        .all()
    )
    serializer_class = CollectiviteSerializer


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
