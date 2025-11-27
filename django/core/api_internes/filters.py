# ruff: noqa: ARG002, RUF012, N815

import functools

from django.db.models import Q, QuerySet
from django_filters import rest_framework as filters

from core.models import Collectivite, Commune, TypeCollectivite


class CharInFilter(filters.BaseInFilter, filters.CharFilter):
    def in_filter(self, queryset: QuerySet, name: str, values: list) -> QuerySet:
        query = Q()
        for value in values:
            query |= Q(departement__code_insee__icontains=value)
        if query:
            queryset = queryset.filter(query)

        return queryset


class DepartementRegionFilterSet(filters.FilterSet):
    departement = CharInFilter(field_name="departement__code_insee", lookup_expr="in")
    region = CharInFilter(field_name="departement__region__code_insee")
    fields = (
        "departement",
        "region",
    )


COMPETENCES_CHOICES = (
    ("plan", "Plan"),
    ("schema", "Schéma"),
)


class CollectiviteFilter(DepartementRegionFilterSet):
    type = CharInFilter(field_name="type")
    exclude_communes = filters.BooleanFilter(method="_exclude_communes")
    competence = filters.MultipleChoiceFilter(
        method="_filter_competences", choices=COMPETENCES_CHOICES
    )

    class Meta:
        model = Collectivite
        fields = ("type", "competence", *DepartementRegionFilterSet.fields)

    def _filter_competences(
        self, queryset: QuerySet, name: str, values: str
    ) -> QuerySet:
        if not values:
            return queryset
        queries = []
        for value in values:
            if value == "plan":
                queries.append(Q(competence_plan=True))
            if value == "schema":
                queries.append(Q(competence_schema=True))

        return queryset.filter(functools.reduce(Q.__or__, queries))

    def _exclude_communes(self, queryset: QuerySet, name: str, value: str) -> QuerySet:
        if not value:
            return queryset
        commune_types = [
            TypeCollectivite.COM,
            TypeCollectivite.COMA,
            TypeCollectivite.COMD,
        ]
        return queryset.exclude(type__in=commune_types)


class CommuneFilter(DepartementRegionFilterSet):
    type = CharInFilter(field_name="type")

    class Meta:
        model = Commune
        fields = ("type", *DepartementRegionFilterSet.fields)
