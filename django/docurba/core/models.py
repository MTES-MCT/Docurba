import logging
from datetime import date
from enum import IntEnum, StrEnum, auto
from functools import cached_property
from operator import attrgetter
from typing import Self

from django.contrib.postgres.fields import ArrayField
from django.contrib.postgres.functions import RandomUUID, TransactionNow
from django.core.exceptions import PermissionDenied, ValidationError
from django.core.validators import MinValueValidator
from django.db import connection, models
from django.db.models import Value
from django.db.models.aggregates import StringAgg
from django.db.models.constraints import UniqueConstraint
from django.db.models.functions import Now
from django.urls import reverse
from django.utils import timezone

from docurba.core.enums import CommuneType, EventScope, TypeCollectivite, VisibilityType
from docurba.core.utils import OversizedIndex
from docurba.users.models import Profile

logger = logging.getLogger(__name__)


# NOTE(cms): These TextChoices should be moved to enums.py


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

    PLUIS = "PLUiS"
    PLUISH = "PLUiSH"
    PLUISHM = "PLUiSHM"
    PLUISM = "PLUiSM"


PLU_LIKE = (
    TypeDocument.PLUI,
    TypeDocument.PLUIH,
    TypeDocument.PLUIHM,
    TypeDocument.PLUIM,
    TypeDocument.PLUIS,
    TypeDocument.PLUISH,
    TypeDocument.PLUISHM,
    TypeDocument.PLUISM,
)


class CodeCompetencePerimetre(IntEnum):
    COMPETENCE_COMMUNE = 1
    COMPETENCE_EPCI_PERIMETRE_EPCI = 2
    COMPETENCE_EPCI_PERIMETRE_INFERIEUR_EPCI = 3
    COMPETENCE_EPCI_PROCEDURE_COMMUNALE = 4
    PAS_DE_PLAN = 9


TYPE_DOCUMENT_TO_CODE = {
    TypeDocument.CC: 1,
    TypeDocument.POS: 2,
    TypeDocument.PLU: 3,
    TypeDocument.PLUI: 3,
    TypeDocument.PLUIH: 3,
    TypeDocument.PLUIM: 3,
    TypeDocument.PLUIHM: 3,
    TypeDocument.PLUIS: 3,
    TypeDocument.PLUISH: 3,
    TypeDocument.PLUISHM: 3,
    TypeDocument.PLUISM: 3,
}

CODE_ETAT_SIMPLIFIE_TO_LIBELLE = {
    "99": "RNU",
    "91": "CC en élaboration",
    "92": "POS en élaboration",
    "93": "PLU en élaboration",
    "19": "CC approuvée",
    "11": "CC en révision",
    "13": "CC approuvée - PLU en élaboration",
    "29": "POS approuvé",
    "21": "POS approuvé - CC en élaboration",
    "22": "POS en révision ",
    "23": "POS approuvé - PLU en révision",
    "39": "PLU approuvé",
    "31": "PLU approuvé - CC en élaboration",
    "33": "PLU en révision",
}

CODE_ETAT_COMPLET_TO_LIBELLE = {
    "1111": "CC approuvée - révision CC - Compétence commune",
    "1131": "CC approuvée - élaboration PLU - Compétence commune",
    "1199": "CC approuvée - aucune procédure en cours - Compétence commune",
    "1332": "CC-I sect approuvée - élaboration PLU-I",
    "1399": "CC-I sect approuvée - aucune procédure en cours",
    "1414": "CC approuvée - révision CC - Compétence EPCI",
    "1432": "CC approuvée - élaboration PLU-I",
    "1433": "CC approuvée - élaboration PLU-I sectoriel",
    "1434": "CC approuvée - élaboration PLU - Compétence EPCI",
    "1499": "CC approuvée - aucune procédure en cours - Compétence EPCI",
    "2131": "POS approuvé - révision de PLU - Compétence commune",
    "2199": "POS approuvé - aucune procédure en cours - Compétence commune",
    "2432": "POS approuvé - révision de PLU-I",
    "2499": "POS approuvé - aucune procédure en cours - Compétence EPCI",
    "3111": "PLU approuvé - élaboration CC - Compétence commune",
    "3131": "PLU approuvé - révision de PLU - Compétence commune",
    "3199": "PLU approuvé - aucune procédure en cours - Compétence commune",
    "3232": "PLU-I approuvé - révision de PLU-I",
    "3299": "PLU-I approuvé - aucune procédure en cours",
    "3332": "PLU-I sect approuvé - révision de PLU-I",
    "3333": "PLU-I sect approuvé - révision de PLU-I sectoriel",
    "3399": "PLU-I sect approuvé - aucune procédure en cours",
    "3432": "PLU approuvé - révision de PLU-I",
    "3433": "PLU approuvé - révision de PLU-I sectoriel",
    "3434": "PLU approuvé - révision de PLU - Compétence EPCI",
    "3499": "PLU approuvé - aucune procédure en cours - Compétence EPCI",
    "9911": "RNU - élaboration CC - Compétence commune",
    "9914": "RNU - élaboration CC - Compétence EPCI",
    "9931": "RNU - élaboration PLU - Compétence commune",
    "9932": "RNU - élaboration PLU-I",
    "9933": "RNU - élaboration PLU-I sectoriel",
    "9934": "RNU - élaboration PLU - Compétence EPCI",
    "9999": "RNU - aucune procédure en cours",
}


class EventCategory(StrEnum):
    # procedure.status (nuxt side) and column "impact" on the Google Sheet commented out.
    PRESCRIPTION = auto()  # "en cours"
    APPROUVE = auto()  # "opposable"
    ABANDON = auto()  # "abandonné"
    ANNULE = auto()  # "annulé"
    CADUC = auto()  # "caduc"
    ARRET_DE_PROJET = auto()
    PORTER_A_CONNAISSANCE = auto()
    PORTER_A_CONNAISSANCE_COMPLEMENTAIRE = auto()
    PUBLICATION_PERIMETRE = auto()
    CARACTERE_EXECUTOIRE = auto()
    FIN_ECHEANCE = auto()


EVENT_CATEGORY_PRIORISES = (
    EventCategory.ABANDON,
    EventCategory.APPROUVE,
    EventCategory.PRESCRIPTION,
    EventCategory.PUBLICATION_PERIMETRE,
    EventCategory.ANNULE,
    EventCategory.CADUC,
)


