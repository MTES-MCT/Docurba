import logging
import uuid
from enum import StrEnum, auto
from functools import cached_property
from json import load
from operator import attrgetter
from typing import TypedDict

from django.conf import settings
from django.db import models


class Foo(TypedDict):
    code: str
    siren: str
    type: str
    intitule: str


class Commune(TypedDict):
    code: str
    codeParent: str
    siren: str
    type: str
    intitule: str
    regionCode: str
    intercommunaliteCode: str
    competencePLU: bool
    competenceSCOT: bool
    groupements: list[Foo]
    membres: list[Foo]


with (settings.BASE_DIR / "communes.json").open() as f:
    communes: dict[str, Commune] = {commune["code"]: commune for commune in load(f)}


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


EVENT_IMPACT_BY_DOCUMENT_TYPE = {
    TypeDocumentSimplifie.CC: {
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
    TypeDocumentSimplifie.SCOT: {
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
    TypeDocumentSimplifie.SD: {
        "Délibération de l'établissement public qui prescrit": EventImpact.EN_COURS,
        "Délibération d'approbation": EventImpact.OPPOSABLE,
        "Caractère exécutoire": EventImpact.OPPOSABLE,
        "Abandon": EventImpact.ABANDON,
        "Annulation TA totale": EventImpact.ANNULE,
        "Annulation TA": EventImpact.ANNULE,
        "Caducité": EventImpact.CADUC,
    },
    TypeDocumentSimplifie.PLU: {
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
    TypeDocumentSimplifie.POS: {
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


class Procedure(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    type_document = models.TextField(  # noqa: DJ001
        choices=TypeDocument, db_column="doc_type", blank=True, null=True
    )
    is_principale = models.BooleanField(blank=True, null=True)
    type = models.TextField(blank=True, null=True)  # noqa: DJ001
    numero = models.TextField(blank=True, null=True)  # noqa: DJ001
    collectivite_porteuse_id = models.TextField(blank=True, null=True)  # noqa: DJ001
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
    # name = models.TextField(blank=True, null=True)
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

    class Meta:
        managed = settings.UNDER_TEST
        db_table = "procedures"

    def __str__(self) -> str:
        return str(self.id)
        return (
            self.name
            or f"Gen {self.type} {self.numero or ''} {self.type_document} {communes[self.collectivite_porteuse_id]['intitule']}"
        )

    @property
    def statut(self) -> EventImpact | None:
        if not self.is_principale:
            return None

        return next(
            (event.impact for event in self.event_set.all() if event.impact), None
        )

    @cached_property
    def event_prescription(self) -> "Event | None":
        prescription_event_types = [
            event_type
            for event_type, event_impact in EVENT_IMPACT_BY_DOCUMENT_TYPE[
                self.type_document_simplifie
            ].items()
            if event_impact == EventImpact.EN_COURS
        ]

        return next(
            (
                event
                for event in self.event_set.all()
                if event.type in prescription_event_types
                and event.date_iso < "2025-01-01"
            ),
            None,
        )

    @property
    def date_prescription(self) -> str:
        if not self.event_prescription:
            return "0000-00-00"
        return self.event_prescription.date_iso

    @property
    def type_document_simplifie(self) -> TypeDocumentSimplifie:
        if self.type_document.startswith("PLU"):
            return TypeDocumentSimplifie("PLU")
        return TypeDocumentSimplifie(self.type_document)

    @property
    def is_schema(self) -> bool:
        return self.type_document in (TypeDocument.SCOT, TypeDocument.SD)


class Event(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    procedure = models.ForeignKey(Procedure, models.DO_NOTHING)
    type = models.TextField(blank=True, null=True)  # noqa: DJ001
    date_iso = models.CharField(blank=True, null=True)  # noqa: DJ001

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
    # is_valid = models.BooleanField()
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
        return EVENT_IMPACT_BY_DOCUMENT_TYPE[
            self.procedure.type_document_simplifie
        ].get(self.type)


class CommuneProcedure(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    created_at = models.DateTimeField(db_default=models.functions.Now())
    collectivite_code = models.TextField()
    collectivite_type = models.TextField()
    procedure = models.ForeignKey(
        Procedure, models.DO_NOTHING, related_name="perimetre"
    )
    # opposable = models.BooleanField()
    departement = models.TextField(blank=True, null=True)

    class Meta:
        managed = settings.UNDER_TEST
        db_table = "procedures_perimetres"
        unique_together = (("collectivite_code", "procedure", "collectivite_type"),)

    def __str__(self) -> str:
        return f"{self.collectivite_code} {communes[self.collectivite_code]['intitule']} - {self.procedure}"

    @property
    def opposable(self) -> bool:
        all_procedures = Procedure.objects.prefetch_related("event_set").filter(
            perimetre__collectivite_code=self.collectivite_code
        )
        procedures_opposables = sorted(
            (
                procedure
                for procedure in all_procedures
                if self.procedure.is_schema == procedure.is_schema
                and procedure.statut == EventImpact.OPPOSABLE
            ),
            key=attrgetter("date_prescription"),
        )
        if self.collectivite_code == "56190":
            for p in procedures_opposables:
                logging.warning(f"{p.id=!s} {p.date_prescription=!s}")
        if not procedures_opposables:
            return False
        return procedures_opposables[-1].id == self.procedure_id
