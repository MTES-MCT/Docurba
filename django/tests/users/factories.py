import uuid

import factory.fuzzy

from docurba.users.enums import PosteType
from docurba.users.models import Profile, SupabaseUser


class SupabaseUserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = SupabaseUser

    class Params:
        for_snapshot = factory.Trait(
            id=uuid.UUID("1cd65b57-7027-4aa5-8d19-5e1baf8d6f09"),
        )

    id = factory.Faker("uuid4")
    email = factory.Faker("email")


class ProfileFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Profile
        skip_postgeneration_save = True

    class Params:
        for_snapshot = factory.Trait(user__for_snapshot=True)

    user = factory.SubFactory(
        SupabaseUserFactory, email=factory.SelfAttribute("..email")
    )
    email = factory.Faker("email")
    firstname = factory.Faker("first_name", locale="fr_FR")
    lastname = factory.Faker("last_name", locale="fr_FR")
    poste = factory.fuzzy.FuzzyChoice(PosteType)
    other_poste: factory.List([])
    collectivite = factory.SubFactory("tests.core.factories.CollectiviteFactory")
    departement = factory.SubFactory("tests.core.factories.DepartementFactory")