# https://docs.google.com/spreadsheets/d/1NEcWazdx7LvpnydcyP4pBdFWl9fI_Iu9zy9AQcDtll0/edit?gid=637043323#gid=637043323
EVENT_CATEGORY_BY_DOC_TYPE = {
    TypeDocument.CC: {
        "Prescription": EventCategory.PRESCRIPTION,
        "Délibération de prescription du conseil municipal": EventCategory.PRESCRIPTION,
        "Approbation du préfet": EventCategory.APPROUVE,
        "Retrait de l'annulation totale": EventCategory.APPROUVE,
        "Arrêté de mise à jour": EventCategory.APPROUVE,
        "Abandon": EventCategory.ABANDON,
        "Retrait de la délibération de prescription": EventCategory.ABANDON,
        "Annulation TA totale": EventCategory.ANNULE,
        "Annulation TA": EventCategory.ANNULE,  # not found in Nuxt's JSON. Probably Sudocuh's name.
        "Abrogation effective": EventCategory.ANNULE,  # should be "abrogé"
        "Arrêt de projet": EventCategory.ARRET_DE_PROJET,
        "Porter à connaissance": EventCategory.PORTER_A_CONNAISSANCE,  # not found in Nuxt's JSON. Probably Sudocuh's name.
        "Porter à connaissance complémentaire": EventCategory.PORTER_A_CONNAISSANCE_COMPLEMENTAIRE,  # not found in Nuxt's JSON. Probably Sudocuh's name.
        "Transmission du porter-à-connaissance": EventCategory.PORTER_A_CONNAISSANCE,
        "Transmission du porter à connaissance complémentaire": EventCategory.PORTER_A_CONNAISSANCE_COMPLEMENTAIRE,
        "Publication de périmètre": EventCategory.PUBLICATION_PERIMETRE,  # not found in Nuxt's JSON. Probably Sudocuh's name.
        "Publication périmètre": EventCategory.PUBLICATION_PERIMETRE,  # not found in Nuxt's JSON. Probably Sudocuh's name.
        "Caractère exécutoire": EventCategory.CARACTERE_EXECUTOIRE,
        "Fin d'échéance": EventCategory.FIN_ECHEANCE,  # Deleted 11/28/25
    },
    TypeDocument.SCOT: {
        "Prescription": EventCategory.PRESCRIPTION,  # not found in Nuxt's JSON. Probably Sudocuh's name.
        "Délibération de l'Etablissement Public": EventCategory.PRESCRIPTION,
        "Délibération de l'établissement public qui prescrit": EventCategory.PRESCRIPTION,
        "Retrait de la délibération d'approbation": EventCategory.PRESCRIPTION,
        "Délibération d'approbation": EventCategory.APPROUVE,
        "Retrait de l'annulation totale": EventCategory.APPROUVE,
        "Abandon": EventCategory.ABANDON,
        "Retrait de la délibération de prescription": EventCategory.ABANDON,
        "Annulation TA totale": EventCategory.ANNULE,
        "Annulation TA": EventCategory.ANNULE,  # not found in Nuxt's JSON. Probably Sudocuh's name.
        "Caducité": EventCategory.CADUC,  # Deleted 05/26/26
        "Arrêt de projet": EventCategory.ARRET_DE_PROJET,
        "Porter à connaissance": EventCategory.PORTER_A_CONNAISSANCE,  # not found in Nuxt's JSON. Probably Sudocuh's name.
        "Porter à connaissance complémentaire": EventCategory.PORTER_A_CONNAISSANCE_COMPLEMENTAIRE,  # not found in Nuxt's JSON. Probably Sudocuh's name.
        "Transmission du porter-à-connaissance": EventCategory.PORTER_A_CONNAISSANCE,
        "Transmission du porter à connaissance complémentaire": EventCategory.PORTER_A_CONNAISSANCE_COMPLEMENTAIRE,
        "Publication de périmètre": EventCategory.PUBLICATION_PERIMETRE,  # not found in Nuxt's JSON. Probably Sudocuh's name.
        "Publication périmètre": EventCategory.PUBLICATION_PERIMETRE,  # not found in Nuxt's JSON. Probably Sudocuh's name.
        "Publication du périmètre par le préfet": EventCategory.PUBLICATION_PERIMETRE,
        "Caractère exécutoire": EventCategory.CARACTERE_EXECUTOIRE,
        "Fin d'échéance": EventCategory.FIN_ECHEANCE,  # Deleted 11/28/25
    },
    TypeDocument.SD: {
        "Prescription": EventCategory.PRESCRIPTION,
        "Délibération de l'établissement public qui prescrit": EventCategory.PRESCRIPTION,
        "Délibération d'approbation": EventCategory.APPROUVE,
        "Abandon": EventCategory.ABANDON,
        "Annulation TA totale": EventCategory.ANNULE,
        "Annulation TA": EventCategory.ANNULE,  # not found in Nuxt's JSON. Probably Sudocuh's name.
        "Caducité": EventCategory.CADUC,  # Deleted 05/26/26
    },
    TypeDocument.PLU: {
        "Prescription": EventCategory.PRESCRIPTION,
        "Délibération de prescription du conseil municipal ou communautaire": EventCategory.PRESCRIPTION,
        "Retrait de l'annulation totale": EventCategory.APPROUVE,
        "Délibération d'approbation du municipal ou communautaire": EventCategory.APPROUVE,  # not found in Nuxt's JSON. Probably Sudocuh's name.
        "Délibération d'approbation du conseil municipal ou communautaire": EventCategory.APPROUVE,
        "Délibération d'approbation": EventCategory.APPROUVE,
        "Abandon": EventCategory.ABANDON,
        "Retrait de la délibération de prescription": EventCategory.ABANDON,
        "Annulation TA totale": EventCategory.ANNULE,
        "Annulation TA": EventCategory.ANNULE,  # not found in Nuxt's JSON. Probably Sudocuh's name.
        "Abrogation": EventCategory.ANNULE,
        "Arrêté d'abrogation": EventCategory.ANNULE,
        "Caducité": EventCategory.CADUC,  # Deleted 05/26/26
        "Arrêt de projet": EventCategory.ARRET_DE_PROJET,
        "Porter à connaissance": EventCategory.PORTER_A_CONNAISSANCE,  # not found in Nuxt's JSON. Probably Sudocuh's name.
        "Porter à connaissance complémentaire": EventCategory.PORTER_A_CONNAISSANCE_COMPLEMENTAIRE,  # not found in Nuxt's JSON. Probably Sudocuh's name.
        "Transmission du porter-à-connaissance": EventCategory.PORTER_A_CONNAISSANCE,
        "Transmission du porter à connaissance complémentaire": EventCategory.PORTER_A_CONNAISSANCE_COMPLEMENTAIRE,
        "Publication de périmètre": EventCategory.PUBLICATION_PERIMETRE,  # not found in Nuxt's JSON. Probably Sudocuh's name.
        "Publication périmètre": EventCategory.PUBLICATION_PERIMETRE,  # not found in Nuxt's JSON. Probably Sudocuh's name.
        "Caractère exécutoire": EventCategory.CARACTERE_EXECUTOIRE,
        "Fin d'échéance": EventCategory.FIN_ECHEANCE,  # Deleted 11/28/25
    },
    TypeDocument.POS: {
        "Prescription": EventCategory.PRESCRIPTION,
        "Délibération de prescription du conseil municipal ou communautaire": EventCategory.PRESCRIPTION,
        "Délibération d'approbation du municipal ou communautaire": EventCategory.APPROUVE,  # not found
        "Délibération d'approbation du conseil municipal ou communautaire": EventCategory.APPROUVE,
        "Délibération d'approbation": EventCategory.APPROUVE,
        "Abandon": EventCategory.ABANDON,
        "Annulation TA": EventCategory.ANNULE,  # not found
        "Annulation TA totale": EventCategory.ANNULE,
        "Caducité": EventCategory.CADUC,  # Deleted 05/26/26
        "Arrêt de projet": EventCategory.ARRET_DE_PROJET,
        "Porter à connaissance": EventCategory.PORTER_A_CONNAISSANCE,  # not found
        "Transmission du porter-à-connaissance": EventCategory.PORTER_A_CONNAISSANCE,
        "Porter à connaissance complémentaire": EventCategory.PORTER_A_CONNAISSANCE_COMPLEMENTAIRE,  # not found
        "Publication de périmètre": EventCategory.PUBLICATION_PERIMETRE,  # not fund
        "Publication périmètre": EventCategory.PUBLICATION_PERIMETRE,  # not found
        "Caractère exécutoire": EventCategory.CARACTERE_EXECUTOIRE,
        "Fin d'échéance": EventCategory.FIN_ECHEANCE,  # Deleted 11/28/25
    },
}
EVENT_CATEGORY_BY_DOC_TYPE |= dict.fromkeys(
    PLU_LIKE, EVENT_CATEGORY_BY_DOC_TYPE[TypeDocument.PLU]
)

