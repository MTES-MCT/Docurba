import pytest
from django.db import connection, transaction

from .factories import SupabaseUserFactory


@pytest.mark.django_db
class TestSupabaseUserModel:
    def test_update_password(self) -> None:
        user = SupabaseUserFactory()
        assert not user.encrypted_password
        password = "ARandomPassword"  # noqa: S105
        user.update_password(password=password)
        user.refresh_from_db()

        assert user.encrypted_password

        with connection.cursor() as cursor, transaction.atomic():
            cursor.execute(
                """
                    SELECT (encrypted_password = crypt(%s, encrypted_password)) AS encrypted_password FROM auth.users where id=%s;
                """,
                [password, user.id],
            )
            row = cursor.fetchone()
        assert row[0]
