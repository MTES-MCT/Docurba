# ruff: noqa: ARG002
# ruff: noqa: ANN001
# ruff: noqa: RUF012
from django.contrib import admin
from django.db import models

from core.models import Collectivite, Commune, Event, Procedure


@admin.register(Collectivite)
class CollectiviteAdmin(admin.ModelAdmin):
    list_display = (
        "__str__",
        "type",
        "competence_plan",
        "competence_schema",
    )
    list_filter = ("type", "competence_plan", "competence_schema", "departement")
    search_fields = ("nom", "code_insee_unique")
    readonly_fields = ("commune",)

    def has_add_permission(self, request) -> bool:
        return False

    def has_delete_permission(self, request, obj=None) -> bool:
        return False

    def has_change_permission(self, request, obj=None) -> bool:
        return False


@admin.register(Commune)
class CommuneAdmin(CollectiviteAdmin):
    pass


class ProcedurePerimetreInline(admin.TabularInline):
    model = Procedure.perimetre.through


class EventsInline(admin.TabularInline):
    model = Event


@admin.register(Procedure)
class ProcedureAdmin(admin.ModelAdmin):
    list_filter = (
        ("parente", admin.EmptyFieldListFilter),
        ("name", admin.EmptyFieldListFilter),
        "doc_type",
    )
    inlines = [ProcedurePerimetreInline, EventsInline]
    list_display = ("__str__", "statut")
    search_fields = ("pk",)
    fields = [
        "doc_type",
        "type",
        "numero",
        "parente",
        "name",
        "collectivite_porteuse",
        "statut",
        "commentaire",
        "is_principale",
    ]

    def has_add_permission(self, request: object) -> bool:
        return False

    def has_delete_permission(self, request, obj=None) -> bool:
        return False

    def has_change_permission(self, request, obj=None) -> bool:
        return False

    def get_queryset(self, request) -> models.QuerySet:
        queryset = super().get_queryset(request)
        return queryset.with_events()  # mandatory to set the status.