# Reverse of EVENT_CATEGORY_BY_DOC_TYPE keeping the same first-level keys.
EVENT_TYPE_BY_EVENT_CATEGORY = {}
for doc_type, types in EVENT_CATEGORY_BY_DOC_TYPE.items():
    for name, category in types.items():
        EVENT_TYPE_BY_EVENT_CATEGORY.setdefault(doc_type, {}).setdefault(
            category, []
        ).append(name)


class ProcedureStatusChoices(models.TextChoices):
    ANNULE = "annule", "Annulé"
    EN_COURS = "en cours", "En cours"
    CADUC = "caduc", "Caduc"
    ABANDON = "abandon", "Abandon"
    OPPOSABLE = "opposable", "Opposable"


class ProcedureQuerySet(models.QuerySet):
    def with_events(self, *, avant: date | None = None) -> Self:
        events = Event.objects.exclude(date_evenement=None).only(
            "type",
            "date_evenement",
            "is_valid",
            "procedure_id",
        )
        return self.annotate(
            date_pivot=models.Value(
                avant or timezone.now().date(), output_field=models.DateField()
            )
        ).prefetch_related(
            models.Prefetch("event_set", events, to_attr="events_prefetched")
        )

    def with_communes_counts(self) -> Self:
        # On utilise une Subquery plutôt qu'une expression directe pour permettre
        # à Django d'ignorer la Subquery quand il fait des count(*) dans l'admin,
        # ce qui rend l'admin plus rapide.
        return self.annotate(
            # 254003304 est un bon EPCI pour tester DISTINCT : 1279 communes en 2024
            communes_adherentes__count=models.functions.Coalesce(
                models.Subquery(
                    MaterializedViewFlatMembership.objects.filter(
                        group=models.OuterRef("collectivite_porteuse__id"),
                        member_type=TypeCollectivite.COM,
                    )
                    .values("group")
                    .annotate(
                        communes_adherentes__count=models.Count("member"),
                    )
                    .values("communes_adherentes__count")
                ),
                0,
            ),
        )

    def with_perimetre_counts(self) -> Self:
        return self.annotate(
            perimetre__count=models.functions.Coalesce(
                models.Subquery(
                    CommuneProcedure.objects.filter(
                        procedure=models.OuterRef("pk"), commune__nouvelle=None
                    )
                    .values("procedure")
                    .annotate(perimetre__count=models.Count("*"))
                    .values("perimetre__count")
                ),
                0,
            ),
        )

    def with_concatenated_topics_as_string(self) -> Self:
        return self.annotate(
            concatenated_topics_as_string=StringAgg(
                "topics__display_name",
                delimiter=Value(","),
                order_by="topics__display_name",
            ),
        )


class ProcedureManager(models.Manager):
    def get_queryset(self) -> ProcedureQuerySet:
        return (
            super()
            .get_queryset()
            .with_perimetre_counts()
            .with_communes_counts()
            .select_related("collectivite_porteuse__departement__region")
        )


class FastLoadingProcedureManager(ProcedureManager):
    def get_queryset(self) -> Self:
        # There is no mention of these fields on Nuxt side.
        to_be_removed_fields = [
            "test",
            "testing",
            "doc_type_code",
            "is_sudocuh_scot",
            "previous_opposable_procedures_ids",
            "type_code",
            "initial_perimetre",
        ]
        # Text or JSON fields.
        heavy_fields = [
            "current_perimetre",
            "comment_dgd",
            "volet_qualitatif",
        ]
        return super().get_queryset().defer(*to_be_removed_fields, *heavy_fields)


