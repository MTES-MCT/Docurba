import django.contrib.postgres.fields
import django.db.models.deletion
import django.db.models.functions.datetime
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0010_remove_event_date_evenement_string_and_more"),
        ("users", "0003_alter_profile_options"),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[],
            state_operations=[
                migrations.RemoveField(
                    model_name="profile",
                    name="collectivite_id",
                ),
                migrations.AddField(
                    model_name="profile",
                    name="collectivite",
                    field=models.ForeignKey(
                        blank=True,
                        db_constraint=False,
                        null=True,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        to="core.collectivite",
                        to_field="code_insee_unique",
                    ),
                ),
                migrations.AddField(
                    model_name="profile",
                    name="departements",
                    field=django.contrib.postgres.fields.ArrayField(
                        base_field=models.CharField(blank=True, max_length=3),
                        blank=True,
                        null=True,
                        size=None,
                        verbose_name="Départements",
                    ),
                ),
                migrations.AlterField(
                    model_name="profile",
                    name="created_at",
                    field=models.DateTimeField(
                        db_default=django.db.models.functions.datetime.Now(),
                        editable=False,
                        verbose_name="Date de création",
                    ),
                ),
                migrations.AlterField(
                    model_name="profile",
                    name="departement",
                    field=models.ForeignKey(
                        blank=True,
                        db_column="departement",
                        db_constraint=False,
                        null=True,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        to="core.departement",
                        to_field="code_insee",
                    ),
                ),
                migrations.AlterField(
                    model_name="profile",
                    name="is_admin",
                    field=models.BooleanField(
                        db_comment="super admin bypass",
                        default=False,
                        help_text="Donne tous les droits",
                        verbose_name="Super Admin",
                    ),
                ),
                migrations.AlterField(
                    model_name="profile",
                    name="is_staff",
                    field=models.BooleanField(
                        default=False, help_text="Cache le compte", verbose_name="Staff"
                    ),
                ),
                migrations.AlterField(
                    model_name="profile",
                    name="other_poste",
                    field=django.contrib.postgres.fields.ArrayField(
                        base_field=models.CharField(
                            blank=True,
                            choices=[
                                (
                                    "chef_unite",
                                    "Chef·fe d'unité/de bureau/de service et adjoint·e",
                                ),
                                ("redacteur_pac", "Rédacteur·ice de PAC"),
                                (
                                    "suivi_procedures",
                                    "Chargé·e de l'accompagnement des collectivités",
                                ),
                                ("referent_sudocuh", "Référent·e Sudocuh"),
                            ],
                        ),
                        blank=True,
                        help_text="chef_unite<br>redacteur_pac<br>suivi_procedures<br>referent_sudocuh",
                        null=True,
                        size=None,
                        verbose_name="Role(s)",
                    ),
                ),
                migrations.AlterField(
                    model_name="profile",
                    name="region",
                    field=models.ForeignKey(
                        blank=True,
                        db_column="region",
                        db_comment="Si l'utilisateur est une DREAL ou une PPA : région de son périmètre. La colonne peut être remplie pour les autres types.",
                        db_constraint=False,
                        null=True,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        to="core.region",
                        to_field="code_insee",
                    ),
                ),
                migrations.AlterField(
                    model_name="profile",
                    name="side",
                    field=models.CharField(
                        choices=[
                            ("etat", "État"),
                            ("collectivite", "Collectivité"),
                            ("ppa", "PPA"),
                        ],
                        null=True,
                        verbose_name="Side",
                    ),
                ),
            ],
        )
    ]
