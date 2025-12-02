import uuid
from typing import Any

from tests.factories import _Auto
from users.models import Profile, User

Auto: Any = _Auto()


def create_user_and_profile(
    *, email: str = Auto, other_poste: list = Auto
) -> tuple[User, Profile]:
    user = User.objects.create(id=uuid.uuid4(), email=email)
    profile = Profile.objects.create(user=user, other_poste=other_poste)
    return user, profile