class Procedure(models.Model):
    id = models.UUIDField(primary_key=True, db_default=RandomUUID())
    test = models.BooleanField(db_default=False)
    testing = models.BooleanField(blank=True, null=True)
    doc_type = models.CharField(choices=TypeDocument, blank=True, null=True)  # noqa: DJ001 # TextField in DB.
    doc_type_code = models.TextField(blank=True, null=True)  # noqa: DJ001
    type_code = models.TextField(blank=True, null=True)  # noqa: DJ001
    vaut_SCoT = models.BooleanField(db_column="is_scot", blank=True, null=True)  # noqa: N815
    # Programme Local de l'Habitat
    vaut_PLH = models.BooleanField(db_column="is_pluih", blank=True, null=True)  # noqa: N815
    # Plan De Mobilité (anciennement Plan de Déplacements Urbains)
    vaut_PDM = models.BooleanField(db_column="is_pdu", blank=True, null=True)  # noqa: N815
    obligation_PDU = models.BooleanField(  # noqa: N815
        db_column="mandatory_pdu", blank=True, null=True
    )
    maitrise_d_oeuvre = models.JSONField(db_column="moe", null=True)

    from_sudocuh = models.IntegerField(unique=True, blank=True, null=True)

    parente = models.ForeignKey(
        "self",
        models.CASCADE,
        db_column="secondary_procedure_of",
        related_name="secondaires",
        null=True,
    )
    name = models.TextField(blank=True, null=True)  # noqa: DJ001
    commentaire = models.TextField(blank=True, null=True)  # noqa: DJ001
    comment_from_sudocuh = models.TextField(blank=True)
    comment_dgd = models.TextField(blank=True, null=True)  # noqa: DJ001
    is_principale = models.BooleanField(blank=True, null=True)
    is_sectoriel = models.BooleanField(blank=True, null=True)
    is_sudocuh_scot = models.BooleanField(
        blank=True, null=True
    )  # No reference in Nuxt's side but column is filled with different values.
    sudocu_secondary_procedure_of = models.IntegerField(blank=True, null=True)
    shareable = models.BooleanField(db_default=False)
    type = models.CharField(blank=True, null=True)  # noqa: DJ001 # TextField in DB.
    numero = models.CharField(blank=True, null=True)  # noqa: DJ001 # TextField in DB.
    collectivite_porteuse = models.ForeignKey(
        "Collectivite",
        models.DO_NOTHING,
        db_constraint=False,
        null=True,
        to_field="code_insee_unique",
    )
    created_at = models.DateTimeField(db_default=TransactionNow(), null=True)
    last_updated_at = models.DateTimeField(db_default=TransactionNow(), null=True)
    # Procedure updated "in cascade" when the parent procedure is.
    # See create_table_procedures.sql.
    # Used in Nuxt's side to display a warning when the procedure is a duplicate.
    # Also used to filter archived procedures (as it's used in `archived`).
    # NOTE(cms): refactor this some day and add tests.
    doublon_cache_de = models.OneToOneField(
        "self", on_delete=models.RESTRICT, blank=True, null=True, unique=True
    )
    soft_delete = models.BooleanField(
        db_default=False, verbose_name="archivée (soft_delete)"
    )
    archived = models.GeneratedField(
        expression=models.Q(doublon_cache_de__isnull=False)
        | models.Q(soft_delete=True),
        output_field=models.BooleanField(),
        db_persist=True,
        verbose_name="archivée (archived)",
    )
    initial_perimetre = models.JSONField(null=True)
    current_perimetre = models.JSONField(null=True)
    volet_qualitatif = models.JSONField(blank=True, null=True)

    last_updated_by = models.ForeignKey("users.Profile", models.DO_NOTHING, null=True)
    started_before_huwart_law = models.BooleanField(
        db_default=False, verbose_name="lancée avant la loi Huwart"
    )
    owner = models.ForeignKey(
        "users.Profile",
        models.SET_NULL,
        null=True,
        verbose_name="propriétaire",
        related_name="procedures",
    )
    project = models.ForeignKey(
        "core.Project",
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        verbose_name="projet",
        related_name="procedures",
    )
    # This columns seems completely obsolete and will be deleted in a migration.
    # The related name is here to prevent a conflict with the `doublon_cache_de_id` column.
    previous_opposable_procedures_ids = models.ForeignKey(
        "self",
        blank=True,
        null=True,
        db_column="previous_opposable_procedures_ids",
        on_delete=models.SET_NULL,
        related_name="procedures_previous_opposable_procedures_ids_set",
    )  # Seems unused
    departements = ArrayField(
        verbose_name="Départements",
        # Charfield pour permettre aux départements ne contenant qu'un chiffre de commencer par un zéro.
        base_field=models.CharField(max_length=3, blank=True),
        blank=True,
        null=True,
    )

    # Denormalized information used only by Nuxt. See self.statut for the Django logic.
    status = models.CharField(choices=ProcedureStatusChoices, blank=True, null=True)  # noqa: DJ001 # TextField in DB.

    objects = FastLoadingProcedureManager.from_queryset(ProcedureQuerySet)()
    full_objects = ProcedureManager.from_queryset(ProcedureQuerySet)()

    class Meta:
        base_manager_name = "objects"
        db_table = "procedures"
        constraints = (
            UniqueConstraint(
                "id",
                condition=models.Q(parente=None, archived=False),
                name="procedures_pkey_secondary_null_not_archived",
            ),
        )
        indexes = (
            models.Index(
                "created_at",
                name="idx_procedures_created_at",
            ),
            models.Index(
                "doc_type",
                name="idx_procedures_doc_type",
            ),
            models.Index(
                fields=[
                    "id",
                    "is_principale",
                    "archived",
                ],
                name="idx_procedures_is_principale",
            ),
            OversizedIndex(
                fields=[
                    "is_principale",
                    "created_at",
                ],
                name="idx_procedures_is_principale_created_at",
            ),
            OversizedIndex(
                fields=[
                    "is_principale",
                    "doc_type",
                    "created_at",
                ],
                name="idx_procedures_is_principale_doc_type_created_at",
            ),
        )

    def __str__(self) -> str:
        return (
            self.name
            or f"🤖 {self.type} {self.numero or ''} {self.type_document} {self.collectivite_porteuse}"
        )

    def __lt__(self, other: Self) -> bool:
        if self.date_approbation and other.date_approbation:
            return self.date_approbation < other.date_approbation
        if self.date_prescription and other.date_prescription:
            return self.date_prescription < other.date_prescription
        return self.created_at < other.created_at

    def get_absolute_url(self) -> str:
        return f"/frise/{self.pk}"

    _events_processed = False

    def _process_events(self) -> None:
        if self._events_processed:
            return

        for event in reversed(self.events_prefetched):
            if event.category and (
                event.category == EventCategory.FIN_ECHEANCE
                or event.date_evenement <= self.date_pivot
            ):
                setattr(self, event.category, event)
        self._events_processed = True

    @cached_property
    def dernier_event_impactant(self) -> "Event | None":
        if self.parente_id:
            return None
        self._process_events()

        events_impactants_priorises = (
            event
            for event_category in EVENT_CATEGORY_PRIORISES
            if (event := getattr(self, event_category, None))
        )
        return max(
            events_impactants_priorises, key=attrgetter("date_evenement"), default=None
        )

    @property
    def statut(self) -> EventCategory | None:
        if self.type_document == TypeDocument.SD:
            return EventCategory.CADUC
        if not self.dernier_event_impactant:
            return None
        if self.date_fin_echeance and self.date_fin_echeance < self.date_pivot:
            return EventCategory.CADUC
        return self.dernier_event_impactant.category

    def _date(self, event_type: EventCategory) -> date | None:
        self._process_events()
        event = getattr(self, event_type, None)
        if not event:
            return None
        return event.date_evenement

    @property
    def date_approbation(self) -> date | None:
        return self._date(EventCategory.APPROUVE)

    @property
    def date_prescription(self) -> date | None:
        return self._date(EventCategory.PRESCRIPTION)

    @property
    def date_publication_perimetre(self) -> date | None:
        return self._date(EventCategory.PUBLICATION_PERIMETRE)

    @property
    def date_arret_projet(self) -> date | None:
        return self._date(EventCategory.ARRET_DE_PROJET)

    @property
    def date_fin_echeance(self) -> date | None:
        return self._date(EventCategory.FIN_ECHEANCE)

    @property
    def date_porter_a_connaissance(self) -> date | None:
        return self._date(EventCategory.PORTER_A_CONNAISSANCE)

    @property
    def date_porter_a_connaissance_complementaire(self) -> date | None:
        return self._date(EventCategory.PORTER_A_CONNAISSANCE_COMPLEMENTAIRE)

    @property
    def date_caractere_executoire(self) -> date | None:
        return self._date(EventCategory.CARACTERE_EXECUTOIRE)

    @property
    def is_schema(self) -> bool:
        return self.doc_type in (TypeDocument.SCOT, TypeDocument.SD)

    @property
    def vaut_PLH_consolide(self) -> bool:  # noqa: N802
        if not self.is_intercommunal:
            return False
        return self.vaut_PLH or self.doc_type in (
            TypeDocument.PLUIH,
            TypeDocument.PLUIHM,
        )

    @property
    def vaut_PDM_consolide(self) -> bool:  # noqa: N802
        if not self.is_intercommunal:
            return False
        return self.vaut_PDM or self.doc_type in (
            TypeDocument.PLUIM,
            TypeDocument.PLUIHM,
        )

    @property
    def type_document(self) -> TypeDocument:
        if self.doc_type in (TypeDocument.PLU, *PLU_LIKE):
            if not self.is_intercommunal:
                return TypeDocument.PLU
            if self.vaut_PLH_consolide and self.vaut_PDM_consolide:
                return (
                    TypeDocument.PLUISHM
                    if self.is_sectoriel_consolide
                    else TypeDocument.PLUIHM
                )
            if self.vaut_PLH_consolide:
                return (
                    TypeDocument.PLUISH
                    if self.is_sectoriel_consolide
                    else TypeDocument.PLUIH
                )
            if self.vaut_PDM_consolide:
                return (
                    TypeDocument.PLUISM
                    if self.is_sectoriel_consolide
                    else TypeDocument.PLUIM
                )
            return (
                TypeDocument.PLUIS if self.is_sectoriel_consolide else TypeDocument.PLUI
            )

        return self.doc_type

    @property
    def type_document_code(self) -> int:
        return TYPE_DOCUMENT_TO_CODE[self.type_document]

    def competence_intercommunalite_code(
        self, collectivite: "Collectivite"
    ) -> CodeCompetencePerimetre:
        if collectivite.is_commune:
            return CodeCompetencePerimetre.COMPETENCE_COMMUNE
        if not self.is_intercommunal:
            return CodeCompetencePerimetre.COMPETENCE_EPCI_PROCEDURE_COMMUNALE
        if self.is_sectoriel_consolide:
            return CodeCompetencePerimetre.COMPETENCE_EPCI_PERIMETRE_INFERIEUR_EPCI
        return CodeCompetencePerimetre.COMPETENCE_EPCI_PERIMETRE_EPCI

    @cached_property
    def is_interdepartemental(self) -> bool:
        return len({commune.departement for commune in self.communes}) > 1

    @property
    def delai_d_approbation(self) -> int | None:
        try:
            delai = self.date_approbation - self.date_prescription
        except TypeError:
            return None
        else:
            return delai.days

    @property
    def is_intercommunal(self) -> bool:
        # self.perimetre_count is set when calling Procedure.objects.with_perimetre_counts
        # which is always called on the manager (see ProcedureManager.get_queryset).
        # For the moment, it is mandatory to know if the procedure is_intercommunal.
        # The self.type_document, using self.is_intercommunal, is used to generate the self representation, thus on the Django admin.
        # For an unknown reason, the ProcedureManager is used on the "list" view but not on the "change" one.
        # This should be refactored some day as this hack is quite ugly.
        if not hasattr(self, "perimetre__count"):
            self.perimetre__count = self.perimetre.count()

        return self.perimetre__count > 1

    @property
    def is_sectoriel_consolide(self) -> bool:
        # self.perimetre_count is set when calling Procedure.objects.with_perimetre_counts
        # which is always called on the manager (see ProcedureManager.get_queryset).
        # For the moment, it is mandatory to know if the procedure is_sectoriel_consolide.
        # This should be refactored some day as this hack is quite ugly.
        if not hasattr(self, "perimetre__count"):
            self.perimetre__count = self.perimetre.count()

        # TODO Ajouter la vérif de la colonne is_sectoriel  # noqa: FIX002
        return self.communes_adherentes__count > self.perimetre__count

    @property
    def is_en_cours(self) -> bool:
        if self.type == "Abrogation" or self.type_document == TypeDocument.POS:
            return False

        return self.statut in (
            EventCategory.PRESCRIPTION,
            EventCategory.PUBLICATION_PERIMETRE,
        )


