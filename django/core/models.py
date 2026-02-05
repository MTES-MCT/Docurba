import logging
import uuid
from datetime import date
from enum import IntEnum, StrEnum, auto
from functools import cached_property
from operator import attrgetter
from typing import Self

from django.db import connection, models
from django.urls import reverse
from django.utils import timezone

logger = logging.getLogger(__name__)


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
    PRESCRIPTION = auto()
    APPROUVE = auto()
    ABANDON = auto()
    ANNULE = auto()
    CADUC = auto()
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
        "Abandon": EventCategory.ABANDON,
        "Retrait de la délibération de prescription": EventCategory.ABANDON,
        "Annulation TA totale": EventCategory.ANNULE,
        "Annulation TA": EventCategory.ANNULE,
        "Abrogation effective": EventCategory.ANNULE,
        "Arrêt de projet": EventCategory.ARRET_DE_PROJET,
        "Porter à connaissance": EventCategory.PORTER_A_CONNAISSANCE,
        "Porter à connaissance complémentaire": EventCategory.PORTER_A_CONNAISSANCE_COMPLEMENTAIRE,
        "Publication de périmètre": EventCategory.PUBLICATION_PERIMETRE,
        "Publication périmètre": EventCategory.PUBLICATION_PERIMETRE,
        "Caractère exécutoire": EventCategory.CARACTERE_EXECUTOIRE,
        "Fin d'échéance": EventCategory.FIN_ECHEANCE,
    },
    TypeDocument.SCOT: {
        "Prescription": EventCategory.PRESCRIPTION,
        "Délibération de l'Etablissement Public": EventCategory.PRESCRIPTION,
        "Délibération de l'établissement public qui prescrit": EventCategory.PRESCRIPTION,
        "Retrait de la délibération d'approbation": EventCategory.PRESCRIPTION,
        "Délibération d'approbation": EventCategory.APPROUVE,
        "Retrait de l'annulation totale": EventCategory.APPROUVE,
        "Abandon": EventCategory.ABANDON,
        "Retrait de la délibération de prescription": EventCategory.ABANDON,
        "Annulation TA totale": EventCategory.ANNULE,
        "Annulation TA": EventCategory.ANNULE,
        "Caducité": EventCategory.CADUC,
        "Arrêt de projet": EventCategory.ARRET_DE_PROJET,
        "Porter à connaissance": EventCategory.PORTER_A_CONNAISSANCE,
        "Porter à connaissance complémentaire": EventCategory.PORTER_A_CONNAISSANCE_COMPLEMENTAIRE,
        "Publication de périmètre": EventCategory.PUBLICATION_PERIMETRE,
        "Publication périmètre": EventCategory.PUBLICATION_PERIMETRE,
        "Publication du périmètre par le préfet": EventCategory.PUBLICATION_PERIMETRE,
        "Caractère exécutoire": EventCategory.CARACTERE_EXECUTOIRE,
        "Fin d'échéance": EventCategory.FIN_ECHEANCE,
    },
    TypeDocument.SD: {
        "Prescription": EventCategory.PRESCRIPTION,
        "Délibération de l'établissement public qui prescrit": EventCategory.PRESCRIPTION,
        "Délibération d'approbation": EventCategory.APPROUVE,
        "Abandon": EventCategory.ABANDON,
        "Annulation TA totale": EventCategory.ANNULE,
        "Annulation TA": EventCategory.ANNULE,
        "Caducité": EventCategory.CADUC,
    },
    TypeDocument.PLU: {
        "Prescription": EventCategory.PRESCRIPTION,
        "Délibération de prescription du conseil municipal ou communautaire": EventCategory.PRESCRIPTION,
        "Retrait de l'annulation totale": EventCategory.APPROUVE,
        "Délibération d'approbation du municipal ou communautaire": EventCategory.APPROUVE,
        "Délibération d'approbation du conseil municipal ou communautaire": EventCategory.APPROUVE,
        "Délibération d'approbation": EventCategory.APPROUVE,
        "Abandon": EventCategory.ABANDON,
        "Retrait de la délibération de prescription": EventCategory.ABANDON,
        "Annulation TA totale": EventCategory.ANNULE,
        "Annulation TA": EventCategory.ANNULE,
        "Abrogation": EventCategory.ANNULE,
        "Arrêté d'abrogation": EventCategory.ANNULE,
        "Caducité": EventCategory.CADUC,
        "Arrêt de projet": EventCategory.ARRET_DE_PROJET,
        "Porter à connaissance": EventCategory.PORTER_A_CONNAISSANCE,
        "Porter à connaissance complémentaire": EventCategory.PORTER_A_CONNAISSANCE_COMPLEMENTAIRE,
        "Publication de périmètre": EventCategory.PUBLICATION_PERIMETRE,
        "Publication périmètre": EventCategory.PUBLICATION_PERIMETRE,
        "Caractère exécutoire": EventCategory.CARACTERE_EXECUTOIRE,
        "Fin d'échéance": EventCategory.FIN_ECHEANCE,
    },
    TypeDocument.POS: {
        "Prescription": EventCategory.PRESCRIPTION,
        "Délibération de prescription du conseil municipal ou communautaire": EventCategory.PRESCRIPTION,
        "Délibération d'approbation du municipal ou communautaire": EventCategory.APPROUVE,
        "Délibération d'approbation du conseil municipal ou communautaire": EventCategory.APPROUVE,
        "Délibération d'approbation": EventCategory.APPROUVE,
        "Abandon": EventCategory.ABANDON,
        "Annulation TA": EventCategory.ANNULE,
        "Annulation TA totale": EventCategory.ANNULE,
        "Caducité": EventCategory.ANNULE,
        "Arrêt de projet": EventCategory.ARRET_DE_PROJET,
        "Porter à connaissance": EventCategory.PORTER_A_CONNAISSANCE,
        "Porter à connaissance complémentaire": EventCategory.PORTER_A_CONNAISSANCE_COMPLEMENTAIRE,
        "Publication de périmètre": EventCategory.PUBLICATION_PERIMETRE,
        "Publication périmètre": EventCategory.PUBLICATION_PERIMETRE,
        "Caractère exécutoire": EventCategory.CARACTERE_EXECUTOIRE,
        "Fin d'échéance": EventCategory.FIN_ECHEANCE,
    },
}
EVENT_CATEGORY_BY_DOC_TYPE |= dict.fromkeys(
    PLU_LIKE, EVENT_CATEGORY_BY_DOC_TYPE[TypeDocument.PLU]
)


