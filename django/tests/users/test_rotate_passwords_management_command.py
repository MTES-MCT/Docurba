import pytest
from django.core.management import call_command

from docurba.users.models import Profile
from tests.users.factories import ProfileFactory


@pytest.mark.django_db
def test_rotate_passwords() -> None:
    ProfileFactory.create_batch(4, user__encrypted_password="password")  # noqa: S106
    assert "password" in Profile.objects.values_list(
        "user__encrypted_password", flat=True
    )
    call_command("rotate_passwords")
    assert "password" in Profile.objects.values_list(
        "user__encrypted_password", flat=True
    )
    call_command("rotate_passwords", wet_run=True)
    assert "password" not in Profile.objects.values_list(
        "user__encrypted_password", flat=True
    )