class ProcedureTopic(models.Model):
    procedure = models.ForeignKey(
        "core.Procedure", on_delete=models.CASCADE, related_name="topics_through"
    )
    topic = models.ForeignKey(
        "core.Topic", on_delete=models.RESTRICT, related_name="procedures_through"
    )
    comment = models.TextField(verbose_name="Commentaire", blank=True)
    created_at = models.DateTimeField("créé le", auto_now_add=True, db_default=Now())
    updated_at = models.DateTimeField("mis à jour le", auto_now=True, null=True)

    class Meta:
        ordering = ["topic"]  # noqa: RUF012
        verbose_name = "objet sélectionné"
        verbose_name_plural = "objets sélectionnés"
        unique_together = ("procedure", "topic")

    def __str__(self) -> str:
        return f"{self.pk}"


class Topic(models.Model):
    name = models.CharField(verbose_name="Nom système")
    display_name = models.CharField(verbose_name="Nom d'affichage")
    procedures = models.ManyToManyField(
        "core.Procedure",
        through="ProcedureTopic",
        related_name="topics",
        verbose_name="procédures",
    )
    ui_rank = models.SmallIntegerField(verbose_name="Position dans le menu déroulant")

    class Meta:
        verbose_name = "objet"
        ordering = [  # noqa: RUF012
            "ui_rank",
        ]

    def __str__(self) -> str:
        return self.name


class ProjectManager(models.Manager):
    pass


class FastLoadingProjectManager(ProjectManager):
    def get_queryset(self) -> Self:
        # There is no mention of these fields on Nuxt side.
        to_be_removed_fields = [
            "test",
            "is_sudocuh_scot",
            "initial_perimetre",
            "current_perimetre_new",
        ]
        # Text, Array or JSON fields.
        heavy_fields = [
            "epci",
            "current_perimetre",
            "doc_type_code",
            "pac",
            "towns",
        ]
        return super().get_queryset().defer(*to_be_removed_fields, *heavy_fields)


class Project(models.Model):
    id = models.UUIDField(primary_key=True, db_default=RandomUUID())
    created_at = models.DateTimeField(db_default=models.functions.Now())
    archived = models.BooleanField(db_default=False)
    name = models.CharField(blank=True, null=True)  # noqa: DJ001
    test = models.BooleanField(blank=True, null=True)

    collectivite = models.ForeignKey(
        "core.Collectivite",
        blank=True,
        null=True,
        on_delete=models.DO_NOTHING,
        related_name="projects",
        to_field="code_insee_unique",
    )
    collectivite_porteuse = models.ForeignKey(
        "core.Collectivite",
        blank=True,
        null=True,
        on_delete=models.DO_NOTHING,
        related_name="owned_projects",
        to_field="code_insee_unique",
    )
    epci = models.JSONField(blank=True, null=True)
    current_perimetre = ArrayField(
        base_field=models.JSONField(blank=True, null=True),
        blank=True,
        null=True,
    )
    initial_perimetre = ArrayField(
        base_field=models.JSONField(blank=True, null=True),
        blank=True,
        null=True,
    )
    current_perimetre_new = models.JSONField(blank=True, null=True)
    doc_type = models.CharField()
    doc_type_code = models.TextField(blank=True, null=True)  # noqa: DJ001

    from_sudocuh = models.IntegerField(unique=True, blank=True, null=True)
    from_sudocuh_procedure_id = models.IntegerField(unique=True, blank=True, null=True)
    sudocuh_procedure_id = models.IntegerField(blank=True, null=True)
    is_sudocuh_scot = models.BooleanField(
        blank=True, null=True
    )  # No reference in Nuxt's side but column is filled with different values.

    pac = models.JSONField(db_column="PAC", blank=True, null=True)
    trame = models.CharField(blank=True, null=True)  # noqa: DJ001

    region = models.CharField(blank=True, null=True)  # noqa: DJ001
    towns = models.JSONField(blank=True, null=True)

    owner = models.ForeignKey(
        "users.Profile", models.DO_NOTHING, db_column="owner", blank=True, null=True
    )

    objects = FastLoadingProjectManager()
    full_objects = ProjectManager()

    class Meta:
        verbose_name = "projet"
        db_table = "projects"
        base_manager_name = "objects"

    def __str__(self) -> str:
        return f"{self.pk} - {self.name}"


