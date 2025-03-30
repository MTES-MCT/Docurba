from django.contrib import admin

from core.models import CommuneProcedure, Procedure


class CommuneProcedureInline(admin.StackedInline):
    model = CommuneProcedure
    extra = 0
    readonly_fields = ("id", "created_at")


@admin.register(Procedure)
class ProcedureAdmin(admin.ModelAdmin):
    readonly_fields = ("id", "created_at")
    list_filter = (
        ("parente", admin.EmptyFieldListFilter),
        ("name", admin.EmptyFieldListFilter),
    )
    list_display = ("__str__", "statut")
    inlines = (CommuneProcedureInline,)
