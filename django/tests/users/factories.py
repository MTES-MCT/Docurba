import factory.fuzzy

from docurba.users.enums import PosteType
from docurba.users.models import Profile, Session, User


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    id = factory.Faker("uuid4")
    email = factory.Faker("email")


class SessionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Session

    id = factory.Faker("uuid4")
    user = factory.SubFactory(UserFactory)


class ProfileFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Profile

    user = factory.SubFactory(UserFactory, email=factory.SelfAttribute("..email"))
    email = factory.Faker("email")
    firstname = factory.Faker("first_name", locale="fr_FR")
    lastname = factory.Faker("last_name", locale="fr_FR")
    poste = factory.fuzzy.FuzzyChoice(PosteType)
    other_poste: factory.List([])