class EventTypeManager(models.Manager):
    pass


class ActiveEventTypeManager(EventTypeManager):
    def get_queryset(self) -> Self:
        return super().get_queryset().filter(is_active=True)


class EventType(models.Model):
    class DocumentType(models.TextChoices):
        PLU = TypeDocument.PLU
        CC = TypeDocument.CC
        SCOT = TypeDocument.SCOT

    id = models.UUIDField(primary_key=True, db_default=RandomUUID(), editable=False)
    document_type = models.CharField(
        verbose_name="type de document", choices=DocumentType
    )
    name = models.CharField(verbose_name="nom")
    order = models.PositiveIntegerField(
        verbose_name="ordre",
        validators=[MinValueValidator(1)],
        blank=True,
    )
    is_active = models.BooleanField(verbose_name="actif", default=True, db_default=True)
    is_structuring = models.BooleanField(
        verbose_name="structurant", default=False, db_default=False
    )
    scope_list = ArrayField(
        verbose_name="liste des scopes",
        base_field=models.CharField(choices=EventScope),
        blank=True,
        default=list,
        db_default="{}",
    )
    scope_sugg = ArrayField(
        verbose_name="Scopes suggérés",
        base_field=models.CharField(choices=EventScope),
        blank=True,
        default=list,
        db_default="{}",
    )
    impact = models.CharField(
        blank=True, default="", db_default="", choices=ProcedureStatusChoices
    )
    sudocuh_name = models.CharField(
        verbose_name="nom sudocuh", blank=True, default="", db_default=""
    )
    sudocuh_code = models.CharField(
        verbose_name="code sudocuh", blank=True, default="", db_default=""
    )
    created_at = models.DateTimeField(
        verbose_name="créé le", auto_now_add=True, db_default=Now()
    )
    updated_at = models.DateTimeField(
        verbose_name="mis à jour le", auto_now=True, null=True
    )

    objects = ActiveEventTypeManager()
    all_objects = EventTypeManager()

    class Meta:
        verbose_name = "type d'évènement"
        verbose_name_plural = "types d'évènement"
        unique_together = ("document_type", "name")
        ordering = ("order",)

    def __str__(self) -> str:
        return f"{self.document_type} - {self.name}"

    def save(self, *args, **kwargs) -> None:  # noqa: ANN002, ANN003
        if self.order is None:
            self.order = EventType.get_next_order(self.document_type)
        super().save(*args, **kwargs)

    @classmethod
    def get_next_order(cls, document_type: DocumentType) -> int:
        result = cls.objects.filter(document_type=document_type).aggregate(
            next_order=models.Max("order", default=0) + 1,
        )
        return result["next_order"]


class EventQuerySet(models.QuerySet):
    def without_archived(self) -> Self:
        return self.filter(archived_at__isnull=True)

    def defer_heavy_fields(self) -> Self:
        to_be_removed_fields = [
            "is_sudocuh_scot",
            "test",
            "code",
            "from_sudocuh_procedure_id",
        ]
        # Text, Array or JSON fields.
        heavy_fields = [
            "description",
            "attachements",
            "actors",
        ]
        return self.defer(*to_be_removed_fields, *heavy_fields)


class EventManager(models.Manager):
    pass


class FastLoadingEventManager(EventManager):
    def get_queryset(self) -> Self:

        return super().get_queryset().without_archived().defer_heavy_fields()


class Event(models.Model):
    id = models.UUIDField(primary_key=True, db_default=RandomUUID(), editable=False)
    procedure = models.ForeignKey(
        "core.Procedure", models.DO_NOTHING, null=True, verbose_name="procédure"
    )
    event_type = models.ForeignKey(
        "core.EventType", models.DO_NOTHING, null=True, verbose_name="type"
    )
    type = models.TextField(blank=True, null=True)  # noqa: DJ001
    date_evenement = models.DateField(
        db_column="date_iso", blank=True, null=True, verbose_name="date"
    )
    is_valid = models.BooleanField(db_default=True, verbose_name="est valide")
    visibility = models.TextField(  # noqa: DJ001
        blank=True,
        null=True,
        db_default="public",
        choices=VisibilityType,
        verbose_name="visibilité",
    )
    description = models.TextField(blank=True, null=True)  # noqa: DJ001

    created_at = models.DateTimeField(
        blank=True, null=True, db_default=TransactionNow(), verbose_name="créé le"
    )
    updated_at = models.DateTimeField(
        blank=True, null=True, db_default=TransactionNow(), verbose_name="modifié le"
    )
    attachements = models.JSONField(
        blank=True, null=True, verbose_name="pièces-jointes"
    )
    from_sudocuh = models.IntegerField(
        unique=True, blank=True, null=True, verbose_name="from_sudocuh"
    )
    profile = models.ForeignKey(
        "users.Profile", models.DO_NOTHING, blank=True, null=True, verbose_name="profil"
    )
    project = models.ForeignKey(
        "core.Project", blank=True, null=True, on_delete=models.SET_NULL
    )
    actors = models.JSONField(blank=True, null=True, verbose_name="acteurs")
    is_sudocuh_scot = models.BooleanField(
        blank=True, null=True, verbose_name="is_sudocuh_scot"
    )
    test = models.BooleanField(blank=True, null=True)
    code = models.TextField(blank=True, null=True)  # noqa: DJ001
    from_sudocuh_procedure_id = models.IntegerField(
        blank=True, null=True, verbose_name="from_sudocuh_procedure_id"
    )

    # archived_at is the source of truth to know if an event is archived
    archived_at = models.DateTimeField(blank=True, null=True, verbose_name="archivé le")
    archived_by = models.ForeignKey(
        "users.Profile",
        models.DO_NOTHING,
        blank=True,
        null=True,
        related_name="+",
        verbose_name="archivé par",
    )

    objects = FastLoadingEventManager.from_queryset(EventQuerySet)()
    full_objects = EventManager.from_queryset(EventQuerySet)()

    class Meta:
        verbose_name = "évènement"
        db_table = "doc_frise_events"
        ordering = ("-date_evenement",)
        base_manager_name = "objects"
        indexes = (
            models.Index(
                "procedure",
                models.F(
                    "date_evenement"
                ).desc(),  # https://github.com/django-extensions/django-extensions/issues/1790
                "type",
                "is_valid",
                name="aaaaa",
            ),
            OversizedIndex(
                "procedure",
                models.F("date_evenement").desc(),
                name="idx_doc_frise_events_procedure_id_date_iso",
            ),
        )

    def __str__(self) -> str:
        return self.type

    def save(self, *args, **kwargs) -> None:  # noqa: ANN002, ANN003
        self.clean()
        if self.procedure:
            self.project_id = self.procedure.project_id
        super().save(*args, **kwargs)

    def clean(self) -> None:
        archive_fields = [self.is_archived, self.archived_by]
        if any(archive_fields) and not all(archive_fields):
            message = "Le champ “archived_by” doit être renseigné uniquement si le champ “archived_at” est renseigné"
            raise ValidationError(message)

    def archive(self, archived_by: Profile) -> None:
        self.archived_by = archived_by
        self.archived_at = timezone.now()

    @property
    def is_archived(self) -> bool:
        return bool(self.archived_at)

    @property
    def category(self) -> EventCategory | None:
        if not self.is_valid:
            return None

        return EVENT_CATEGORY_BY_DOC_TYPE[self.procedure.doc_type].get(self.type)


