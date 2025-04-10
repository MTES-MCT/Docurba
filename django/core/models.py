import uuid
from datetime import date
from enum import StrEnum, auto
from functools import cached_property
from itertools import groupby
from json import load
from operator import attrgetter
from typing import Self, TypedDict

from django.conf import settings
from django.db import models
from django.db.models.functions import Coalesce

# class CollectiviteLight(TypedDict):
#     type: str
#     intitule: str
#     siren: str
#     code: str


# class Collectivite(CollectiviteLight):
#     regionCode: str
#     departementCode: str
#     competencePLU: bool
#     competenceSCOT: bool
#     groupements: list[CollectiviteLight]
#     membres: list[CollectiviteLight]


# class Commune(Collectivite):
#     codeParent: str
#     intercommunaliteCode: str


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
    APPROUVE = auto()
    ABANDON = auto()
    ANNULE = auto()
    CADUC = auto()


EVENT_IMPACT_BY_TYPE_DOCUMENT = {
    TypeDocument.CC: {
        "Délibération de prescription du conseil municipal": EventImpact.EN_COURS,
        "Approbation du préfet": EventImpact.APPROUVE,
        "Caractère exécutoire": EventImpact.APPROUVE,
        "Retrait de l'annulation totale": EventImpact.APPROUVE,
        "Abandon": EventImpact.ABANDON,
        "Retrait de la délibération de prescription": EventImpact.ABANDON,
        "Annulation TA totale": EventImpact.ANNULE,
        "Annulation TA": EventImpact.ANNULE,
        "Abrogation effective": EventImpact.ANNULE,
    },
    TypeDocument.SCOT: {
        "Délibération de l'établissement public qui prescrit": EventImpact.EN_COURS,
        "Retrait de la délibération d'approbation": EventImpact.EN_COURS,
        "Délibération d'approbation": EventImpact.APPROUVE,
        "Caractère exécutoire": EventImpact.APPROUVE,
        "Retrait de l'annulation totale": EventImpact.APPROUVE,
        "Abandon": EventImpact.ABANDON,
        "Retrait de la délibération de prescription": EventImpact.ABANDON,
        "Annulation TA totale": EventImpact.ANNULE,
        "Annulation TA": EventImpact.ANNULE,
        "Caducité": EventImpact.CADUC,
    },
    TypeDocument.SD: {
        "Délibération de l'établissement public qui prescrit": EventImpact.EN_COURS,
        "Délibération d'approbation": EventImpact.APPROUVE,
        "Caractère exécutoire": EventImpact.APPROUVE,
        "Abandon": EventImpact.ABANDON,
        "Annulation TA totale": EventImpact.ANNULE,
        "Annulation TA": EventImpact.ANNULE,
        "Caducité": EventImpact.CADUC,
    },
    TypeDocument.PLU: {
        "Délibération de prescription du conseil municipal ou communautaire": EventImpact.EN_COURS,
        "Caractère exécutoire": EventImpact.APPROUVE,
        "Retrait de l'annulation totale": EventImpact.APPROUVE,
        "Délibération d'approbation du municipal ou communautaire": EventImpact.APPROUVE,
        "Délibération d'approbation du conseil municipal ou communautaire": EventImpact.APPROUVE,
        "Délibération d'approbation": EventImpact.APPROUVE,
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
        "Caractère exécutoire": EventImpact.APPROUVE,
        "Délibération d'approbation du municipal ou communautaire": EventImpact.APPROUVE,
        "Délibération d'approbation du conseil municipal ou communautaire": EventImpact.APPROUVE,
        "Délibération d'approbation": EventImpact.APPROUVE,
        "Abandon": EventImpact.ABANDON,
        "Annulation TA": EventImpact.ANNULE,
        "Annulation TA totale": EventImpact.ANNULE,
        "Caducité": EventImpact.ANNULE,
    },
}
EVENT_IMPACT_BY_TYPE_DOCUMENT |= dict.fromkeys(
    (TypeDocument.PLUI, TypeDocument.PLUIH, TypeDocument.PLUIHM, TypeDocument.PLUIM),
    EVENT_IMPACT_BY_TYPE_DOCUMENT[TypeDocument.PLU],
)


