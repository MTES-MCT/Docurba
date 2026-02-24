# ruff: noqa: ARG002
# ruff: noqa: ANN001
# ruff: noqa: RUF012
from typing import Any

from django.contrib import admin
from django.db import models
from pghistory.admin import EventModelAdmin

from docurba.core.enums import TypeCollectivite
from docurba.core.models import (
    Collectivite,
    Commune,
    Event,
    EventsSnapshot,
    Procedure,
    Project,
    Topic,
)


@admin.register(Collectivite)
class CollectiviteAdmin(admin.ModelAdmin):
    list_display = (
        "code_insee_unique",
        "__str__",
        "type",
        "competence_plan",
        "competence_schema",
    )
    list_display_links = ("code_insee_unique", "__str__")
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
    readonly_fields = (
        "collectivite_code",
        "collectivite_type",
        "opposable",
        "departement",
        "created_at",
        "added_at",
    )
    fields = [
        *readonly_fields,
    ]

    def get_queryset(self, request) -> models.QuerySet:
        queryset = super().get_queryset(request)
        return queryset.select_related(
            "procedure",
        )

    def has_add_permission(self, *args: list, **kwargs: dict) -> bool:
        return False

    def has_delete_permission(self, *args: list, **kwargs: dict) -> bool:
        return False

    def has_change_permission(self, *args: list, **kwargs: dict) -> bool:
        return False


class EventsInline(admin.TabularInline):
    model = Event
    show_change_link = True
    autocomplete_fields = ("profile",)
    readonly_fields = (
        "id",
        "type",
        "date_evenement",
        "is_valid",
        "visibility",
        "from_sudocuh",
    )
    fields = [
        *readonly_fields,
        *autocomplete_fields,
    ]

    def get_queryset(self, request) -> models.QuerySet:
        queryset = super().get_queryset(request)
        return queryset.select_related(
            "procedure", "procedure__collectivite_porteuse"
        ).prefetch_related("procedure__perimetre")

    def has_add_permission(self, *args: list, **kwargs: dict) -> bool:
        return False

    def has_delete_permission(self, *args: list, **kwargs: dict) -> bool:
        return False

    def has_change_permission(self, request, obj=None) -> bool:
        if obj and bool(obj.from_sudocuh):
            return False
        return super().has_change_permission(request, obj)


class TopicsFilter(admin.SimpleListFilter):
    title = "objet"
    parameter_name = "topic"

    def lookups(self, request, model_admin) -> list[tuple[str, Any]]:
        return [(topic.name, topic.display_name) for topic in Topic.objects.all()]

    def queryset(self, request, queryset) -> models.QuerySet[Any]:
        if not self.value():
            return queryset
        return queryset.filter(topics__name=self.value())


class CollectiviteTypeFilter(admin.SimpleListFilter):
    title = "type de la collectivité porteuse"
    parameter_name = "collectivite_type"

    def lookups(self, request, model_admin) -> list[tuple[str, Any]]:
        return TypeCollectivite.choices

    def queryset(self, request, queryset) -> models.QuerySet[Any]:
        if not self.value():
            return queryset
        return queryset.filter(collectivite_porteuse__type=self.value())


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    search_fields = [
        "id",
    ]

    def has_add_permission(self, request: object) -> bool:
        return False

    def has_change_permission(self, request, obj=None) -> bool:
        return False

    def has_delete_permission(self, request, obj=None) -> bool:
        return False


@admin.register(Procedure)
class ProcedureAdmin(admin.ModelAdmin):
    readonly_fields = (
        "collectivite_porteuse_id",
        "from_sudocuh",
        "doc_type",
        "type",
        "numero",
        "parente",
        "name",
        "nuxt_status",
        "django_status",
        "commentaire",
        "current_perimetre",
        "is_principale",
        "started_before_huwart_law",
        "archived",
    )
    raw_id_fields = ("project",)
    autocomplete_fields = (
        "collectivite_porteuse",
        "owner",
    )
    list_filter = (
        ("parente", admin.EmptyFieldListFilter),
        ("name", admin.EmptyFieldListFilter),
        "doc_type",
        "started_before_huwart_law",
        CollectiviteTypeFilter,
        TopicsFilter,
    )
    inlines = [ProcedurePerimetreInline, EventsInline]
    list_display = ("__str__", "django_status")
    search_fields = ("pk",)
    fields = [
        *autocomplete_fields,
        *readonly_fields,
        *raw_id_fields,
        "soft_delete",
    ]

    def has_add_permission(self, request: object) -> bool:
        return False

    def has_delete_permission(self, request, obj=None) -> bool:
        return False

    def get_queryset(self, request) -> models.QuerySet:
        queryset = super().get_queryset(request)
        return (
            queryset.with_events()  # mandatory to set the status.
            .select_related("collectivite_porteuse")
            .prefetch_related("perimetre")
        )

    @admin.display(description="Statut selon Nuxt")
    def nuxt_status(self, obj) -> str:
        return obj.get_status_display() or "-"

    @admin.display(description="Statut selon Django")
    def django_status(self, obj) -> str:
        return obj.statut or "-"


@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ("display_name", "ui_rank")
    fields = ["display_name", "ui_rank"]

    def has_add_permission(self, request: object) -> bool:
        return False

    def has_delete_permission(self, request, obj=None) -> bool:
        return False

    def has_change_permission(self, request, obj=None) -> bool:
        return False


@admin.register(EventsSnapshot)
class EventSnapshotAdmin(EventModelAdmin):
    list_display = (
        "pgh_obj",
        "pgh_label",
        "pgh_created_at",
        "procedure",
        "profile",
        "date_evenement",
        "is_valid",
    )

    def get_queryset(self, request) -> models.QuerySet:
        return (
            super()
            .get_queryset(request)
            .prefetch_related(models.Prefetch("procedure", Procedure.objects.all()))
        )


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    readonly_fields = (
        "pk",
        "procedure",
        "type",
        "date_evenement",
        "is_valid",
        "visibility",
        "from_sudocuh",
        "description",
        "created_at",
        "updated_at",
        "attachements",
        "actors",
        "is_sudocuh_scot",
        "code",
        "from_sudocuh_procedure_id",
    )
    raw_id_fields = ("project",)
    list_display = ("pk", "created_at")
    list_filter = ("code",)
    search_fields = ("pk",)
    autocomplete_fields = ("profile",)
    fields = [
        *readonly_fields,
        *autocomplete_fields,
    ]

    def has_add_permission(self, request: object) -> bool:
        return False

    def has_delete_permission(self, request: object, obj=None) -> bool:
        return False

    def has_change_permission(self, request: object, obj=None) -> bool:
        if obj and bool(obj.from_sudocuh):
            return False
        return super().has_change_permission(request, obj)

    def get_queryset(self, request) -> models.QuerySet:
        queryset = super().get_queryset(request)
        return (
            queryset.select_related("procedure")
            .select_related("procedure__collectivite_porteuse")
            .prefetch_related("procedure__perimetre")
        )
