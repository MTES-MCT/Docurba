import pytest
from django.test import Client
from django.urls import reverse
from pytest_django.asserts import assertContains

from docurba.users.models import Profile, User
from tests.users.factories import SupabaseUserFactory


@pytest.mark.django_db
class TestSupabaseUserAdmin:
    def test_change_page(self, admin_session_client: Client) -> None:
        user = SupabaseUserFactory()

        url = reverse("admin:users_supabaseuser_change", kwargs={"object_id": user.pk})
        response = admin_session_client.get(url)
        assert response.status_code == 200

    def test_update_password(self, staff_session_client: Client) -> None:
        user = SupabaseUserFactory()

        url = reverse("admin:users_supabaseuser_change", kwargs={"object_id": user.pk})
        response = staff_session_client.get(url)

        assertContains(response, "Créer un mot de passe par défaut")

        response = staff_session_client.post(
            url,
            data={"_update_user_password": "Créer+un+mot+de+passe+par+défaut"},
            follow=True,
        )
        assertContains(response, "Nouveau mot de passe :")

    # Make sure you remove the test database first
    # because the Django user is not recreated between
    # tests.
    def test_staff_session_client(self, staff_session_client: Client) -> None:
        django_user = User.objects.get(pk=staff_session_client.session["_auth_user_id"])
        assert (
            django_user.profile_id
            == Profile.objects.get(email=django_user.email).user_id
        )

    def test_admin_session_client(self, admin_session_client: Client) -> None:
        django_user = User.objects.get(pk=admin_session_client.session["_auth_user_id"])
        assert (
            django_user.profile_id
            == Profile.objects.get(email=django_user.email).user_id
        )
