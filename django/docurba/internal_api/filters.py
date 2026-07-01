# ruff: noqa: ARG002

import functools

from django.db.models import Q, QuerySet
from django.forms import MultipleChoiceField
from django_filters import rest_framework as filters

from docurba.core.models import (
    Collectivite,
    Commune,
    Departement,
    EventType,
    Region,
    TypeCollectivite,
)


class DepartementRegionFilterSet(filters.FilterSet):
    departement = filters.ModelMultipleChoiceFilter(
        field_name="departement__code_insee",
        to_field_name="code_insee",
        queryset=Departement.objects.all(),
    )
    region = filters.ModelMultipleChoiceFilter(
        field_name="departement__region__code_insee",
        to_field_name="code_insee",
        queryset=Region.objects.all(),
    )
    fields = (
        "departement",
        "region",
    )


# NOTE(cms): we could use the english word "jurisdiction"
# that has the same meaning as "compétence" in French
# but "compétence" is widely used in the existing code.
# Let's bring everything in Django first so that we can quietly
# rename it lately.
COMPETENCES_CHOICES = (
    ("plan", "Plan"),
    ("schema", "Schéma"),
)


class NoValidationMultipleField(MultipleChoiceField):
    def validate(self, value: str) -> None:
        pass


class NoValidationMultipleFilter(filters.MultipleChoiceFilter):
    field_class = NoValidationMultipleField


class CollectiviteFilter(DepartementRegionFilterSet):
    type = filters.MultipleChoiceFilter(field_name="type", choices=TypeCollectivite)
    codes_siren = NoValidationMultipleFilter(
        label="Codes SIREN",
        field_name="code_insee_unique",
    )
    without_communes = filters.BooleanFilter(
        label="Sans les communes", method="_without_communes"
    )
    competence = filters.MultipleChoiceFilter(
        label="Compétence",
        method="_filter_competences",
        choices=COMPETENCES_CHOICES,
    )

    class Meta:
        model = Collectivite
        fields = (
            "type",
            "codes_siren",
            "competence",
            *DepartementRegionFilterSet.fields,
        )

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

    def _without_communes(self, queryset: QuerySet, name: str, value: str) -> QuerySet:
        if not value:
            return queryset
        commune_types = TypeCollectivite.communes()
        return queryset.exclude(type__in=commune_types)


class CommuneFilter(DepartementRegionFilterSet):
    type = filters.MultipleChoiceFilter(
        field_name="type", choices=TypeCollectivite.communes()
    )
    code = NoValidationMultipleFilter(field_name="code_insee_unique")

    class Meta:
        model = Commune
        fields = ("type", "code", *DepartementRegionFilterSet.fields)


class EventTypeFilter(filters.FilterSet):
    class Meta:
        model = EventType
        fields = ("document_type",)
