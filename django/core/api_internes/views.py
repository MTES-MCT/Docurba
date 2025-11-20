# ruff: noqa: ARG002
from typing import Any

from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.request import Request
from rest_framework.response import Response

from core.admin import Commune
from core.api_internes.serializers import CollectiviteSerializer
from core.models import Collectivite


class CollectiviteViewSet(viewsets.ViewSet):
    """Collectivités en base."""

    def list(self, request: Request) -> Response:
        queryset = (
            Collectivite.objects.select_related("departement", "departement__region")
            .order_by("code_insee_unique")
            .all()[:5]
        )
        serializer = CollectiviteSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request: Request, pk: int = Any) -> Response:
        queryset = Collectivite.objects.select_related(
            "departement", "departement__region"
        ).all()
        collectivite = get_object_or_404(queryset, pk=pk)
        serializer = CollectiviteSerializer(collectivite)
        return Response(serializer.data)


class CommuneViewSet(viewsets.ViewSet):
    """Communes en base."""

    def list(self, request: Request) -> Response:
        queryset = (
            Commune.objects.select_related("departement", "departement__region")
            .order_by("code_insee_unique")
            .all()[:5]
        )
        serializer = CollectiviteSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request: Request, pk: int = Any) -> Response:
        queryset = Commune.objects.select_related(
            "departement", "departement__region"
        ).all()
        commune = get_object_or_404(queryset, pk=pk)
        serializer = CollectiviteSerializer(commune)
        return Response(serializer.data)
