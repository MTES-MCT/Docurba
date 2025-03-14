import logging
import uuid
from enum import StrEnum, auto
from itertools import groupby
from json import load
from operator import attrgetter
from typing import Self, TypedDict

from django.conf import settings
from django.db import models
from django.db.models.functions import Coalesce


class Foo(TypedDict):
    code: str
    siren: str
    type: str
    intitule: str


class Collectivite(TypedDict):
    type: str
    intitule: str
    siren: str
    code: str
    regionCode: str
    departementCode: str
    competencePLU: bool
    competenceSCOT: bool
    groupements: list[Foo]
    membres: list[Foo]


class Commune(Collectivite):
    codeParent: str
    intercommunaliteCode: str


with (settings.BASE_DIR / "communes.json").open() as f:
    communes: dict[str, Commune] = {
        f"{commune['code']}_{commune['type']}": commune for commune in load(f)
    }
with (settings.BASE_DIR / "groupements.json").open() as f:
    groupements: dict[str, Collectivite] = {
        groupement["code"]: groupement for groupement in load(f)
    }


class TypeDocumentSimplifie(models.TextChoices):
    CC = "CC"
    SCOT = "SCOT"
    SD = "SD"
    PLU = "PLU"
    POS = "POS"


class TypeDocument(models.TextChoices):
    CC = "CC"
    SCOT = "SCOT"
    SD = "SD"
    PLU = "PLU"
    POS = "POS"

    PLUI = "PLUi"
    PLUIH = "PLUiH"
    PLUIHM = "PLUiHM"
    PLUIM = "PLUiM"


class EventImpact(StrEnum):
    EN_COURS = "en cours"
    OPPOSABLE = auto()
    ABANDON = auto()
    ANNULE = auto()
    CADUC = auto()


EVENT_IMPACT_BY_TYPE_DOCUMENT = {
    TypeDocument.CC: {
        "Délibération de prescription du conseil municipal": EventImpact.EN_COURS,
        "Approbation du préfet": EventImpact.OPPOSABLE,
        "Caractère exécutoire": EventImpact.OPPOSABLE,
        "Retrait de l'annulation totale": EventImpact.OPPOSABLE,
        "Abandon": EventImpact.ABANDON,
        "Retrait de la délibération de prescription": EventImpact.ABANDON,
        "Annulation TA totale": EventImpact.ANNULE,
        "Annulation TA": EventImpact.ANNULE,
        "Abrogation effective": EventImpact.ANNULE,
    },
    TypeDocument.SCOT: {
        "Délibération de l'établissement public qui prescrit": EventImpact.EN_COURS,
        "Retrait de la délibération d'approbation": EventImpact.EN_COURS,
        "Délibération d'approbation": EventImpact.OPPOSABLE,
        "Caractère exécutoire": EventImpact.OPPOSABLE,
        "Retrait de l'annulation totale": EventImpact.OPPOSABLE,
        "Abandon": EventImpact.ABANDON,
        "Retrait de la délibération de prescription": EventImpact.ABANDON,
        "Annulation TA totale": EventImpact.ANNULE,
        "Annulation TA": EventImpact.ANNULE,
        "Caducité": EventImpact.CADUC,
    },
    TypeDocument.SD: {
        "Délibération de l'établissement public qui prescrit": EventImpact.EN_COURS,
        "Délibération d'approbation": EventImpact.OPPOSABLE,
        "Caractère exécutoire": EventImpact.OPPOSABLE,
        "Abandon": EventImpact.ABANDON,
        "Annulation TA totale": EventImpact.ANNULE,
        "Annulation TA": EventImpact.ANNULE,
        "Caducité": EventImpact.CADUC,
    },
    TypeDocument.PLU: {
        "Délibération de prescription du conseil municipal ou communautaire": EventImpact.EN_COURS,
        "Caractère exécutoire": EventImpact.OPPOSABLE,
        "Retrait de l'annulation totale": EventImpact.OPPOSABLE,
        "Délibération d'approbation du municipal ou communautaire": EventImpact.OPPOSABLE,
        "Délibération d'approbation du conseil municipal ou communautaire": EventImpact.OPPOSABLE,
        "Délibération d'approbation": EventImpact.OPPOSABLE,
        "Abandon": EventImpact.ABANDON,
        "Retrait de la délibération de prescription": EventImpact.ABANDON,
        "Annulation TA totale": EventImpact.ANNULE,
        "Annulation TA": EventImpact.ANNULE,
        "Abrogation": EventImpact.ANNULE,
        "Arrêté d'abrogation": EventImpact.ANNULE,
        "Caducité": EventImpact.CADUC,
    },
    TypeDocument.POS: {
        "Délibération de prescription du conseil municipal ou communautaire": EventImpact.EN_COURS,
        "Caractère exécutoire": EventImpact.OPPOSABLE,
        "Délibération d'approbation du municipal ou communautaire": EventImpact.OPPOSABLE,
        "Délibération d'approbation du conseil municipal ou communautaire": EventImpact.OPPOSABLE,
        "Délibération d'approbation": EventImpact.OPPOSABLE,
        "Abandon": EventImpact.ABANDON,
        "Annulation TA": EventImpact.ANNULE,
        "Annulation TA totale": EventImpact.ANNULE,
        "Caducité": EventImpact.ANNULE,
    },
}
EVENT_IMPACT_BY_TYPE_DOCUMENT |= {
    plu_like: EVENT_IMPACT_BY_TYPE_DOCUMENT[TypeDocumentSimplifie.PLU]
    for plu_like in (
        TypeDocument.PLUI,
        TypeDocument.PLUIH,
        TypeDocument.PLUIHM,
        TypeDocument.PLUIM,
    )
}


