# ruff: noqa: ARG002
# ruff: noqa: ANN001
# ruff: noqa: RUF012
from typing import ClassVar

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
    readonly_fields = ("commune",)
    fields = ("commune",)


class EventsInline(admin.TabularInline):
    model = Event
    show_change_link = True
    view_on_site = False


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = "__str__", "procedure", "profile", "date_evenement", "is_valid"
    list_select_related = ("profile",)
    search_fields = ("procedure__exact",)
    autocomplete_fields = ("profile",)
    radio_fields: ClassVar = {"visibility": admin.VERTICAL}

    readonly_fields = (
        "id",
        "procedure",
        "from_sudocuh",
        "created_at",
        "updated_at",
        "attachements",
    )
    fields = (
        "id",
        ("procedure", "from_sudocuh"),
        "type",
        "date_evenement",
        ("visibility", "is_valid"),
        "description",
        "profile",
        ("created_at", "updated_at"),
        "attachements",
    )

    def has_add_permission(self, request: object) -> bool:
        return False

    def has_change_permission(self, request: object, obj=None) -> bool:
        return False

    def has_delete_permission(self, request, obj=None) -> bool:
        return False

    def get_queryset(self, request) -> models.QuerySet:
        return (
            super()
            .get_queryset(request)
            .prefetch_related(models.Prefetch("procedure", Procedure.objects.all()))
        )


@admin.register(Procedure)
class ProcedureAdmin(admin.ModelAdmin):
    list_filter = (
        ("parente", admin.EmptyFieldListFilter),
        ("name", admin.EmptyFieldListFilter),
        "doc_type",
    )
    inlines = [ProcedurePerimetreInline, EventsInline]
    list_display = ("__str__", "django_status")
    search_fields = ("pk",)
    fields = [
        "doc_type",
        "type",
        "numero",
        "parente",
        "name",
        "nuxt_status",
        "django_status",
        "collectivite_porteuse",
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

    @admin.display(description="Statut selon Nuxt")
    def nuxt_status(self, obj) -> str:
        return obj.get_status_display() or "-"

    @admin.display(description="Statut selon Django")
    def django_status(self, obj) -> str:
        return obj.statut or "-"
