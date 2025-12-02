# ruff: noqa: ANN001, ARG002
from typing import Literal

from django.contrib import admin

from users.models import Profile, User


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    readonly_fields = ("user",)
    search_fields = ("email",)
    raw_id_fields = ("collectivite",)
    list_filter = ("poste", "side")

    def has_add_permission(self, request) -> Literal[False]:
        return False

    def has_delete_permission(self, request, obj=None) -> Literal[False]:
        return False


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """Les données sont gérées par Supabase."""

    def has_delete_permission(self, request, obj=None) -> Literal[False]:
        return False

    def has_change_permission(self, request, obj=None) -> Literal[False]:
        return False

    def has_add_permission(self, request) -> Literal[False]:
        return False
