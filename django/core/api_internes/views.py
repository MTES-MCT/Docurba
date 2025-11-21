# ruff: noqa: ARG002
from typing import Any

from django.db.models import Q
from django.shortcuts import get_object_or_404
from django_filters import rest_framework as filters
from rest_framework import viewsets
from rest_framework.request import Request
from rest_framework.response import Response

from core.admin import Commune
from core.api_internes.serializers import CollectiviteSerializer
from core.models import Collectivite


class CharInFilter(filters.BaseInFilter, filters.CharFilter):
    pass


# class myFilter(FilterSet):
#         id__in = NumberInFilter(field_name='id', lookup_expr='in')

#         class Meta:
#             model = Boat


class CollectiviteFilter(filters.FilterSet):
    departementCode = CharInFilter(
        field_name="departement__code_insee", lookup_expr="in"
    )
    regionCode = filters.CharFilter(field_name="departement__region__code_insee")
    # price__gt = django_filters.NumberFilter(field_name='price', lookup_expr='gt')

    class Meta:
        model = Collectivite
        fields = [
            "departementCode",
            "regionCode",
            "type",
        ]
        # fields = {
        #     'price': ['lt', 'gt'],
        #     'release_date': ['exact', 'year__gt'],
        # }

    def in_filter(self, queryset, name, values):
        # value will contain a list of tags, and we want any movie that at least one of
        # its tag is in the list of provided tags
        query = Q()
        for value in values:
            query |= Q(departement__code_insee__icontains=value)
        if query:
            queryset = queryset.filter(query)

        return queryset


class CollectiviteViewSet(viewsets.ReadOnlyModelViewSet):
    """Collectivités en base."""

    queryset = (
        Collectivite.objects.select_related("departement", "departement__region")
        .order_by("code_insee_unique")
        .all()
    )
    serializer_class = CollectiviteSerializer
    filterset_class = CollectiviteFilter


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
