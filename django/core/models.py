from django.db import models


# FIXME: Améliorer les modèles
class Procedures(models.Model):
    id = models.UUIDField(primary_key=True)
    project = models.ForeignKey("Projects", models.DO_NOTHING, blank=True, null=True)
    type = models.TextField(blank=True, null=True)
    commentaire = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    last_updated_at = models.DateTimeField(blank=True, null=True)
    from_sudocuh = models.IntegerField(unique=True, blank=True, null=True)
    collectivite_porteuse_id = models.TextField(blank=True, null=True)
    is_principale = models.BooleanField(blank=True, null=True)
    status = models.TextField(blank=True, null=True)
    secondary_procedure_of = models.ForeignKey(
        "self",
        models.DO_NOTHING,
        db_column="secondary_procedure_of",
        related_name="secondaires",
        blank=True,
        null=True,
    )
    doc_type = models.TextField(blank=True, null=True)
    is_sectoriel = models.BooleanField(blank=True, null=True)
    is_scot = models.BooleanField(blank=True, null=True)
    is_pluih = models.BooleanField(blank=True, null=True)
    is_pdu = models.BooleanField(blank=True, null=True)
    mandatory_pdu = models.BooleanField(blank=True, null=True)
    moe = models.JSONField(blank=True, null=True)
    volet_qualitatif = models.JSONField(blank=True, null=True)
    sudocu_secondary_procedure_of = models.IntegerField(blank=True, null=True)
    departements = models.TextField(
        blank=True, null=True
    )  # This field type is a guess.
    current_perimetre = models.JSONField(blank=True, null=True)
    initial_perimetre = models.JSONField(blank=True, null=True)
    name = models.TextField(blank=True, null=True)
    is_sudocuh_scot = models.BooleanField(blank=True, null=True)
    testing = models.BooleanField(blank=True, null=True)
    numero = models.TextField(blank=True, null=True)
    owner = models.ForeignKey("Profiles", models.DO_NOTHING, blank=True, null=True)
    previous_opposable_procedures_ids = models.ForeignKey(
        "self",
        models.DO_NOTHING,
        db_column="previous_opposable_procedures_ids",
        related_name="procedures_previous_opposable_procedures_ids_set",
        blank=True,
        null=True,
    )
    test = models.BooleanField(blank=True, null=True)
    type_code = models.TextField(blank=True, null=True)
    doc_type_code = models.TextField(blank=True, null=True)
    comment_dgd = models.TextField(blank=True, null=True)
    shareable = models.BooleanField(blank=True, null=True)
    doublon_cache_de = models.OneToOneField(
        "self", on_delete=models.DO_NOTHING, blank=True, null=True, unique=True
    )
    soft_delete = models.BooleanField()
    archived = models.GeneratedField(
        expression=models.Q(doublon_cache_de__isnull=False)
        | models.Q(soft_delete=True),
        output_field=models.BooleanField(),
        db_persist=True,
    )

    class Meta:
        managed = False
        db_table = "procedures"

    def __str__(self) -> str:
        return (
            self.name
            or f"Gen {self.type} {self.numero} {self.doc_type} {self.collectivite_porteuse.nomcollectivite}"
        )


class ProceduresPerimetres(models.Model):
    id = models.UUIDField(primary_key=True)
    created_at = models.DateTimeField()
    added_at = models.DateTimeField(blank=True, null=True)
    collectivite_code = models.TextField()
    collectivite_type = models.TextField()
    procedure = models.ForeignKey(Procedures, models.DO_NOTHING)
    opposable = models.BooleanField()
    departement = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "procedures_perimetres"
        unique_together = (("collectivite_code", "procedure", "collectivite_type"),)
