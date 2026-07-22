import pytest
from django.db import connection, transaction

from docurba.users.models import Profile, SupabaseUser

from .factories import ProfileFactory, SupabaseUserFactory


@pytest.mark.django_db
class TestSupabaseUserModel:
    def test_user_creation(self) -> None:
        """La table users n'est pas dans le schéma par défaut (public) mais dans `auth`.

        Les schémas PostgreSQL ne semblent pas être très bien pris en charge nativement par Django.
        Nous aurions probablement pu mettre en place un routeur de DB (Database Router) pour rester
        en cohérence avec l'architecture de Django mais cette table disparaîtra avec Supabase.
        Elle existe uniquement car Supabase l'utilise dans sa fonctionnalité SSO.
        Pour le moment, et uniquement pour les tests, créons un schéma `auth`.
        """
        SupabaseUserFactory()
        assert SupabaseUser.objects.count() == 1

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
                    SELECT (encrypted_password = crypt(%s, encrypted_password)) AS encrypted_password FROM auth.users;
                """,
                [password],
            )
            row = cursor.fetchone()
        assert row[0]


@pytest.mark.django_db
class TestProfileModel:
    def test_profile_creation(self) -> None:
        profile = ProfileFactory(other_poste=["rédacteur", "maire"])
        assert Profile.objects.count() == 1
        assert profile.other_poste == ["rédacteur", "maire"]
