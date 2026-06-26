from django.db import models
from rest_framework import viewsets

from docurba.core.models import Collectivite, Commune, MaterializedViewFlatMembership
from docurba.internal_api import filters as custom_filters
from docurba.internal_api.serializers import CollectiviteSerializer, CommuneSerializer


class CollectiviteViewSet(viewsets.ReadOnlyModelViewSet):
    """Collectivités en base."""

    serializer_class = CollectiviteSerializer
    filterset_class = custom_filters.CollectiviteFilter

    def get_serializer_context(self) -> dict:
        context = super().get_serializer_context()
        context.update(
            {"with_members": self.request.query_params.get("with_members", False)}
        )
        return context

    def get_queryset(self):
        qs = Collectivite.objects.select_related("departement", "departement__region")
        if "with_members" in self.get_serializer_context():
            # get Collectivite
            qs = qs.prefetch_related(
                models.Prefetch(
                    "flat_members",
                    queryset=Collectivite.objects.select_related(
                        "departement", "departement__region"
                    ),
                )
            )
        return qs.order_by("code_insee_unique").all()


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
