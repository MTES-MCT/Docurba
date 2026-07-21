# ruff: noqa: ARG002
# ruff: noqa: ANN001
# ruff: noqa: RUF012
from typing import Any

from django.conf import settings
from django.contrib import admin
from django.db import models
from django.forms.models import ModelForm
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.utils.html import format_html

from docurba.core.enums import TypeCollectivite
from docurba.core.models import (
    Collectivite,
    Commune,
    Event,
    EventType,
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
    readonly_fields = (
        "commune",
        "siren",
        "code_insee_unique",
    )
    fields = [
        *readonly_fields,
    ]

    def has_add_permission(self, request) -> bool:
        return False

    def has_delete_permission(self, request, obj=None) -> bool:
        return False

    def has_change_permission(self, request, obj=None) -> bool:
        return False


@admin.register(Commune)
class CommuneAdmin(CollectiviteAdmin):
    change_form_template = "admin/core/commune/procedures.html"

    def get_extra_context(self, object_id) -> dict:
        commune = get_object_or_404(
            Commune.objects.with_procedures_principales(), pk=object_id
        )
        procedures = (
            commune.procedures.filter(parente=None)
            .with_events()
            .order_by("doc_type", "-created_at")
        )
        for procedure in procedures:
            procedure.is_opposable = commune.is_opposable(procedure)
        return {"procedures": procedures}

    # We cant use inlines here as they only work with ForeignKey and not with ForeignObject (CommuneProcedure.commune)
    def change_view(
        self, request, object_id, form_url="", extra_context=None
    ) -> HttpResponse:
        extra_context = extra_context or {}
        extra_context.update(self.get_extra_context(admin.utils.unquote(object_id)))
        return super().change_view(
            request,
            object_id,
            form_url,
            extra_context=extra_context,
        )

    def get_queryset(self, request) -> models.QuerySet:
        queryset = super().get_queryset(request)
        return queryset.with_procedures_principales()

    def get_readonly_fields(self, request, obj=None) -> tuple[str]:
        readonly = super().get_readonly_fields(request, obj)

        return (*readonly, "code_etat_simplifie", "code_etat_complet")

    @admin.display(description="Code état Simplifié")
    def code_etat_simplifie(self, obj) -> str:
        return f"{obj.code_etat_simplifie} - {obj.libelle_code_etat_simplifie}"

    @admin.display(description="Code état Complet")
    def code_etat_complet(self, obj) -> str:
        return f"{obj.code_etat_complet} - {obj.libelle_code_etat_complet}"


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
        "id",
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
    list_display = ("id", "__str__", "django_status")
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


@admin.register(EventType)
class EventTypeAdmin(admin.ModelAdmin):
    readonly_fields = (
        "id",
        "created_at",
        "updated_at",
    )
    editable_fields = (
        "document_type",
        "name",
        "sudocuh_code",
        "sudocuh_name",
        "is_structuring",
        "impact",
        "scope_list",
        "scope_sugg",
        "is_active",
        "order",
    )
    fields = (*editable_fields, *readonly_fields)
    list_editable = (
        "is_structuring",
        "impact",
        "scope_list",
        "scope_sugg",
        "is_active",
        "order",
    )
    list_display = (
        "__str__",
        "sudocuh_code",
        "sudocuh_name",
        *list_editable,
    )
    list_filter = ("document_type", "is_structuring", "impact", "is_active")
    search_fields = ("name", "sudocuh_name", "sudocuh_code")

    def get_queryset(self, request) -> models.QuerySet:
        return self.model.all_objects.get_queryset()

    def has_delete_permission(self, request, obj=None) -> bool:
        return False


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    readonly_fields = (
        "pk",
        "created_at",
        "updated_at",
        "project",
        "attachements",
        "archived_at",
        "archived_by",
        # Data imported from Sudocuh
        "is_valid",
        "from_sudocuh_procedure_id",
    )
    raw_id_fields = ("procedure",)
    list_display = ("pk", "created_at", "archived_at")
    list_filter = ("archived_at", "code")
    search_fields = ("pk",)
    autocomplete_fields = ("profile",)
    historized_fields = (
        "type",
        "code",
        "date_evenement",
        "description",
        "from_sudocuh",
    )
    fields = [
        "visibility",
        *autocomplete_fields,
        *raw_id_fields,
        *historized_fields,
        *readonly_fields,
    ]

    def has_add_permission(self, request: object) -> bool:
        return False

    def has_delete_permission(self, request: object, obj=None) -> bool:
        return False

    def has_change_permission(self, request: object, obj=None) -> bool:
        return super().has_change_permission(request, obj)

    def get_queryset(self, request) -> models.QuerySet:
        queryset = self.model.full_objects.defer_heavy_fields()
        ordering = self.get_ordering(request)
        if ordering:
            queryset = queryset.order_by(*ordering)
        return (
            queryset.select_related("procedure")
            .select_related("procedure__collectivite_porteuse")
            .prefetch_related("procedure__perimetre")
        )

    def get_form(self, request, obj=None, change=False, **kwargs) -> type[ModelForm]:  # noqa: ANN003, FBT002
        form = super().get_form(request, obj=obj, change=change, **kwargs)
        form.base_fields["type"].help_text = format_html(
            """<a href="{}" target="_blank">Voir le tableau des types d'évènements</a>""",
            settings.EVENT_TYPE_HELP_TEXT_URL,
        )
        return form
