import logging
import uuid
from datetime import date
from enum import StrEnum, auto
from functools import cached_property
from typing import Self

from django.conf import settings
from django.db import models
from django.db.models.functions import Coalesce
from django.db.models.lookups import GreaterThan
from django.urls import reverse


class TypeCollectivite(models.TextChoices):
    COM = "COM", "Commune"
    COMD = "COMD", "Commune déléguée"
    COMA = "COMA", "Commune associée"
    CC = "CC", "Communauté de communes"
    SMF = "SMF", "Syndicat Mixte Fermé"
    SMO = "SMO", "Syndicat Mixte Ouvert"
    METRO = "METRO", "Métropole"
    CU = "CU", "Communauté Urbaine"
    PETR = "PETR", "Pôle d'Équilibre Territorial et Rural"
    MET69 = "MET69", "Métropole de Lyon"
    SIVU = "SIVU", "Syndicat Intercommunal à Vocation Unique"
    EPT = "EPT", "Établissement Public Territorial"
    CA = "CA", "Communauté d'Agglomération"
    POLEM = "POLEM", "Pôle Métropolitain"
    SIVOM = "SIVOM", "Syndicat Intercommunal à Vocation Multiple"


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


PLU_LIKE = (
    TypeDocument.PLUI,
    TypeDocument.PLUIH,
    TypeDocument.PLUIHM,
    TypeDocument.PLUIM,
)


class EventImpact(StrEnum):
    EN_COURS = "en cours"
    APPROUVE = auto()
    ABANDON = auto()
    ANNULE = auto()
    CADUC = auto()


class EventNotable(StrEnum):
    ARRET_DE_PROJET = auto()
    PORTER_A_CONNAISSANCE = auto()
    PORTER_A_CONNAISSANCE_COMPLEMENTAIRE = auto()
    DELIBERATION = auto()
    PUBLICATION_PERIMETRE = auto()
    CARACTERE_EXECUTOIRE = auto()
    FIN_ECHEANCE = auto()


# https://docs.google.com/spreadsheets/d/1NEcWazdx7LvpnydcyP4pBdFWl9fI_Iu9zy9AQcDtll0/edit?gid=637043323#gid=637043323
EVENT_IMPACT_BY_DOC_TYPE = {
    TypeDocument.CC: {
        "Délibération de prescription du conseil municipal": EventImpact.EN_COURS,
        "Approbation du préfet": EventImpact.APPROUVE,
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
        "Abandon": EventImpact.ABANDON,
        "Annulation TA totale": EventImpact.ANNULE,
        "Annulation TA": EventImpact.ANNULE,
        "Caducité": EventImpact.CADUC,
    },
    TypeDocument.PLU: {
        "Délibération de prescription du conseil municipal ou communautaire": EventImpact.EN_COURS,
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
        "Délibération d'approbation du municipal ou communautaire": EventImpact.APPROUVE,
        "Délibération d'approbation du conseil municipal ou communautaire": EventImpact.APPROUVE,
        "Délibération d'approbation": EventImpact.APPROUVE,
        "Abandon": EventImpact.ABANDON,
        "Annulation TA": EventImpact.ANNULE,
        "Annulation TA totale": EventImpact.ANNULE,
        "Caducité": EventImpact.ANNULE,
    },
}
EVENT_IMPACT_BY_DOC_TYPE |= dict.fromkeys(
    PLU_LIKE, EVENT_IMPACT_BY_DOC_TYPE[TypeDocument.PLU]
)

EVENT_NOTABLE_BY_DOC_TYPE = {
    TypeDocument.SCOT: {
        "Arrêt de projet": EventNotable.ARRET_DE_PROJET,
        "Porter à connaissance": EventNotable.PORTER_A_CONNAISSANCE,
        "Porter à connaissance complémentaire": EventNotable.PORTER_A_CONNAISSANCE_COMPLEMENTAIRE,
        "Délibération de l'Etab Pub sur les modalités de concertation": EventNotable.DELIBERATION,
        "Délibération de l'Etablissement Public": EventNotable.DELIBERATION,
        "Publication de périmètre": EventNotable.PUBLICATION_PERIMETRE,
        "Publication périmètre": EventNotable.PUBLICATION_PERIMETRE,
        "Caractère exécutoire": EventNotable.CARACTERE_EXECUTOIRE,
        "Fin d'échéance": EventNotable.FIN_ECHEANCE,
    }
}


