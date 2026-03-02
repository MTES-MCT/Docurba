import uuid
from typing import Any

from docurba.users.models import Profile, User
from tests.factories import _Auto

Auto: Any = _Auto()


def create_user_and_profile(
    *, email: str = Auto, other_poste: list = Auto
) -> tuple[User, Profile]:
    user = User.objects.create(id=uuid.uuid4(), email=email)
    profile = Profile.objects.create(user=user, other_poste=other_poste)
    return user, profile