class ProcedureQuerySet(models.QuerySet):
    def with_events(self) -> Self:
        # FIXME : Il va falloir individualiser cela ?
        approbation_event_types = [
            event_type
            for lol in EVENT_IMPACT_BY_TYPE_DOCUMENT.values()
            for event_type, event_impact in lol.items()
            if event_impact == EventImpact.OPPOSABLE
        ]

        # event_types = [
        #     event_type
        #     for lol in EVENT_IMPACT_BY_DOCUMENT_TYPE.values()
        #     for event_type in lol
        # ]

        whens = [
            models.When(
                type_document=type_document,
                then=models.Subquery(
                    Event.objects.filter(
                        procedure=models.OuterRef("pk"),
                        is_valid=True,
                        type__in=event_impact_by_event_type.keys(),
                    ).values("type")[:1]
                ),
            )
            for (
                type_document,
                event_impact_by_event_type,
            ) in EVENT_IMPACT_BY_TYPE_DOCUMENT.items()
        ]

        # whens = [
        #     models.When(
        #         procedure__type_document=type_document,
        #         then=list(event_impact_by_event_type.keys()),
        #     )
        #     for (
        #         type_document,
        #         event_impact_by_event_type,
        #     ) in EVENT_IMPACT_BY_TYPE_DOCUMENT.items()
        # ]

        return self.annotate(
            date_approbation=Coalesce(
                models.Subquery(
                    Event.objects.filter(
                        procedure=models.OuterRef("pk"),
                        type__in=approbation_event_types,
                    ).values("date_iso")[:1]
                ),
                models.Value("0000-00-00"),
            ),
            # dernier_event_impactant=models.Subquery(
            #     Event.objects.filter(
            #         procedure=models.OuterRef("pk"), type__in=event_types, is_valid=True
            #     ).values("type")[:1]
            # ),
            dernier_event_impactant=models.Case(*whens),
            # dernier_event_impactant=models.Subquery(
            #     Event.objects.filter(
            #         procedure=models.OuterRef("pk"),
            #         is_valid=True,
            #         type__in=models.Case(*whens),
            #     ).values("type")[:1]
            # ),
        )


class ProcedureManager(models.Manager):
    def get_queryset(self) -> ProcedureQuerySet:
        return super().get_queryset().with_events()


