import uuid

import pytest

from users.models import Profile, User


@pytest.mark.django_db
def test_user_creation() -> None:
    """La table users n'est pas dans le schéma par défaut (public) mais dans `auth`.

    Les schémas PostgreSQL ne semblent pas être très bien pris en charge nativement par Django.
    Nous aurions probablement pu mettre en place un routeur de DB (Database Router) pour rester
    en cohérence avec l'architecture de Django mais cette table disparaîtra avec Supabase.
    Elle existe uniquement car Supabase l'utilise dans sa fonctionnalité SSO.
    Pour le moment, et uniquement pour les tests, créons un schéma `auth`.
    """
    User.objects.create(id=uuid.uuid4(), email="georges-eugene@haussmann.com")
    assert User.objects.count() == 1


@pytest.mark.django_db
def test_profile_creation() -> None:
    user = User.objects.create(id=uuid.uuid4(), email="georges-eugene@haussmann.com")
    profile = Profile.objects.create(user=user, other_poste=["rédacteur", "maire"])
    assert Profile.objects.count() == 1
    assert profile.other_poste == ["rédacteur", "maire"]
