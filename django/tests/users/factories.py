import factory.fuzzy

from docurba.users.enums import PosteType
from docurba.users.models import Profile, Session, SupabaseUser


class SupabaseUserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = SupabaseUser

    id = factory.Faker("uuid4")
    email = factory.Faker("email")


class SessionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Session

    id = factory.Faker("uuid4")
    user = factory.SubFactory(SupabaseUserFactory)


class ProfileFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Profile

    user = factory.SubFactory(
        SupabaseUserFactory, email=factory.SelfAttribute("..email")
    )
    email = factory.Faker("email")
    firstname = factory.Faker("first_name", locale="fr_FR")
    lastname = factory.Faker("last_name", locale="fr_FR")
    poste = factory.fuzzy.FuzzyChoice(PosteType)
    other_poste: factory.List([])
