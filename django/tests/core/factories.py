import datetime
import string
import uuid
from json import loads
from pathlib import Path

import factory.fuzzy
from django.utils import timezone
from factory.random import randgen

from docurba.core.enums import CommuneType
from docurba.core.models import (
    EVENT_CATEGORY_BY_DOC_TYPE,
    EVENT_TYPE_BY_EVENT_CATEGORY,
    Collectivite,
    Commune,
    CommuneProcedure,
    Departement,
    Event,
    EventType,
    MaterializedViewFlatMembership,
    Procedure,
    ProcedureStatusChoices,
    Project,
    Region,
    TypeCollectivite,
    TypeDocument,
)
from tests.users.factories import ProfileFactory

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
    class Params:
        for_snapshot = factory.Trait(
            code_insee="76",
            nom="Occitanie",
        )

    class Meta:
        model = Region
        django_get_or_create = ("code_insee",)

    code_insee = factory.fuzzy.FuzzyChoice(REGIONS.keys())
    nom = factory.LazyAttribute(lambda o: REGIONS[o.code_insee])


class DepartementFactory(factory.django.DjangoModelFactory):
    class Params:
        for_snapshot = factory.Trait(
            code_insee="30",
            nom="Gard",
            region=factory.SubFactory(RegionFactory, for_snapshot=True),
        )

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
    class Params:
        for_snapshot = factory.Trait(
            code_insee="30032",
            type=CommuneType.COM,
            nom="Beaucaire",
            departement__for_snapshot=True,
        )

    class Meta:
        model = Commune
        django_get_or_create = ("code_insee_unique",)

    id = factory.LazyAttribute(lambda o: f"{o.code_insee_unique}_{o.type}")
    code_insee_unique = factory.LazyAttribute(lambda o: f"{o.code_insee}")
    code_insee = factory.fuzzy.FuzzyChoice(COMMUNES.keys())
    type = CommuneType.COM  # Don't mess with COMD and COMA
    nom = factory.LazyAttribute(lambda o: COMMUNES[o.code_insee_unique]["name"])
    competence_plan = False
    competence_schema = False

    departement = factory.SubFactory(
        DepartementFactory,
        code_insee=factory.LazyAttribute(
            lambda o: COMMUNES[o.factory_parent.code_insee]["departement_insee_code"]
        ),
    )


class CollectiviteFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Collectivite
        django_get_or_create = ("code_insee_unique",)
        skip_postgeneration_save = True

    class Params:
        for_snapshot = factory.Trait(
            siren="253000020",
            type=TypeCollectivite.SMO,
            nom="Syndicat mixte d'équipement de la commune de Beaucaire",
            departement__for_snapshot=True,
        )

    id = factory.LazyAttribute(lambda o: f"{o.code_insee_unique}_{o.type}")
    code_insee_unique = factory.LazyAttribute(lambda o: f"{o.siren}")
    # NOTE(cms): don't add a code_insee attribute because we don't have
    # communes as collectivite for the moment.
    # We should create a child class but it should be reflected in models.
    siren = factory.fuzzy.FuzzyText(length=8, chars=string.digits, prefix="1")
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

    @factory.post_generation
    def with_members(
        self,
        create: bool,  # noqa: FBT001
        extracted: list[Collectivite] | None,
        **extra: dict,
    ) -> None:
        if not create or not extracted:
            return
        members_list = extra.get("list") or CollectiviteFactory.create_batch(2)
        self.collectivites_adherentes.add(*members_list)
        MaterializedViewFlatMembership.refresh()

    @factory.post_generation
    def with_flat_members(self, create: bool, extracted: bool, **extra: dict) -> None:  # noqa: FBT001
        if not create or not extracted:
            return
        child = None
        grand_children = []
        if extra.get("for_snapshot", False):
            child = CollectiviteFactory(
                type=TypeCollectivite.CC,
                departement__code_insee="30",
                nom="CC Beaucaire Terre d'Argence",
                siren="243000585",
            )
            communes_attrs = (
                (TypeCollectivite.COM, "Beaucaire", "30032"),
                (TypeCollectivite.COM, "Bellegarde", "30034"),
                (TypeCollectivite.COM, "Fourques", "30117"),
                (TypeCollectivite.COM, "Jonquières-Saint-Vincent", "30135"),
                (TypeCollectivite.COM, "Vallabrègues", "30336"),
            )
            for attr in communes_attrs:
                grand_child = CommuneFactory(
                    type=attr[0],
                    departement__code_insee="30",
                    nom=attr[1],
                    code_insee=attr[2],
                )
                grand_children.append(grand_child)
        else:
            child = CollectiviteFactory(departement__code_insee="30")
            grand_children.append(CollectiviteFactory(departement__code_insee="30"))

        self.collectivites_adherentes.add(*[child])
        child.collectivites_adherentes.add(*grand_children)

        MaterializedViewFlatMembership.refresh()


class ProjectFactory(factory.django.DjangoModelFactory):
    name = factory.Faker("sentence")
    collectivite = factory.SubFactory(CollectiviteFactory)
    collectivite_porteuse = factory.SubFactory(CollectiviteFactory)
    owner = factory.SubFactory(ProfileFactory)

    class Params:
        for_snapshot = factory.Trait(
            name="Projet d'élaboration du PLU de Nantes",
        )

    class Meta:
        model = Project


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
    project = factory.SubFactory(ProjectFactory)

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
        for_snapshot = factory.Trait(
            pk=uuid.UUID("1cd65b57-7027-4aa5-8d19-5e1baf8d6f09"),
            collectivite_porteuse__for_snapshot=True,
            doc_type=TypeDocument.PLU,
            name="Élaboration du PLU de Nantes",
            project__for_snapshot=True,
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

    @factory.post_generation
    def with_event(self, create: bool, extracted: bool, **extra: dict) -> None:  # noqa: FBT001
        if not create or not extracted:
            return

        event_type = extra.pop("type", None) or "Prescription"
        if extra.get("category"):
            event_type = EVENT_TYPE_BY_EVENT_CATEGORY[self.doc_type][
                extra.pop("category")
            ][0]

        EventFactory(procedure=self, type=event_type, **extra)


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


class EventTypeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = EventType

    name = factory.LazyAttribute(
        lambda o: randgen.choice(
            list(EVENT_CATEGORY_BY_DOC_TYPE[o.document_type].keys())
        )
    )
    document_type = factory.fuzzy.FuzzyChoice(EventType.DocumentType)
    impact = factory.fuzzy.FuzzyChoice(ProcedureStatusChoices)


class EventFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Event

    procedure = factory.SubFactory(ProcedureFactory)
    date_evenement = factory.fuzzy.FuzzyDate(datetime.date(1970, 1, 1))
    type = "Prescription"
    from_sudocuh = None

    archived_at = None
    archived_by = None

    class Params:
        archived = factory.Trait(
            archived_at=timezone.now(), archived_by=factory.SubFactory(ProfileFactory)
        )
