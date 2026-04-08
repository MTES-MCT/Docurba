from json import loads
from pathlib import Path

import factory.fuzzy

from docurba.core.enums import CommuneType
from docurba.core.models import (
    Commune,
    CommuneProcedure,
    Departement,
    Procedure,
    Region,
    TypeCollectivite,
    TypeDocument,
)

REGIONS = {
    "76": "Occitanie",
    "84": "Auvergne-Rhône-Alpes",
    "93": "Provence-Alpes-Côte d'Azur",
}

# For the moment, thoses files are copied from Nuxt's middleware to share the same data.
# Same as nuxt/server-middleware/Data/regions.json
# These files have been used when populating the Django tables.
# See the `collectivites_en_base` management command.

# Subset of nuxt/server-middleware/Data/departements.json
# with departements 13, 30 and 84 and their communes.
# TODO: replace by TESTS_DIR
DEPARTEMENTS_DICT = loads(
    Path(Path(__file__).parent / "geo_data" / "departements.json").read_text()
)
DEPARTEMENTS = {
    departement["code"]: {
        "name": departement["intitule"],
        "region_insee_code": departement["region"]["code"],
    }
    for departement in DEPARTEMENTS_DICT
}


def generate_communes() -> dict:
    # 661 communes
    communes = {}
    for departement in DEPARTEMENTS_DICT:
        for commune in departement["communes"]:
            communes[commune["code"]] = {
                "name": commune["intitule"],
                "departement_insee_code": departement["code"],
                "region_insee_code": departement["region"]["code"],
            }
    return communes


COMMUNES = generate_communes()


class RegionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Region
        django_get_or_create = ("code_insee",)

    code_insee = factory.fuzzy.FuzzyChoice(REGIONS.keys())
    nom = factory.LazyAttribute(lambda o: REGIONS[o.code_insee])


class DepartementFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Departement
        django_get_or_create = ("code_insee",)

    code_insee = factory.fuzzy.FuzzyChoice(DEPARTEMENTS.keys())
    region = factory.SubFactory(
        RegionFactory,
        code_insee=factory.LazyAttribute(
            lambda o: DEPARTEMENTS[o.factory_parent.code_insee]["region_insee_code"]
        ),
    )


class CollectiviteFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Commune
        django_get_or_create = ("code_insee_unique",)

    code_insee_unique = "200035087"  # factory.fuzzy.FuzzyChoice(COMMUNES.keys())
    type = TypeCollectivite.CC  # Don't mess with COMD and COMA
    id = factory.LazyFunction(
        lambda: (
            f"{factory.SelfAttribute('code_insee_unique')}_{factory.SelfAttribute('type')}"
        )
    )
    nom = "CA Terre de Provence"  # factory.LazyAttribute(lambda o: COMMUNES[o.code_insee_unique]["name"])
    competence_plan = False
    competence_schema = False
    departement = factory.SubFactory(
        DepartementFactory,
        code_insee="13",
        # code_insee=factory.LazyAttribute(
        #     lambda o: COMMUNES[o.factory_parent.code_insee_unique][
        #         "departement_insee_code"
        #     ]
        # ),
    )


class CommuneFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Commune
        django_get_or_create = ("code_insee_unique",)

    # Collectivite fields
    code_insee_unique = factory.fuzzy.FuzzyChoice(COMMUNES.keys())
    type = CommuneType.COM  # Don't mess with COMD and COMA
    nom = factory.LazyAttribute(lambda o: COMMUNES[o.code_insee_unique]["name"])
    competence_plan = False
    competence_schema = False
    # adhesions = models.ManyToManyField(
    #     "self", related_name="collectivites_adherentes", symmetrical=False
    # )

    # Commune only fields
    # procedures = models.ManyToManyField(
    #     Procedure, through="CommuneProcedure", related_name="perimetre"
    # )
    # TODO: Trait (is optional)
    # intercommunalite = models.ForeignKey(
    #     Collectivite, models.DO_NOTHING, null=True, related_name="communes"
    # )
    # TODO: Trait
    # nouvelle = models.ForeignKey(
    #     "self", models.DO_NOTHING, null=True, related_name="deleguee"
    # )
    # TODO: post_generation because of the Materialized View.
    # adhesions_deep = models.ManyToManyField(
    #     Collectivite,
    #     through="ViewCommuneAdhesionsDeep",
    #     related_name="communes_adherentes_deep",
    # )

    departement = factory.SubFactory(
        DepartementFactory,
        code_insee=factory.LazyAttribute(
            lambda o: COMMUNES[o.factory_parent.code_insee_unique][
                "departement_insee_code"
            ]
        ),
    )

    @factory.lazy_attribute
    def id(self) -> str:
        return f"{self.code_insee_unique}_{self.type}"


class ProcedureFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Procedure

    collectivite_porteuse = factory.SubFactory(CollectiviteFactory)
    doc_type = factory.fuzzy.FuzzyChoice(TypeDocument)

    @factory.post_generation
    def with_perimetre(obj, create, extracted, **kwargs) -> None:
        a = "a"
        if not create:
            return
        perimetre = extracted or CommuneFactory()
        for commune in perimetre:
            CommuneProcedureFactory(
                procedure=obj,
                collectivite_code=commune.code_insee_unique,
                collectivite_type=commune.type,
                departement=commune.departement.code_insee,
            )


class CommuneProcedureFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CommuneProcedure

    procedure = factory.SubFactory(ProcedureFactory)
    collectivite_code = factory.fuzzy.FuzzyChoice(COMMUNES.keys())
    collectivite_type = CommuneType.COM
    opposable = False
    departement = factory.LazyAttribute(
        lambda o: COMMUNES[o.collectivite_code]["departement_insee_code"]
    )
