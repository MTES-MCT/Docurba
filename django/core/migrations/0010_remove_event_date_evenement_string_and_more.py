import django.contrib.postgres.functions
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0009_alter_communeprocedure_options_alter_event_options_and_more"),
        ("users", "0003_alter_profile_options"),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[],
            state_operations=[
                migrations.RemoveField(
                    model_name="event",
                    name="date_evenement_string",
                ),
                migrations.RemoveField(
                    model_name="procedure",
                    name="type_document",
                ),
                migrations.AddField(
                    model_name="communeprocedure",
                    name="commune",
                    field=models.ForeignObject(
                        default=12,
                        from_fields=["commune_id"],
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        to="core.commune",
                        to_fields=["collectivite_ptr_id"],
                    ),
                    preserve_default=False,
                ),
                migrations.AddField(
                    model_name="communeprocedure",
                    name="deprecated_nuxt_collectivite_code",
                    field=models.CharField(db_column="collectivite_code", default=12),
                    preserve_default=False,
                ),
                migrations.AddField(
                    model_name="communeprocedure",
                    name="deprecated_nuxt_collectivite_type",
                    field=models.CharField(db_column="collectivite_type", default=12),
                    preserve_default=False,
                ),
                migrations.AddField(
                    model_name="communeprocedure",
                    name="procedure",
                    field=models.ForeignKey(
                        default=12,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        to="core.procedure",
                    ),
                    preserve_default=False,
                ),
                migrations.AddField(
                    model_name="event",
                    name="procedure",
                    field=models.ForeignKey(
                        editable=False,
                        null=True,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        to="core.procedure",
                    ),
                ),
                migrations.AddField(
                    model_name="event",
                    name="profile",
                    field=models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        to="users.profile",
                    ),
                ),
                migrations.AddField(
                    model_name="procedure",
                    name="collectivite_porteuse",
                    field=models.ForeignKey(
                        db_constraint=False,
                        null=True,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        to="core.collectivite",
                        to_field="code_insee_unique",
                    ),
                ),
                migrations.AddField(
                    model_name="procedure",
                    name="doublon_cache_de",
                    field=models.OneToOneField(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        to="core.procedure",
                    ),
                ),
                migrations.AddField(
                    model_name="procedure",
                    name="parente",
                    field=models.ForeignKey(
                        db_column="secondary_procedure_of",
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="secondaires",
                        to="core.procedure",
                    ),
                ),
                migrations.AddField(
                    model_name="communeprocedure",
                    name="deprecated_nuxt_opposable",
                    field=models.BooleanField(db_column="opposable", default=False),
                ),
                migrations.AddField(
                    model_name="event",
                    name="attachements",
                    field=models.JSONField(blank=True, editable=False, null=True),
                ),
                migrations.AddField(
                    model_name="event",
                    name="created_at",
                    field=models.DateTimeField(
                        blank=True,
                        db_default=django.contrib.postgres.functions.TransactionNow(),
                        editable=False,
                        null=True,
                    ),
                ),
                migrations.AddField(
                    model_name="event",
                    name="date_evenement",
                    field=models.DateField(db_column="date_iso", null=True),
                ),
                migrations.AddField(
                    model_name="event",
                    name="description",
                    field=models.TextField(blank=True, null=True),
                ),
                migrations.AddField(
                    model_name="event",
                    name="from_sudocuh",
                    field=models.IntegerField(
                        blank=True, editable=False, null=True, unique=True
                    ),
                ),
                migrations.AddField(
                    model_name="event",
                    name="updated_at",
                    field=models.DateTimeField(
                        blank=True,
                        db_default=django.contrib.postgres.functions.TransactionNow(),
                        editable=False,
                        null=True,
                    ),
                ),
                migrations.AddField(
                    model_name="event",
                    name="visibility",
                    field=models.CharField(
                        blank=True,
                        choices=[
                            ("public", "Publique - Visible par le grand public"),
                            (
                                "private",
                                "Privé - Visible uniquement par les collaborateur·ices de la procédure",
                            ),
                        ],
                        db_default="public",
                        null=True,
                    ),
                ),
                migrations.AddField(
                    model_name="procedure",
                    name="commentaire",
                    field=models.TextField(blank=True, null=True),
                ),
                migrations.AddField(
                    model_name="procedure",
                    name="doc_type",
                    field=models.CharField(
                        blank=True,
                        choices=[
                            ("CC", "Cc"),
                            ("SCOT", "Scot"),
                            ("SD", "Sd"),
                            ("PLU", "Plu"),
                            ("POS", "Pos"),
                            ("PLUi", "Plui"),
                            ("PLUiH", "Pluih"),
                            ("PLUiHM", "Pluihm"),
                            ("PLUiM", "Pluim"),
                        ],
                        null=True,
                    ),
                ),
                migrations.AddField(
                    model_name="procedure",
                    name="from_sudocuh",
                    field=models.IntegerField(blank=True, null=True, unique=True),
                ),
                migrations.AddField(
                    model_name="procedure",
                    name="is_principale",
                    field=models.BooleanField(blank=True, null=True),
                ),
                migrations.AddField(
                    model_name="procedure",
                    name="maitrise_d_oeuvre",
                    field=models.JSONField(db_column="moe", null=True),
                ),
                migrations.AddField(
                    model_name="procedure",
                    name="obligation_PDU",
                    field=models.BooleanField(
                        blank=True, db_column="mandatory_pdu", null=True
                    ),
                ),
                migrations.AddField(
                    model_name="procedure",
                    name="status",
                    field=models.CharField(
                        blank=True,
                        choices=[
                            ("annule", "Annulé"),
                            ("en cours", "En cours"),
                            ("caduc", "Caduc"),
                            ("abandon", "Abandon"),
                            ("opposable", "Opposable"),
                        ],
                        null=True,
                    ),
                ),
                migrations.AddField(
                    model_name="procedure",
                    name="vaut_PDM",
                    field=models.BooleanField(
                        blank=True, db_column="is_pdu", null=True
                    ),
                ),
                migrations.AddField(
                    model_name="procedure",
                    name="vaut_PLH",
                    field=models.BooleanField(
                        blank=True, db_column="is_pluih", null=True
                    ),
                ),
                migrations.AddField(
                    model_name="procedure",
                    name="vaut_SCoT",
                    field=models.BooleanField(
                        blank=True, db_column="is_scot", null=True
                    ),
                ),
                migrations.AlterField(
                    model_name="communeprocedure",
                    name="id",
                    field=models.UUIDField(
                        db_default=django.contrib.postgres.functions.RandomUUID(),
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                migrations.AlterField(
                    model_name="event",
                    name="id",
                    field=models.UUIDField(
                        db_default=django.contrib.postgres.functions.RandomUUID(),
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                migrations.AlterField(
                    model_name="event",
                    name="type",
                    field=models.CharField(blank=True, null=True),
                ),
                migrations.AlterField(
                    model_name="procedure",
                    name="created_at",
                    field=models.DateTimeField(
                        db_default=django.contrib.postgres.functions.TransactionNow(),
                        null=True,
                    ),
                ),
                migrations.AlterField(
                    model_name="procedure",
                    name="id",
                    field=models.UUIDField(
                        db_default=django.contrib.postgres.functions.RandomUUID(),
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                migrations.AddConstraint(
                    model_name="communeprocedure",
                    constraint=models.UniqueConstraint(
                        models.F("deprecated_nuxt_collectivite_code"),
                        models.F("procedure"),
                        models.F("deprecated_nuxt_collectivite_type"),
                        name="uniq_perimeters_collectivite_procedure_type_couple_ids",
                    ),
                ),
                migrations.AddConstraint(
                    model_name="procedure",
                    constraint=models.UniqueConstraint(
                        models.F("id"),
                        condition=models.Q(("archived", False), ("parente", None)),
                        name="procedures_pkey_secondary_null_not_archived",
                    ),
                ),
            ],
        )
    ]
