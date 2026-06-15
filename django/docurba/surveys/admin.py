# ruff: noqa: ARG002
# ruff: noqa: ANN001
# ruff: noqa: RUF012

from typing import Any

from django.contrib import admin
from django.db import models

from docurba.core.enums import TypeCollectivite
from docurba.core.models import (
    Departement,
)
from docurba.surveys.models import (
    ProcedureSurvey,
    Survey,
)


@admin.register(Survey)
class SurveyAdmin(admin.ModelAdmin):
    readonly_fields = ("created_at",)
    list_display = ("name", *readonly_fields)
    fields = ["name", "created_at"]

    def has_delete_permission(self, request, obj=None) -> bool:
        return False

    def has_change_permission(self, request, obj=None) -> bool:
        return False


class DepartementsFilter(admin.SimpleListFilter):
    title = "departement"
    parameter_name = "departement"

    def lookups(self, request, model_admin) -> list[tuple[str, Any]]:
        return [("None", "Sans département")] + [
            (departement.code_insee, departement.nom)
            for departement in Departement.objects.all()
        ]

    def queryset(self, request, queryset) -> models.QuerySet[Any]:
        if not self.value():
            return queryset
        if self.value() == "None":
            return queryset.filter(departements__isnull=True)
        return queryset.filter(departements__contains=[self.value()])


class CollectiviteTypeFilter(admin.SimpleListFilter):
    title = "type de la collectivité"
    parameter_name = "collectivite_type"

    def lookups(self, request, model_admin) -> list[tuple[str, Any]]:
        return TypeCollectivite.choices

    def queryset(self, request, queryset) -> models.QuerySet[Any]:
        if not self.value():
            return queryset
        return queryset.filter(collectivite_code__type=self.value())


@admin.register(ProcedureSurvey)
class ProcedureSurveyAdmin(admin.ModelAdmin):
    list_display = ("procedure", "procedure_id", "is_validated")
    readonly_fields = (
        "created_at",
        "responded_at",
        "survey",
        "procedure",
    )
    raw_id_fields = ("respondant",)
    autocomplete_fields = ("collectivite_code",)
    fields = (
        "departements",
        "is_validated",
        *readonly_fields,
        *raw_id_fields,
        *autocomplete_fields,
    )
    search_fields = ("procedure__id", "collectivite_code__code_insee_unique")
    list_filter = ("is_validated", DepartementsFilter, CollectiviteTypeFilter)

    def get_queryset(self, request) -> models.QuerySet:
        queryset = super().get_queryset(request)
        return queryset.select_related(
            "procedure",
            "survey",
            "collectivite_code",
            "procedure__collectivite_porteuse",
        ).prefetch_related("procedure__perimetre")