class ProcedureQuerySet(models.QuerySet):
    def with_events(self, *, avant: date | None = None) -> Self:
        events = Event.objects.filter(is_valid=True)
        if avant:
            events = events.filter(date_evenement_string__lt=str(avant))

        approbation_event_types = [
            event_type
            for event_impact_by_event_type in EVENT_IMPACT_BY_DOC_TYPE.values()
            for event_type, event_impact in event_impact_by_event_type.items()
            if event_impact == EventImpact.APPROUVE
        ]
        prescription_event_types = [
            event_type
            for event_impact_by_event_type in EVENT_IMPACT_BY_DOC_TYPE.values()
            for event_type, event_impact in event_impact_by_event_type.items()
            if event_impact == EventImpact.EN_COURS
        ]

        dernier_event_impactant_whens = [
            models.When(
                doc_type=doc_type,
                then=models.Subquery(
                    events.filter(
                        procedure=models.OuterRef("pk"),
                        type__in=event_impact_by_event_type.keys(),
                    ).values("type")[:1]
                ),
            )
            for (
                doc_type,
                event_impact_by_event_type,
            ) in EVENT_IMPACT_BY_DOC_TYPE.items()
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
            date_prescription=Coalesce(
                models.Subquery(
                    events.filter(
                        procedure=models.OuterRef("pk"),
                        type__in=prescription_event_types,
                    ).values("date_evenement_string")[:1]
                ),
                models.Value("0000-00-00"),
            ),
            dernier_event_impactant=models.Case(*dernier_event_impactant_whens),
        )

    def with_dates_notables(self, *, avant: date | None = None) -> Self:
        events = Event.objects.filter(is_valid=True)
        if avant:
            events = events.filter(date_evenement_string__lt=str(avant))

        queryset = self
        for date_notable, category_notable in {
            "date_publication_perimetre": EventNotable.PUBLICATION_PERIMETRE,
            "date_arret_projet": EventNotable.ARRET_DE_PROJET,
            "date_fin_echeance": EventNotable.FIN_ECHEANCE,
        }.items():
            event_types = [
                event_type
                for event_notable_by_event_type in EVENT_NOTABLE_BY_DOC_TYPE.values()
                for event_type, event_notable in event_notable_by_event_type.items()
                if event_notable == category_notable
            ]
            queryset = queryset.annotate(
                **{
                    date_notable: models.Subquery(
                        events.filter(
                            procedure=models.OuterRef("pk"), type__in=event_types
                        ).values("date_evenement_string")[:1]
                    )
                }
            )
        return queryset

    def with_is_intercommunal(self) -> Self:
        # On utilise une Subquery plutôt qu'une expression directe pour permettre
        # à Django d'ignorer la Subquery quand il fait des count(*) dans l'admin,
        # ce qui rend l'admin plus rapide.
        return self.annotate(
            is_intercommunal=models.Subquery(
                CommuneProcedure.objects.filter(procedure=models.OuterRef("pk"))
                .values("procedure")
                .annotate(is_intercommunal=GreaterThan(models.Count("*"), 1))
                .values("is_intercommunal")
            )
        )


class ProcedureManager(models.Manager):
    def get_queryset(self) -> ProcedureQuerySet:
        return (
            super()
            .get_queryset()
            .with_events()
            .with_is_intercommunal()
            .select_related("collectivite_porteuse")
        )


