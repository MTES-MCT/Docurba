from json import loads
from pathlib import Path

import factory.fuzzy

from docurba.core.enums import CommuneType
from docurba.core.models import (
    Commune,
    Departement,
    Region,
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
