from json import loads
from pathlib import Path

import factory.fuzzy

from docurba.core.enums import CommuneType
from docurba.core.models import (
    Collectivite,
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
    nom = factory.LazyAttribute(lambda o: DEPARTEMENTS[o.code_insee]["name"])
    region = factory.SubFactory(
        RegionFactory,
        code_insee=factory.LazyAttribute(
            lambda o: DEPARTEMENTS[o.factory_parent.code_insee]["region_insee_code"]
        ),
    )


class CommuneFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Commune
        django_get_or_create = ("code_insee_unique",)

    id = factory.LazyAttribute(lambda o: f"{o.code_insee_unique}_{o.type}")
    code_insee_unique = factory.fuzzy.FuzzyChoice(COMMUNES.keys())
    type = CommuneType.COM  # Don't mess with COMD and COMA
    nom = factory.LazyAttribute(lambda o: COMMUNES[o.code_insee_unique]["name"])
    competence_plan = False
    competence_schema = False

    departement = factory.SubFactory(
        DepartementFactory,
        code_insee=factory.LazyAttribute(
            lambda o: COMMUNES[o.factory_parent.code_insee_unique][
                "departement_insee_code"
            ]
        ),
    )


class CollectiviteFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Collectivite
        django_get_or_create = ("code_insee_unique",)

    id = factory.LazyAttribute(lambda o: f"{o.code_insee_unique}_{o.type}")
    code_insee_unique = factory.Faker("siren", locale="fr_FR")
    type = factory.fuzzy.FuzzyChoice(
        [
            type_groupement
            for type_groupement in TypeCollectivite
            if type_groupement
            not in (TypeCollectivite.COM, TypeCollectivite.COMA, TypeCollectivite.COMD)
        ]
    )

    nom = factory.LazyAttribute(
        lambda o: f"{o.type} {factory.Faker('company', locale='fr_FR')}"
    )
    competence_plan = False
    competence_schema = False
    departement = factory.SubFactory(DepartementFactory)


class ProcedureFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Procedure
        skip_postgeneration_save = True

    collectivite_porteuse = factory.SubFactory(CollectiviteFactory)
    doc_type = factory.fuzzy.FuzzyChoice(TypeDocument)
    type = "Élaboration"
    vaut_PLH = False  # noqa: N815
    vaut_PDM = False  # noqa: N815
    soft_delete = False
    name = factory.LazyAttribute(
        lambda o: f"{o.type} {o.doc_type} {o.collectivite_porteuse.nom}"
    )
    parente = None
    doublon_cache_de = None

    class Params:
        with_parente = factory.Trait(
            parente=factory.SubFactory(
                "tests.core.factories.ProcedureFactory",
                doc_type=factory.SelfAttribute("..doc_type"),
                collectivite_porteuse=factory.SelfAttribute("..collectivite_porteuse"),
            ),
        )
        with_doublon = factory.Trait(
            doublon_cache_de=factory.SubFactory(
                "tests.core.factories.ProcedureFactory",
                doc_type=factory.SelfAttribute("..doc_type"),
                collectivite_porteuse=factory.SelfAttribute("..collectivite_porteuse"),
            ),
        )

    @factory.post_generation
    def with_perimetre(self, create: bool, extracted: list[Commune] | None) -> None:  # noqa: FBT001
        if not create or not extracted:
            return

        for commune in extracted:
            CommuneProcedureFactory(
                procedure=self,
                commune=commune,
            )


class CommuneProcedureFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CommuneProcedure

    commune = factory.SubFactory(CommuneFactory)
    commune_id = factory.LazyAttribute(
        lambda o: f"{o.collectivite_code}_{o.collectivite_type}"
    )
    procedure = factory.SubFactory(ProcedureFactory)
    collectivite_code = factory.SelfAttribute("commune.code_insee_unique")
    collectivite_type = factory.SelfAttribute("commune.type")
    opposable = False
    departement = factory.SelfAttribute("commune.departement.code_insee")
