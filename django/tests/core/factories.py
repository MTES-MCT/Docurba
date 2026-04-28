from csv import DictReader
from pathlib import Path

import factory.fuzzy

from docurba.core.enums import CommuneType
from docurba.core.models import (
    Commune,
    Departement,
    Region,
)


def generate_communes() -> dict:
    # 661 communes
    communes = {}
    # for departement in DEPARTEMENTS_DICT:
    #     for commune in departement["communes"]:
    #         communes[commune["code"]] = {
    #             "name": commune["intitule"],
    #             "departement_insee_code": departement["code"],
    #             "region_insee_code": departement["region"]["code"],
    #         }
    return communes


COMMUNES = generate_communes()

with Path(Path(__file__).parent / "geo_data" / "regions.csv").open(newline="") as f:
    reader = DictReader(f)
    REGIONS = {row["REG"]: row for row in reader}

class RegionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Region
        django_get_or_create = ("code_insee",)

    class Params:
        default_code_insee = factory.fuzzy.FuzzyChoice(REGIONS.keys())

    code_insee = factory.SelfAttribute("default_code_insee")
    nom = factory.LazyAttribute(
        lambda o: (
            REGIONS[o.code_insee]["LIBELLE"]
            if o.code_insee in REGIONS
            else "region_" + o.code_insee
        )
    )


with Path(Path(__file__).parent / "geo_data" / "departements.csv").open(
    newline=""
) as f:
    reader = DictReader(f)
    DEPARTEMENTS = {row["DEP"]: row for row in reader}


class DepartementFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Departement
        django_get_or_create = ("code_insee",)

    class Params:
        default_code_insee = factory.fuzzy.FuzzyChoice(DEPARTEMENTS.keys())

    code_insee = factory.SelfAttribute("default_code_insee")
    nom = factory.LazyAttribute(
        lambda o: (
            DEPARTEMENTS[o.code_insee]["LIBELLE"]
            if o.code_insee in DEPARTEMENTS
            else "departement_" + o.code_insee
        )
    )
    region = factory.SubFactory(
        RegionFactory,
        code_insee=factory.LazyAttribute(
            lambda o: (
                DEPARTEMENTS[o.factory_parent.code_insee]["REG"]
                if o.factory_parent.code_insee in DEPARTEMENTS
                else o.default_code_insee
            )
        ),
    )

with Path(Path(__file__).parent / "geo_data" / "communes.csv").open(newline="") as f:
    reader = DictReader(f)
    COMMUNES = {row["COM"]: row for row in reader}

class CommuneFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Commune
        django_get_or_create = ("code_insee_unique",)

    # Collectivite fields
    code_insee_unique = factory.fuzzy.FuzzyChoice(COMMUNES.keys())
    type = CommuneType.COM  # Don't mess with COMD and COMA
    nom = factory.LazyAttribute(
        lambda o: (
            COMMUNES[o.code_insee_unique]["LIBELLE"]
            if o.code_insee_unique in COMMUNES
            else "commune_" + o.code_insee_unique
        )
    )
    competence_plan = False
    competence_schema = False

    departement = factory.SubFactory(
        DepartementFactory,
        code_insee=factory.LazyAttribute(
            lambda o: (
                COMMUNES[o.factory_parent.code_insee_unique]["DEP"]
                if o.factory_parent.code_insee_unique in COMMUNES
                else o.default_code_insee
            )
        ),
    )

    @factory.lazy_attribute
    def id(self) -> str:
        return f"{self.code_insee_unique}_{self.type}"