class Region(models.Model):
    code_insee = models.CharField(unique=True)
    nom = models.CharField()

    def __str__(self) -> str:
        return f"{self.nom} ({self.code_insee})"


class Departement(models.Model):
    code_insee = models.CharField(unique=True)
    nom = models.CharField()
    region = models.ForeignKey(Region, models.DO_NOTHING, related_name="departements")

    def __str__(self) -> str:
        return f"{self.code_insee} - {self.nom}"


class Adhesion(models.Model):
    from_collectivite = models.ForeignKey(
        "core.Collectivite",
        on_delete=models.CASCADE,
        related_name="to_collectivite_through",
        verbose_name="groupement",
    )
    to_collectivite = models.ForeignKey(
        "core.Collectivite",
        on_delete=models.RESTRICT,
        related_name="from_collectivite_through",
        verbose_name="membre",
    )

    class Meta:
        verbose_name = "adhésion"
        verbose_name_plural = "adhésions"
        unique_together = ("from_collectivite", "to_collectivite")
        # The many to many was first created without a manager.
        db_table = "core_collectivite_adhesions"

    def __str__(self) -> str:
        return f"{self.pk}"


class CollectiviteQuerySet(models.QuerySet):
    def portant_scot(self, avant: date | None = None) -> Self:
        procedures_qs = (
            Procedure.objects.with_events(avant=avant)
            .with_concatenated_topics_as_string()
            .order_by("created_at")
            .filter(
                doc_type="SCOT",
                parente=None,
                archived=False,
            )
        )
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
                    procedures_qs,
                    to_attr="scots",
                ),
                models.Prefetch(
                    "scots__perimetre",
                    Commune.objects.with_scots(avant=avant).select_related(
                        "departement__region",
                    ),
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
    # NOTE(cms): this is a copy of `code_insee_unique` containing SIREN codes only.
    # NOTE(cms): add a unique constraint when siren will not be in code_insee_unique anymore.
    siren = models.CharField(blank=True, verbose_name="SIREN", max_length=9)
    # NOTE(cms): this is a copy of `code_insee_unique` containing INSEE codes only.
    # « Grands quartiers » can have up to 7 characters.
    # https://fr.wikipedia.org/wiki/Code_Insee
    code_insee = models.CharField(blank=True, verbose_name="code INSEE", max_length=7)
    type = models.CharField(choices=TypeCollectivite.choices)
    nom = models.CharField()
    competence_plan = models.BooleanField(db_default=False)
    competence_schema = models.BooleanField(db_default=False)
    adhesions = models.ManyToManyField(
        "self",
        related_name="collectivites_adherentes",
        symmetrical=False,
        through="core.Adhesion",
    )
    flat_groups = models.ManyToManyField(
        "self",
        related_name="flat_members",
        through="core.MaterializedViewFlatMembership",
        symmetrical=False,
    )
    departement = models.ForeignKey(
        Departement, models.DO_NOTHING, related_name="collectivites"
    )

    objects = CollectiviteQuerySet.as_manager()

    def __str__(self) -> str:
        return f"{self.nom} ({self.code_insee_unique})"

    def save(self, *args: list, **kwargs: dict) -> None:
        self.clean()
        super().save(*args, **kwargs)

    def clean(self) -> None:
        if self.code_insee and not self.is_commune:
            raise ValidationError("Seules les communes peuvent avoir un code INSEE.")  # noqa: EM101, TRY003
        super().clean()

    @property
    def is_commune(self) -> bool:
        return self.type in (
            TypeCollectivite.COM,
            TypeCollectivite.COMA,
            TypeCollectivite.COMD,
        )

    @cached_property
    def _scots_opposables(self) -> list[Procedure]:
        return [
            scot
            for scot in self.scots
            if scot.statut == EventCategory.APPROUVE
            and any(commune.is_opposable(scot) for commune in scot.communes)
        ]

    @cached_property
    def _scot_en_cours(self) -> Procedure | None:
        en_cours = [procedure for procedure in self.scots if procedure.is_en_cours]

        if not en_cours:
            return None

        if len(en_cours) > 1:
            logger.error(
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
    def with_procedures_principales(self, *, avant: date | None = None) -> Self:
        procedures_principales = (
            Procedure.objects.with_concatenated_topics_as_string()
            .with_events(avant=avant)
            .filter(parente=None, archived=False)
        )

        return self.prefetch_related(
            models.Prefetch(
                "procedures", procedures_principales, to_attr="procedures_principales"
            )
        )

    def with_scots(self, avant: date | None = None) -> Self:
        return self.prefetch_related(
            models.Prefetch(
                "procedures",
                Procedure.objects.with_events(avant=avant).filter(
                    doc_type="SCOT", parente=None, archived=False
                ),
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

    class Meta:
        indexes = (
            # perimetre__count utilise commune__nouvelle=None pour savoir si une commune est déléguée.
            # Cet index partiel permet un Index Only Scan (au lieu de Index Scan)
            models.Index(
                fields=["collectivite_ptr"],
                condition=models.Q(nouvelle__isnull=True),
                name="collectivite_nouvelle_null_idx",
                opclasses=["varchar_pattern_ops"],
            ),
        )

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
        return sorted(
            (
                procedure
                for procedure in self.procedures_principales
                if procedure.type != "Abrogation"
                and procedure.statut == EventCategory.APPROUVE
            ),
            reverse=True,
        )

    @cached_property
    def procedures_principales_en_cours(self) -> list[Procedure]:
        return sorted(
            (
                procedure
                for procedure in self.procedures_principales
                if procedure.is_en_cours
            ),
            reverse=True,
        )

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
    def plan_en_cours(self) -> Procedure | None:
        return next(
            (
                procedure
                for procedure in self.procedures_principales_en_cours
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

    @property
    def collectivite_porteuse(self) -> Collectivite:
        if self.plan_en_cours:
            return self.plan_en_cours.collectivite_porteuse
        if self.plan_opposable:
            return self.plan_opposable.collectivite_porteuse
        return self

    def is_opposable(self, procedure: Procedure) -> bool:
        return procedure in (self.plan_opposable, self.schema_opposable)

    @property
    def is_nouvelle(self) -> bool:
        return self.deleguee.count() > 0

    @property
    def code_etat_simplifie(self) -> str:
        code_type_opposable = (
            self.plan_opposable.type_document_code if self.plan_opposable else 9
        )
        code_type_en_cours = (
            self.plan_en_cours.type_document_code if self.plan_en_cours else 9
        )
        return f"{code_type_opposable}{code_type_en_cours}"

    @property
    def code_etat_complet(self) -> str:
        code_type_opposable = (
            self.plan_opposable.type_document_code if self.plan_opposable else 9
        )
        code_competence_opposable = (
            self.plan_opposable.competence_intercommunalite_code(
                self.collectivite_porteuse
            )
            if self.plan_opposable
            else 9
        )
        code_type_en_cours = (
            self.plan_en_cours.type_document_code if self.plan_en_cours else 9
        )
        code_competence_en_cours = (
            self.plan_en_cours.competence_intercommunalite_code(
                self.collectivite_porteuse
            )
            if self.plan_en_cours
            else 9
        )
        return f"{code_type_opposable}{code_competence_opposable}{code_type_en_cours}{code_competence_en_cours}"

    @property
    def libelle_code_etat_simplifie(self) -> str:
        return CODE_ETAT_SIMPLIFIE_TO_LIBELLE[self.code_etat_simplifie]

    @property
    def libelle_code_etat_complet(self) -> str:
        return CODE_ETAT_COMPLET_TO_LIBELLE.get(self.code_etat_complet, "")


class CommuneProcedure(models.Model):  # noqa: DJ008
    id = models.UUIDField(primary_key=True, db_default=RandomUUID())

    # Created for Nuxt before Django models were here.
    # It should be refactored when working on the COG.
    commune_id = models.GeneratedField(
        expression=models.functions.Concat(
            "collectivite_code",
            models.Value("_"),
            "collectivite_type",
        ),
        output_field=models.TextField(),
        db_persist=True,
    )
    # Use the commune_id (GeneratedField) as a foreign key.
    commune = models.ForeignObject(
        Commune,
        from_fields=["commune_id"],
        to_fields=["collectivite_ptr_id"],
        on_delete=models.DO_NOTHING,
    )
    procedure = models.ForeignKey(
        Procedure, models.CASCADE, related_name="perimetre_through"
    )
    collectivite_code = models.TextField(
        verbose_name="Code collectivité",
    )
    collectivite_type = models.TextField(
        verbose_name="Type de collectivité",
        choices=CommuneType,
        default=CommuneType.COM,
    )
    opposable = models.BooleanField(verbose_name="Est opposable", default=False)
    # Denormalized version of commune.departement.code_insee already existing in production.
    # Real type is TextField but I used a Charfiel here for performance reasons.
    # This column is used in Nuxt side to retrieve procedures by departement.
    # See urbanizator.getProceduresForDept.
    # Unfortunately, there is a mismatch between commune.departement.code_insee and self.departement
    # in some records.
    # This should be treated globally when refactoring departements usage as well in Django and in Nuxt.
    # In the meantine, add it in the model so we can use it with the ORM.
    departement = models.TextField(null=True, blank=True)  # noqa: DJ001

    created_at = models.DateTimeField(db_default=TransactionNow())
    added_at = models.DateTimeField(db_default=TransactionNow(), null=True)

    class Meta:
        db_table = "procedures_perimetres"
        verbose_name = "Périmètre"
        constraints = (
            models.UniqueConstraint(
                fields=[
                    "collectivite_code",
                    "procedure",
                    "collectivite_type",
                ],
                name="uniq_perimeters_collectivite_procedure_type_couple_ids",
            ),
        )
        indexes = [  # noqa: RUF012
            models.Index(name="departement_idx", fields=["departement"]),
            OversizedIndex(
                name="procedure_including_commune_idx",
                fields=["procedure_id"],
                include=["commune_id"],
            ),
            OversizedIndex(
                name="procedures_perimetres_commune_id_idx", fields=["commune_id"]
            ),
            OversizedIndex(
                name="procedures_perimetres_commune_id_including_procedure",
                fields=["commune_id"],
                include=["procedure_id"],
            ),
            # Remove me later.
            models.Index(name="test_idx", fields=["procedure_id", "collectivite_code"]),
        ]


class MaterializedViewFlatMembershipQuerySet(models.QuerySet):
    def create(self, *args: list, **kwargs: dict) -> Exception:  # noqa: ARG002
        raise PermissionDenied(self.model.READ_ONLY_EXCEPTION_MSG)

    def bulk_create(self, *args: list, **kwargs: dict) -> Exception:  # noqa: ARG002
        raise PermissionDenied(self.model.READ_ONLY_EXCEPTION_MSG)

    def bulk_update(self, *args: list, **kwargs: dict) -> Exception:  # noqa: ARG002
        raise PermissionDenied(self.model.READ_ONLY_EXCEPTION_MSG)

    def delete(self, *args: list, **kwargs: dict) -> Exception:  # noqa: ARG002
        raise PermissionDenied(self.model.READ_ONLY_EXCEPTION_MSG)


class MaterializedViewFlatMembership(models.Model):
    READ_ONLY_EXCEPTION_MSG = (
        "ViewCommuneAdhesionsDeep is read only because it is a materialized view."
        "Refresh the table with ViewCommuneAdhesionsDeep.refresh()"
    )

    id = models.UUIDField(primary_key=True, db_default=RandomUUID())
    member = models.ForeignKey(
        "core.Collectivite",
        models.DO_NOTHING,
        related_name="flat_groups_through",
        verbose_name="Membre",
    )
    group = models.ForeignKey(
        "core.Collectivite",
        models.DO_NOTHING,
        related_name="flat_members_through",
        verbose_name="Groupement",
    )
    member_type = models.CharField(choices=TypeCollectivite.choices)
    group_type = models.CharField(choices=TypeCollectivite.choices)

    objects = MaterializedViewFlatMembershipQuerySet.as_manager()

    class Meta:
        db_table = "materialized_view_flat_memberships"
        managed = False
        indexes = (
            models.Index(
                "member",
                name="member_id_idx",
                include=("group_id",),
            ),
            models.Index(
                "group",
                name="group_id_idx",
                include=("member_id",),
            ),
            models.Index(
                fields=["group_id", "member_type"],
                name="group_id_member_type_idx",
                include=("member_id",),
            ),
            models.Index(
                fields=["member_id", "group_type"],
                name="member_id_group_type_idx",
                include=("group_id",),
            ),
            models.Index(
                "member_type",
                name="member_type_idx",
            ),
        )

    def __str__(self) -> str:
        return str(self.id)

    def save_base(self, *args: list, **kwargs: dict) -> Exception:  # noqa: ARG002
        raise PermissionDenied(self.READ_ONLY_EXCEPTION_MSG)

    def delete(self, *args: list, **kwargs: dict) -> Exception:  # noqa: ARG002
        raise PermissionDenied(self.READ_ONLY_EXCEPTION_MSG)

    @classmethod
    def refresh(cls) -> None:
        with connection.cursor() as cursor:
            cursor.execute(f"REFRESH MATERIALIZED VIEW {cls._meta.db_table}")
