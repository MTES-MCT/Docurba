import uuid
from typing import Any

from users.models import Profile, User


class _Auto:
    """Sentinel value indicating an automatic default will be used."""

    def __bool__(self) -> bool:
        # Allow `Auto` to be used like `None` or `False` in boolean expressions
        return False


Auto: Any = _Auto()


def create_user_and_profile(
    *, email: str = Auto, other_poste: list = Auto
) -> tuple[User, Profile]:
    user = User.objects.create(
        id=uuid.uuid4(), email=email or "georges-eugene@haussmann.com"
    )
    profile = Profile.objects.create(
        user=user, other_poste=other_poste or ["rédacteur", "maire"]
    )
    return user, profile