class Procedure(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    doc_type = models.CharField(choices=TypeDocument, blank=True, null=True)  # noqa: DJ001
    # Programme Local de l'Habitat
    vaut_PLH = models.BooleanField(db_column="is_pluih", blank=True, null=True)  # noqa: N815
    # Plan De Mobilité (anciennement Plan de Déplacements Urbains)
    vaut_PDM = models.BooleanField(db_column="is_pdu", blank=True, null=True)  # noqa: N815

    from_sudocuh = models.IntegerField(unique=True, blank=True, null=True)

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
    collectivite_porteuse = models.ForeignKey(
        "Collectivite",
        models.DO_NOTHING,
        db_constraint=False,
        null=True,
        to_field="code_insee_unique",
    )
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

    def __str__(self) -> str:
        return (
            self.name
            or f"🤖 {self.type} {self.numero or ''} {self.type_document} {self.collectivite_porteuse}"
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
            for event_impact_by_event_type in EVENT_IMPACT_BY_DOC_TYPE.values()
            for event_type, event_impact in event_impact_by_event_type.items()
        }
        return impact_by_event_type[self.dernier_event_impactant]

    @property
    def is_schema(self) -> bool:
        return self.doc_type in (TypeDocument.SCOT, TypeDocument.SD)

    @property
    def type_document(self) -> TypeDocument:
        if self.doc_type in (TypeDocument.PLU, *PLU_LIKE):
            if not self.is_intercommunal:
                return TypeDocument.PLU
            if (
                self.vaut_PLH and self.vaut_PDM
            ) or self.doc_type == TypeDocument.PLUIHM:
                return TypeDocument.PLUIHM
            if self.vaut_PLH or self.doc_type == TypeDocument.PLUIH:
                return TypeDocument.PLUIH
            if self.vaut_PDM or self.doc_type == TypeDocument.PLUIM:
                return TypeDocument.PLUIM
            return TypeDocument.PLUI

        return self.doc_type

    @cached_property
    def is_interdepartemental(self) -> bool:
        return len({commune.departement for commune in self.communes}) > 1


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

        return EVENT_IMPACT_BY_DOC_TYPE[self.procedure.doc_type].get(self.type)


class Region(models.Model):
    code_insee = models.CharField(unique=True)
    nom = models.CharField()

    def __str__(self) -> str:
        return self.nom


class Departement(models.Model):
    code_insee = models.CharField(unique=True)
    nom = models.CharField()
    region = models.ForeignKey(Region, models.DO_NOTHING, related_name="departements")

    def __str__(self) -> str:
        return f"{self.code_insee} - {self.nom}"


class CollectiviteQuerySet(models.QuerySet):
    def portant_scot(self, avant: date | None = None) -> Self:
        return (
            self.distinct()
            .filter(
                procedure__doc_type=TypeDocument.SCOT,
                procedure__parente=None,
                procedure__archived=False,
            )
            .select_related("departement__region")
            .prefetch_related(
                models.Prefetch(
                    "procedure_set",
                    Procedure.objects.with_events(avant=avant)
                    .with_dates_notables(avant=avant)
                    .filter(
                        doc_type="SCOT",
                        parente=None,
                        archived=False,
                    )
                    .annotate(
                        is_intercommunal=models.Value("1")  # Désactive la jointure
                    ),
                    to_attr="scots",
                ),
                models.Prefetch(
                    "scots__perimetre",
                    Commune.objects.with_scots().select_related("departement__region"),
                    to_attr="communes",
                ),
            )
        )


class Collectivite(models.Model):
    id = models.CharField(primary_key=True)  # Au format code_type
    code_insee_unique = models.CharField(  # noqa: DJ001
        unique=True,
        null=True,
        db_comment="Peut-être vide pour une COMD ayant le même code que sa commune parente",
    )
    type = models.CharField(choices=TypeCollectivite.choices)
    nom = models.CharField()
    competence_plan = models.BooleanField(db_default=False)
    competence_schema = models.BooleanField(db_default=False)
    adhesions = models.ManyToManyField(
        "self", related_name="collectivites_adherentes", symmetrical=False
    )
    departement = models.ForeignKey(
        Departement, models.DO_NOTHING, related_name="collectivites"
    )

    objects = CollectiviteQuerySet.as_manager()

    def __str__(self) -> str:
        return self.nom

    @property
    def code_insee(self) -> str:
        return self.id.split("_")[0]

    @cached_property
    def _scots_opposables(self) -> list[Procedure]:
        return [
            scot
            for scot in self.scots
            if scot.statut == EventImpact.APPROUVE
            and any(commune.is_opposable(scot) for commune in scot.communes)
        ]

    @cached_property
    def _scot_en_cours(self) -> Procedure | None:
        en_cours = [
            procedure
            for procedure in self.scots
            if procedure.statut == EventImpact.EN_COURS or not procedure.statut
        ]

        if not en_cours:
            return None

        if len(en_cours) > 1:
            logging.error(
                "Plusieurs SCoT en cours pour la collectivité %s", self.code_insee
            )
        return en_cours[0]

    @cached_property
    def scots_pour_csv(self) -> list[tuple[Procedure | None, Procedure | None]]:
        """Retourne des tuples de la forme (scot opposable, scot en cours)."""
        if not self._scots_opposables and self._scot_en_cours:
            return [(None, self._scot_en_cours)]

        return [
            (scot_opposable, self._scot_en_cours)
            for scot_opposable in self._scots_opposables
        ]


class CommuneQuerySet(models.QuerySet):
    def with_procedures_principales(self, avant: date | None = None) -> Self:
        return self.prefetch_related(
            models.Prefetch(
                "procedures",
                Procedure.objects.with_events(avant=avant)
                .filter(parente=None, archived=False)
                .order_by("-date_approbation"),
                to_attr="procedures_principales",
            )
        )

    def with_scots(self, avant: date | None = None) -> Self:
        return self.prefetch_related(
            models.Prefetch(
                "procedures",
                Procedure.objects.with_events(avant=avant)
                .annotate(
                    is_intercommunal=models.Value("1")  # Désactive la jointure
                )
                .filter(doc_type="SCOT", parente=None, archived=False)
                .order_by("-date_approbation"),
                to_attr="procedures_principales",
            )
        )


class Commune(Collectivite):
    intercommunalite = models.ForeignKey(
        Collectivite, models.DO_NOTHING, null=True, related_name="communes"
    )
    nouvelle = models.ForeignKey(
        "self", models.DO_NOTHING, null=True, related_name="deleguee"
    )
    procedures = models.ManyToManyField(
        Procedure, through="CommuneProcedure", related_name="perimetre"
    )

    objects = CommuneQuerySet.as_manager()

    def get_absolute_url(self) -> str:
        return reverse(
            "collectivite-detail",
            kwargs={
                "collectivite_code": self.code_insee,
                "collectivite_type": self.type,
            },
        )

    @cached_property
    def procedures_principales_approuvees(self) -> list[Procedure]:
        return [
            procedure
            for procedure in self.procedures_principales
            if procedure.type != "Abrogation"
            and procedure.statut == EventImpact.APPROUVE
        ]

    @cached_property
    def plan_opposable(self) -> Procedure | None:
        return next(
            (
                procedure
                for procedure in self.procedures_principales_approuvees
                if not procedure.is_schema
            ),
            None,
        )

    @cached_property
    def schema_opposable(self) -> Procedure | None:
        return next(
            (
                procedure
                for procedure in self.procedures_principales_approuvees
                if procedure.is_schema
            ),
            None,
        )

    def is_opposable(self, procedure: Procedure) -> bool:
        return procedure in (self.plan_opposable, self.schema_opposable)


class CommuneProcedure(models.Model):  # noqa: DJ008
    commune = models.ForeignKey(Commune, models.DO_NOTHING, db_constraint=False)
    procedure = models.ForeignKey(Procedure, models.DO_NOTHING)

    class Meta:
        managed = settings.UNDER_TEST
        db_table = "procedures_perimetres"
