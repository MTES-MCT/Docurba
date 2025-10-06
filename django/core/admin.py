# ruff: noqa: ARG002
# ruff: noqa: ANN001
# ruff: noqa: RUF012
from django.contrib import admin
from django.db import models

from core.models import Collectivite, Commune, Procedure


@admin.register(Collectivite)
class CollectiviteAdmin(admin.ModelAdmin):
    list_display = (
        "code_insee",
        "__str__",
        "type",
        "competence_plan",
        "competence_schema",
    )
    list_display_links = ("code_insee", "__str__")
    list_filter = ("type", "competence_plan", "competence_schema", "departement")
    search_fields = ("nom", "code_insee")
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


@admin.register(Procedure)
class ProcedureAdmin(admin.ModelAdmin):
    list_filter = (
        ("parente", admin.EmptyFieldListFilter),
        ("name", admin.EmptyFieldListFilter),
        "doc_type",
    )
    list_display = ("__str__", "statut")
    fields = [
        "doc_type",
        "parente",
        "name",
        "collectivite_porteuse",
        "statut",
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
