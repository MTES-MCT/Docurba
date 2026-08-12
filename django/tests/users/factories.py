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
        skip_postgeneration_save = True

    user = factory.SubFactory(
        SupabaseUserFactory, email=factory.SelfAttribute("..email")
    )
    email = factory.Faker("email")
    firstname = factory.Faker("first_name", locale="fr_FR")
    lastname = factory.Faker("last_name", locale="fr_FR")
    poste = factory.fuzzy.FuzzyChoice(PosteType)
    other_poste: factory.List([])

    @factory.post_generation
    def with_collectivite(self, create: bool, extracted: bool, **extra: dict) -> None:  # noqa: FBT001
        if not create or not extracted:
            return

        # avoid circular import
        from tests.core.factories import CollectiviteFactory  # noqa: PLC0415

        self.collectivite = extra.pop("collectivite", CollectiviteFactory())