class ProcedureQuerySet(models.QuerySet):
    def with_events(self, *, avant: date | None = None) -> Self:
        events = Event.objects.exclude(date_evenement=None)
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
                    ViewCommuneAdhesionsDeep.objects.filter(
                        groupement=models.OuterRef("collectivite_porteuse__id")
                    )
                    .values("groupement")
                    .annotate(
                        communes_adherentes__count=models.Count("commune"),
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

    def without_adhesions_count(self) -> Self:
        self.query.annotations.pop("communes_adherentes__count")
        return self


class ProcedureManager(models.Manager):
    def get_queryset(self) -> ProcedureQuerySet:
        return (
            super()
            .get_queryset()
            .with_perimetre_counts()
            .with_communes_counts()
            .select_related("collectivite_porteuse__departement__region")
        )


class Procedure(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    doc_type = models.CharField(choices=TypeDocument, blank=True, null=True)  # noqa: DJ001
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
    is_principale = models.BooleanField(blank=True, null=True)
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
    current_perimetre = models.JSONField(null=True)
    initial_perimetre = models.JSONField(null=True)

    objects = ProcedureManager.from_queryset(ProcedureQuerySet)()

    class Meta:
        managed = False
        db_table = "procedures"

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
            # self.perimetre_count is set when calling Procedure.objects.with_perimetre_counts
            # which is always called on the manager (see ProcedureManager.get_queryset).
            # For the moment, it is mandatory to know if the procedure is_intercommunal.
            # The type_document is used to generate the self representation, thus on the Django admin.
            # For an unknown reason, the ProcedureManager is used on the "list" view but not on the "change" one.
            # This should be refactored some day as this hack is quite ugly.
            try:
                getattr(self, "perimetre__count")  # noqa: B009
            except AttributeError:
                self.perimetre__count = self.perimetre.count()

            if not self.is_intercommunal:
                return TypeDocument.PLU
            if self.vaut_PLH_consolide and self.vaut_PDM_consolide:
                return TypeDocument.PLUIHM
            if self.vaut_PLH_consolide:
                return TypeDocument.PLUIH
            if self.vaut_PDM_consolide:
                return TypeDocument.PLUIM
            return TypeDocument.PLUI

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
        return self.perimetre__count > 1

    @property
    def is_sectoriel_consolide(self) -> bool:
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


class Event(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    procedure = models.ForeignKey(Procedure, models.DO_NOTHING)
    type = models.TextField(blank=True, null=True)  # noqa: DJ001
    date_evenement = models.DateField(db_column="date_iso", null=True)
    is_valid = models.BooleanField(db_default=True)

    class Meta:
        managed = False
        db_table = "doc_frise_events"
        ordering = ("-date_evenement",)

    def __str__(self) -> str:
        return f"{self.procedure}  - {self.type}"

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
                    .without_adhesions_count()
                    .filter(
                        doc_type="SCOT",
                        parente=None,
                        archived=False,
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
        return f"{self.nom} ({self.code_insee_unique})"

    @property
    def code_insee(self) -> str:
        return self.id.split("_")[0]

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
    def with_procedures_principales(
        self, *, avant: date | None = None, with_adhesions_count: bool = True
    ) -> Self:
        procedures_principales = Procedure.objects.with_events(avant=avant).filter(
            parente=None, archived=False
        )
        if not with_adhesions_count:
            procedures_principales = procedures_principales.without_adhesions_count()

        return self.prefetch_related(
            models.Prefetch(
                "procedures", procedures_principales, to_attr="procedures_principales"
            )
        )

    def csv_prefetch(self) -> Self:
        return self.select_related(
            "departement__region", "intercommunalite__departement__region"
        ).prefetch_related("deleguee")

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
    adhesions_deep = models.ManyToManyField(
        Collectivite,
        through="ViewCommuneAdhesionsDeep",
        related_name="communes_adherentes_deep",
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
        try:
            return CODE_ETAT_COMPLET_TO_LIBELLE[self.code_etat_complet]
        except KeyError:
            logger.exception(
                "Code état (%s) incohérent pour %s",
                self.code_etat_complet,
                self.code_insee,
            )
            return ""


class CommuneProcedure(models.Model):  # noqa: DJ008
    commune = models.ForeignKey(Commune, models.DO_NOTHING, db_constraint=False)
    procedure = models.ForeignKey(Procedure, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = "procedures_perimetres"
        verbose_name = "Périmètre"


class ViewCommuneAdhesionsDeep(models.Model):  # noqa: DJ008
    commune = models.ForeignKey(Commune, models.DO_NOTHING, related_name="+")
    groupement = models.ForeignKey(Collectivite, models.DO_NOTHING, related_name="+")

    class Meta:
        db_table = "view_commune_adhesions_deep"
        managed = False

    @classmethod
    def _refresh_materialized_view(cls) -> None:
        """Uniquement pour les tests."""
        with connection.cursor() as cursor:
            cursor.execute(f"REFRESH MATERIALIZED VIEW {cls._meta.db_table}")