class Procedure(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    type_document = models.CharField(  # noqa: DJ001
        choices=TypeDocument, db_column="doc_type", blank=True, null=True
    )
    is_principale = models.BooleanField(blank=True, null=True)
    name = models.TextField(blank=True, null=True)  # noqa: DJ001
    type = models.CharField(blank=True, null=True)  # noqa: DJ001
    numero = models.CharField(blank=True, null=True)  # noqa: DJ001
    collectivite_porteuse_id = models.CharField(blank=True, null=True)  # noqa: DJ001
    created_at = models.DateTimeField(db_default=models.functions.Now())

    # project = models.ForeignKey("Projects", models.DO_NOTHING, blank=True, null=True)
    # commentaire = models.TextField(blank=True, null=True)
    # created_at = models.DateTimeField(blank=True, null=True)
    # last_updated_at = models.DateTimeField(blank=True, null=True)
    # from_sudocuh = models.IntegerField(unique=True, blank=True, null=True)
    # status = models.TextField(blank=True, null=True)
    # secondary_procedure_of = models.ForeignKey(
    #     "self",
    #     models.DO_NOTHING,
    #     db_column="secondary_procedure_of",
    #     related_name="secondaires",
    #     blank=True,
    #     null=True,
    # )
    # is_sectoriel = models.BooleanField(blank=True, null=True)
    # is_scot = models.BooleanField(blank=True, null=True)
    # is_pluih = models.BooleanField(blank=True, null=True)
    # is_pdu = models.BooleanField(blank=True, null=True)
    # mandatory_pdu = models.BooleanField(blank=True, null=True)
    # moe = models.JSONField(blank=True, null=True)
    # volet_qualitatif = models.JSONField(blank=True, null=True)
    # sudocu_secondary_procedure_of = models.IntegerField(blank=True, null=True)
    # departements = models.TextField(
    #     blank=True, null=True
    # )  # This field type is a guess.
    # current_perimetre = models.JSONField(blank=True, null=True)
    # initial_perimetre = models.JSONField(blank=True, null=True)
    # is_sudocuh_scot = models.BooleanField(blank=True, null=True)
    # testing = models.BooleanField(blank=True, null=True)
    # # owner = models.ForeignKey("Profiles", models.DO_NOTHING, blank=True, null=True)
    # previous_opposable_procedures_ids = models.ForeignKey(
    #     "self",
    #     models.DO_NOTHING,
    #     db_column="previous_opposable_procedures_ids",
    #     related_name="procedures_previous_opposable_procedures_ids_set",
    #     blank=True,
    #     null=True,
    # )
    # test = models.BooleanField(blank=True, null=True)
    # type_code = models.TextField(blank=True, null=True)
    # doc_type_code = models.TextField(blank=True, null=True)
    # comment_dgd = models.TextField(blank=True, null=True)
    # shareable = models.BooleanField(blank=True, null=True)
    # doublon_cache_de = models.OneToOneField(
    #     "self", on_delete=models.DO_NOTHING, blank=True, null=True, unique=True
    # )
    # soft_delete = models.BooleanField()
    # archived = models.GeneratedField(
    #     expression=models.Q(doublon_cache_de__isnull=False)
    #     | models.Q(soft_delete=True),
    #     output_field=models.BooleanField(),
    #     db_persist=True,
    # )

    objects = ProcedureManager.from_queryset(ProcedureQuerySet)()

    class Meta:
        managed = settings.UNDER_TEST
        db_table = "procedures"

    def __str__(self) -> str:
        collectivite = f"{self.collectivite_porteuse_id}_COM"
        if collectivite in communes:
            collectivite = communes[collectivite]["intitule"]
        if self.collectivite_porteuse_id in groupements:
            collectivite = groupements[self.collectivite_porteuse_id]["intitule"]
        return (
            self.name
            or f"🤖 {self.type} {self.numero or ''} {self.type_document} {collectivite}"
        )

    def get_absolute_url(self) -> str:
        return f"https://docurba.beta.gouv.fr/frise/{self.pk}"

    @property
    def statut(self) -> EventImpact | None:
        if not self.is_principale:
            return None
        if not self.dernier_event_impactant:
            return None

        impact_by_event_type = {
            event_type: event_impact
            for lol in EVENT_IMPACT_BY_TYPE_DOCUMENT.values()
            for event_type, event_impact in lol.items()
        }
        return impact_by_event_type[self.dernier_event_impactant]

    # @property
    # def type_document_simplifie(self) -> TypeDocumentSimplifie:
    #     if self.type_document.startswith("PLU"):
    #         return TypeDocumentSimplifie("PLU")
    #     return TypeDocumentSimplifie(self.type_document)

    @property
    def is_schema(self) -> bool:
        return self.type_document in (TypeDocument.SCOT, TypeDocument.SD)


class Event(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    procedure = models.ForeignKey(Procedure, models.DO_NOTHING)
    type = models.TextField(blank=True, null=True)  # noqa: DJ001
    date_iso = models.CharField(blank=True, null=True)  # noqa: DJ001
    is_valid = models.BooleanField(db_default=True)

    # project = models.ForeignKey("Projects", models.DO_NOTHING, blank=True, null=True)
    # description = models.TextField(blank=True, null=True)
    # created_at = models.DateTimeField(blank=True, null=True)
    # actors = models.TextField(blank=True, null=True)  # This field type is a guess.
    # updated_at = models.DateTimeField(blank=True, null=True)
    # attachements = models.TextField(
    #     blank=True, null=True
    # )  # This field type is a guess.
    # visibility = models.TextField(blank=True, null=True)
    # from_sudocuh = models.IntegerField(unique=True, blank=True, null=True)
    # is_sudocuh_scot = models.BooleanField(blank=True, null=True)
    # profile = models.ForeignKey("Profiles", models.DO_NOTHING, blank=True, null=True)
    # test = models.BooleanField(blank=True, null=True)
    # code = models.TextField(blank=True, null=True)
    # from_sudocuh_procedure_id = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = settings.UNDER_TEST
        db_table = "doc_frise_events"
        ordering = ("-date_iso",)

    def __str__(self) -> str:
        return f"{self.procedure}  - {self.type}"

    @property
    def impact(self) -> EventImpact | None:
        if not self.is_valid:
            return None

        return EVENT_IMPACT_BY_TYPE_DOCUMENT[self.procedure.type_document].get(
            self.type
        )


class CommuneProcedureQuerySet(models.QuerySet):
    def departement(self, departement: str | None = None) -> list["CommuneProcedure"]:
        perimetres = self.prefetch_related(
            models.Prefetch("procedure", Procedure.objects.all())
        ).order_by("collectivite_code", "created_at")

        if departement:
            perimetres = perimetres.filter(departement=departement)

        a = []
        for _, collectivite_perims in groupby(
            perimetres, attrgetter("collectivite_code", "collectivite_type")
        ):
            c = list(collectivite_perims)
            for perim in c:
                perim.opposable = perim._opposable(c)  # noqa: SLF001
                a.append(perim)
        return a

    # FIXME: Non testé
    def collectivite(
        self, collectivite_code: str, collectivite_type: str
    ) -> list["CommuneProcedure"]:
        perimetres = self.prefetch_related(
            models.Prefetch("procedure", Procedure.objects.all())
        ).filter(
            collectivite_code=collectivite_code, collectivite_type=collectivite_type
        )

        for perim in perimetres:
            perim.opposable = perim._opposable(perimetres)
        return perimetres


class CommuneProcedure(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    created_at = models.DateTimeField(db_default=models.functions.Now())
    collectivite_code = models.CharField()
    collectivite_type = models.CharField()
    procedure = models.ForeignKey(
        Procedure, models.DO_NOTHING, related_name="perimetre"
    )
    # opposable = models.BooleanField()
    departement = models.CharField(blank=True, null=True)  # noqa: DJ001

    objects = CommuneProcedureQuerySet.as_manager()

    class Meta:
        managed = settings.UNDER_TEST
        db_table = "procedures_perimetres"
        unique_together = (("collectivite_code", "procedure", "collectivite_type"),)

    def __str__(self) -> str:
        try:
            return f"{self.collectivite_code} {communes[self.collectivite_code]['intitule']} - {self.procedure}"
        except KeyError:
            return f"{self.collectivite_code} - {self.procedure}"

    def _opposable(self, all_perims: list[Self]) -> bool:
        procedures_opposables = sorted(
            (
                perim.procedure
                for perim in all_perims
                if self.procedure.is_schema == perim.procedure.is_schema
                and perim.procedure.type != "Abrogation"
                and perim.procedure.statut == EventImpact.OPPOSABLE
            ),
            key=attrgetter(
                "date_approbation",
                "created_at",  # FIXME Test created_at order
            ),
        )
        if not procedures_opposables:
            return False
        return procedures_opposables[-1].id == self.procedure_id
