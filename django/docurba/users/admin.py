# ruff: noqa: ANN001, ARG002
from typing import ClassVar, Literal

from django.contrib import admin
from django.contrib.postgres.fields import ArrayField
from django.core.exceptions import PermissionDenied
from django.forms.widgets import TextInput
from django.http import HttpResponse
from django.utils.html import format_html

from docurba.users.models import Profile, SupabaseUser


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    readonly_fields = (
        "user",
        "email",  # email doit correspondre à celui connu par Supabase Auth donc on désactive l'édition
    )

    list_display = (
        "__str__",
        "side",
        "departement",
        "collectivite",
        "verified",
        "is_staff",
        "is_admin",
        "email",
    )
    list_select_related = ("departement", "collectivite")
    search_fields = ("email", "firstname", "lastname")
    list_filter = (
        ("collectivite_id", admin.EmptyFieldListFilter),
        "verified",
        "is_staff",
        "side",
        "poste",
        "region",
        "departement",
    )
    autocomplete_fields = ("collectivite",)
    save_on_top = True
    radio_fields: ClassVar = {"side": admin.VERTICAL}
    fields = (
        ("verified", "is_staff", "is_admin"),
        "email",
        ("firstname", "lastname"),
        ("side", "poste", "other_poste"),
        ("collectivite", "departement", "region", "departements"),
        "tel",
        ("no_signup", "successfully_logged_once", "optin", "updated_pipedrive"),
    )
    formfield_overrides: ClassVar = {
        ArrayField: {"widget": TextInput(attrs={"size": "40"})}
    }

    def has_add_permission(self, request) -> Literal[False]:
        return False

    def has_delete_permission(self, request, obj=None) -> Literal[False]:
        return False


@admin.register(SupabaseUser)
class SupabaseUserAdmin(admin.ModelAdmin):
    """Les données sont gérées par Supabase."""

    readonly_fields = (
        "id",
        "email",
        "last_sign_in_at",
    )
    fields = (*readonly_fields,)
    search_fields = ("email",)
    change_form_template = "admin/users/change_user_form.html"

    def response_change(self, request, obj) -> HttpResponse:
        """Add custom "actions" as buttons."""
        if "_update_user_password" in request.POST:
            if request.user.has_perm("users.change_supabaseuser"):
                password = obj.update_password()
                self.message_user(
                    request, format_html("Nouveau mot de passe : {}", password)
                )
                self.log_change(request, obj, "Modification du mot de passe")
            else:
                raise PermissionDenied

        return super().response_change(request, obj)

    def has_delete_permission(self, request, obj=None) -> Literal[False]:
        return False

    def has_add_permission(self, request) -> Literal[False]:
        return False
