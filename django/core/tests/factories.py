import itertools
import random
from typing import Any

from core.models import (
    Collectivite,
    Commune,
    Departement,
    Region,
    TypeCollectivite,
)


class _Auto:
    """Sentinel value indicating an automatic default will be used."""

    def __bool__(self) -> bool:
        # Allow `Auto` to be used like `None` or `False` in boolean expressions
        return False


Auto: Any = _Auto()

REGION_CODE_INSEE_SEQUENCE = (f"R{n}" for n in itertools.count())
DEPARTEMENT_CODE_INSEE_SEQUENCE = (f"D{n}" for n in itertools.count())
GROUPEMENT_CODE_INSEE_SEQUENCE = (f"G{n}" for n in itertools.count())


def create_region(*, code_insee: str = Auto) -> Region:
    return Region.objects.create(
        code_insee=code_insee or next(REGION_CODE_INSEE_SEQUENCE)
    )


def create_departement(*, code_insee: str = Auto, region: Region = Auto) -> Departement:
    return Departement.objects.create(
        code_insee=code_insee or next(DEPARTEMENT_CODE_INSEE_SEQUENCE),
        region=region or create_region(),
    )


def create_groupement(
    *,
    code_insee: str = Auto,
    groupement_type: TypeCollectivite = Auto,
    departement: Departement = Auto,
) -> Collectivite:
    code_insee = code_insee or next(GROUPEMENT_CODE_INSEE_SEQUENCE)
    groupement_type = groupement_type or random.choice(list(TypeCollectivite))  # noqa: S311
    return Collectivite.objects.create(
        id=f"{code_insee}_{groupement_type}",
        code_insee_unique=code_insee,
        type=groupement_type,
        departement=departement or create_departement(),
    )


def create_commune(
    *,
    code_insee: str = Auto,
    commune_type: TypeCollectivite = Auto,
    departement: Departement = Auto,
    intercommunalite: Collectivite | None = Auto,
    nouvelle: Commune = Auto,
) -> Commune:
    code_insee = code_insee or next(GROUPEMENT_CODE_INSEE_SEQUENCE)
    commune_type = commune_type or TypeCollectivite.COM
    intercommunalite = (
        create_groupement() if intercommunalite is Auto else intercommunalite
    )

    return Commune.objects.create(
        id=f"{code_insee}_{commune_type}",
        code_insee_unique=code_insee,
        type=commune_type,
        departement=departement or create_departement(),
        intercommunalite=intercommunalite,
        nouvelle=nouvelle or None,
    )