class ProcedureQuerySet(models.QuerySet):
    def with_events(self, *, avant: date | None = None) -> Self:
        events = Event.objects.all()
        if avant:
            events = events.filter(date_evenement_string__lt=str(avant))

        approbation_event_types = [
            event_type
            for event_impact_by_event_type in EVENT_IMPACT_BY_TYPE_DOCUMENT.values()
            for event_type, event_impact in event_impact_by_event_type.items()
            if event_impact == EventImpact.APPROUVE
        ]

        dernier_event_impactant_whens = [
            models.When(
                type_document=type_document,
                then=models.Subquery(
                    events.filter(
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

        return self.annotate(
            date_approbation=Coalesce(
                models.Subquery(
                    events.filter(
                        procedure=models.OuterRef("pk"),
                        type__in=approbation_event_types,
                    ).values("date_evenement_string")[:1]
                ),
                models.Value("0000-00-00"),
            ),
            dernier_event_impactant=models.Case(*dernier_event_impactant_whens),
        )


class ProcedureManager(models.Manager):
    def get_queryset(self) -> ProcedureQuerySet:
        return super().get_queryset().with_events()


class Procedure(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    type_document = models.CharField(  # noqa: DJ001
        choices=TypeDocument, db_column="doc_type", blank=True, null=True
    )
    parente = models.ForeignKey(
        "self",
        models.CASCADE,
        db_column="secondary_procedure_of",
        related_name="secondaires",
        null=True,
    )
    name = models.TextField(blank=True, null=True)  # noqa: DJ001
    type = models.CharField(blank=True, null=True)  # noqa: DJ001
    numero = models.CharField(blank=True, null=True)  # noqa: DJ001
    collectivite_porteuse_id = models.CharField(blank=True, null=True)  # noqa: DJ001
    created_at = models.DateTimeField(db_default=models.functions.Now())
    doublon_cache_de = models.OneToOneField(
        "self", on_delete=models.DO_NOTHING, blank=True, null=True, unique=True
    )
    soft_delete = models.BooleanField(db_default=False)
    archived = models.GeneratedField(
        expression=models.Q(doublon_cache_de__isnull=False)
        | models.Q(soft_delete=True),
        output_field=models.BooleanField(),
        db_persist=True,
    )

    objects = ProcedureManager.from_queryset(ProcedureQuerySet)()

    class Meta:
        managed = settings.UNDER_TEST
        db_table = "procedures"
        # ordering = ("-date_approbation",)

    def __str__(self) -> str:
        collectivite = f"{self.collectivite_porteuse_id}_COM"
        # if collectivite in communes:
        #     collectivite = communes[collectivite]["intitule"]
        # if self.collectivite_porteuse_id in groupements:
        #     collectivite = groupements[self.collectivite_porteuse_id]["intitule"]
        return (
            self.name
            or f"🤖 {self.type} {self.numero or ''} {self.type_document} {collectivite}"
        )

    def get_absolute_url(self) -> str:
        return f"/frise/{self.pk}"

    @property
    def statut(self) -> EventImpact | None:
        if self.parente_id:
            return None
        if not self.dernier_event_impactant:
            return None

        impact_by_event_type = {
            event_type: event_impact
            for event_impact_by_event_type in EVENT_IMPACT_BY_TYPE_DOCUMENT.values()
            for event_type, event_impact in event_impact_by_event_type.items()
        }
        return impact_by_event_type[self.dernier_event_impactant]

    @property
    def is_schema(self) -> bool:
        return self.type_document in (TypeDocument.SCOT, TypeDocument.SD)


class Event(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    procedure = models.ForeignKey(Procedure, models.DO_NOTHING)
    type = models.TextField(blank=True, null=True)  # noqa: DJ001
    date_evenement_string = models.CharField(db_column="date_iso", null=True)  # noqa: DJ001
    is_valid = models.BooleanField(db_default=True)

    class Meta:
        managed = settings.UNDER_TEST
        db_table = "doc_frise_events"
        ordering = ("-date_evenement_string",)

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
    def with_opposabilite(
        self,
        *,
        departement: str | None = None,
        collectivite_code: str | None = None,
        collectivite_type: str | None = None,
        avant: date | None = None,
    ) -> list["CommuneProcedure"]:
        communes_procedures = (
            self.filter(
                procedure__parente=None,
                procedure__archived=False,
            )
            .prefetch_related(
                models.Prefetch("procedure", Procedure.objects.with_events(avant=avant))
            )
            .order_by("collectivite_code", "collectivite_type")
        )

        if departement:
            communes_procedures = communes_procedures.filter(departement=departement)
        elif collectivite_code and collectivite_type:
            communes_procedures = communes_procedures.filter(
                collectivite_code=collectivite_code, collectivite_type=collectivite_type
            )

        communes_procedures_with_opposabilite = []
        for _, commune_procedures_iterator in groupby(
            communes_procedures, attrgetter("collectivite_code", "collectivite_type")
        ):
            communes_procedures_meme_commune = list(commune_procedures_iterator)
            for commune_procedure in communes_procedures_meme_commune:
                commune_procedure.opposable = commune_procedure._opposable(  # noqa: SLF001
                    communes_procedures_meme_commune
                )
                communes_procedures_with_opposabilite.append(commune_procedure)
        return communes_procedures_with_opposabilite


# ALTER TABLE procedures_perimetres
# ADD commune_id text GENERATED always AS (collectivite_code || '_' || collectivite_type) stored


class CommuneQuerySet(models.QuerySet):
    def with_procedures_principales(self):
        return self.prefetch_related(
            models.Prefetch(
                "procedures",
                Procedure.objects.filter(parente=None, archived=False).order_by(
                    "-date_approbation"
                ),
                to_attr="procedures_principales",
            )
        )


class Commune(models.Model):
    id = models.CharField(primary_key=True)
    procedures = models.ManyToManyField(
        Procedure, through="CommuneProcedure", related_name="perimetre"
    )

    objects = CommuneQuerySet.as_manager()

    class Meta:
        managed = settings.UNDER_TEST

    def __str__(self) -> str:
        return f"Commune {self.id}"

    @cached_property
    def procedures_principales_approuvees(self):
        return [
            procedure
            for procedure in self.procedures_principales
            if procedure.type != "Abrogation"
            and procedure.statut == EventImpact.APPROUVE
        ]

    @cached_property
    def plan_opposable(self):
        return next(
            (
                procedure
                for procedure in self.procedures_principales_approuvees
                if not procedure.is_schema
            ),
            None,
        )

    @cached_property
    def schema_opposable(self):
        return next(
            (
                procedure
                for procedure in self.procedures_principales_approuvees
                if procedure.is_schema
            ),
            None,
        )


class CommuneProcedure(models.Model):
    commune = models.ForeignKey(Commune, models.DO_NOTHING)
    procedure = models.ForeignKey(Procedure, models.DO_NOTHING)

    class Meta:
        managed = settings.UNDER_TEST
        db_table = "procedures_perimetres"
