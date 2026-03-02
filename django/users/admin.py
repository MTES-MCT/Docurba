# ruff: noqa: ANN001, ARG002
from typing import ClassVar, Literal

from django import forms
from django.contrib import admin
from django.contrib.postgres.fields import ArrayField
from django.contrib.postgres.forms import SimpleArrayField
from django.forms.widgets import TextInput

from users.models import Profile, User


class ProfileAdminForm(forms.ModelForm):
    # Côté collectivité, other_poste accepte du texte libre (pas de choix imposés).
    # On redéfinit le champ pour lever la validation choices du modèle.
    other_poste = SimpleArrayField(
        base_field=forms.CharField(),
        widget=TextInput(attrs={"size": "40"}),
        required=False,
    )

    class Meta:
        model = Profile
        fields = (
            "verified",
            "is_staff",
            "is_admin",
            "firstname",
            "lastname",
            "side",
            "poste",
            "other_poste",
            "collectivite",
            "departement",
            "region",
            "departements",
            "tel",
            "no_signup",
            "successfully_logged_once",
            "optin",
            "updated_pipedrive",
        )

    def _get_validation_exclusions(self) -> set[str]:
        exclude = super()._get_validation_exclusions()
        exclude.add("other_poste")
        return exclude


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    form = ProfileAdminForm
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


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """Les données sont gérées par Supabase."""

    def has_delete_permission(self, request, obj=None) -> Literal[False]:
        return False

    def has_change_permission(self, request, obj=None) -> Literal[False]:
        return False

    def has_add_permission(self, request) -> Literal[False]:
        return False
