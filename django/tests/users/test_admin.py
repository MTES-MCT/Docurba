import pytest
from django.test import Client
from django.urls import reverse
from pytest_django.asserts import assertContains

from tests.users.factories import UserFactory


@pytest.mark.django_db
class TestUserAdmin:
    def test_change_page(self, admin_session_client: Client) -> None:
        user = UserFactory()

        url = reverse("admin:users_user_change", kwargs={"object_id": user.pk})
        response = admin_session_client.get(url)
        assert response.status_code == 200

    def test_update_password(self, staff_session_client: Client) -> None:
        user = UserFactory()

        url = reverse("admin:users_user_change", kwargs={"object_id": user.pk})
        response = staff_session_client.get(url)

        assertContains(response, "Créer un mot de passe par défaut")

        response = staff_session_client.post(
            url,
            data={"_update_user_password": "Créer+un+mot+de+passe+par+défaut"},
            follow=True,
        )
        assertContains(response, "Nouveau mot de passe :")
