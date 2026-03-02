from unittest.mock import MagicMock

import pytest
from django.contrib.admin.sites import AdminSite
from django.test import Client
from django.urls import reverse

from users.admin import ProfileAdmin
from users.models import Profile

from .factories import create_user_and_profile


@pytest.mark.django_db
def test_profile_change_page_with_free_text_other_poste(admin_client: Client) -> None:
    _, profile = create_user_and_profile(
        email="sophie.rousselet@atip67.fr", other_poste=["ATIP 67"]
    )
    response = admin_client.get(
        reverse("admin:users_profile_change", kwargs={"object_id": profile.pk})
    )
    assert response.status_code == 200


@pytest.mark.django_db
def test_other_poste_accepts_free_text() -> None:
    _, profile = create_user_and_profile(
        email="tdemolle@agencescalen.fr",
        other_poste=["Agence de développement des territoires"],
    )
    site = AdminSite()
    ma = ProfileAdmin(Profile, site)
    form_class = ma.get_form(request=MagicMock(), obj=profile)
    form = form_class(
        data={
            "side": "collectivite",
            "poste": "autre",
            "other_poste": "Agence de développement des territoires",
        },
        instance=profile,
    )
    assert "other_poste" not in form.errors
