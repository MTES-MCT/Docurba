import django.contrib.postgres.functions
import django.db.models.deletion
import pgtrigger.compiler
import pgtrigger.migrations
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0012_json_to_jsonb"),
        ("pghistory", "0007_auto_20250421_0444"),
        ("users", "0004_remove_profile_collectivite_id_profile_collectivite_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="EventsSnapshot",
            fields=[
                ("pgh_id", models.AutoField(primary_key=True, serialize=False)),
                ("pgh_created_at", models.DateTimeField(auto_now_add=True)),
                ("pgh_label", models.TextField(help_text="The event label.")),
                (
                    "id",
                    models.UUIDField(
                        db_default=django.contrib.postgres.functions.RandomUUID(),
                        editable=False,
                        serialize=False,
                    ),
                ),
                ("type", models.CharField(blank=True, null=True)),
                ("date_evenement", models.DateField(db_column="date_iso", null=True)),
                ("is_valid", models.BooleanField(db_default=True)),
                (
                    "visibility",
                    models.CharField(
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
                ("description", models.TextField(blank=True, null=True)),
                (
                    "created_at",
                    models.DateTimeField(
                        blank=True,
                        db_default=django.contrib.postgres.functions.TransactionNow(),
                        editable=False,
                        null=True,
                    ),
                ),
                (
                    "updated_at",
                    models.DateTimeField(
                        blank=True,
                        db_default=django.contrib.postgres.functions.TransactionNow(),
                        editable=False,
                        null=True,
                    ),
                ),
                (
                    "attachements",
                    models.JSONField(blank=True, editable=False, null=True),
                ),
                (
                    "from_sudocuh",
                    models.IntegerField(blank=True, editable=False, null=True),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        pgtrigger.migrations.AddTrigger(
            model_name="event",
            trigger=pgtrigger.compiler.Trigger(
                name="insert_insert",
                sql=pgtrigger.compiler.UpsertTriggerSql(
                    func='INSERT INTO "core_eventssnapshot" ("attachements", "created_at", "date_iso", "description", "from_sudocuh", "id", "is_valid", "pgh_context_id", "pgh_created_at", "pgh_label", "pgh_obj_id", "procedure_id", "profile_id", "type", "updated_at", "visibility") VALUES (NEW."attachements", NEW."created_at", NEW."date_iso", NEW."description", NEW."from_sudocuh", NEW."id", NEW."is_valid", _pgh_attach_context(), NOW(), \'insert\', NEW."id", NEW."procedure_id", NEW."profile_id", NEW."type", NEW."updated_at", NEW."visibility"); RETURN NULL;',
                    hash="07eace67edf897c7d7fcf7ac522cbd13b0bfb06d",
                    operation="INSERT",
                    pgid="pgtrigger_insert_insert_137f2",
                    table="doc_frise_events",
                    when="AFTER",
                ),
            ),
        ),
        pgtrigger.migrations.AddTrigger(
            model_name="event",
            trigger=pgtrigger.compiler.Trigger(
                name="update_update",
                sql=pgtrigger.compiler.UpsertTriggerSql(
                    condition="WHEN (OLD.* IS DISTINCT FROM NEW.*)",
                    func='INSERT INTO "core_eventssnapshot" ("attachements", "created_at", "date_iso", "description", "from_sudocuh", "id", "is_valid", "pgh_context_id", "pgh_created_at", "pgh_label", "pgh_obj_id", "procedure_id", "profile_id", "type", "updated_at", "visibility") VALUES (NEW."attachements", NEW."created_at", NEW."date_iso", NEW."description", NEW."from_sudocuh", NEW."id", NEW."is_valid", _pgh_attach_context(), NOW(), \'update\', NEW."id", NEW."procedure_id", NEW."profile_id", NEW."type", NEW."updated_at", NEW."visibility"); RETURN NULL;',
                    hash="9f1d73036eace5f85dd6776e354820d2844f5207",
                    operation="UPDATE",
                    pgid="pgtrigger_update_update_d4328",
                    table="doc_frise_events",
                    when="AFTER",
                ),
            ),
        ),
        migrations.AddField(
            model_name="eventssnapshot",
            name="pgh_context",
            field=models.ForeignKey(
                db_constraint=False,
                null=True,
                on_delete=django.db.models.deletion.DO_NOTHING,
                related_name="+",
                to="pghistory.context",
            ),
        ),
        migrations.AddField(
            model_name="eventssnapshot",
            name="pgh_obj",
            field=models.ForeignKey(
                db_constraint=False,
                on_delete=django.db.models.deletion.DO_NOTHING,
                related_name="events",
                to="core.event",
            ),
        ),
        migrations.AddField(
            model_name="eventssnapshot",
            name="procedure",
            field=models.ForeignKey(
                db_constraint=False,
                editable=False,
                null=True,
                on_delete=django.db.models.deletion.DO_NOTHING,
                related_name="+",
                related_query_name="+",
                to="core.procedure",
            ),
        ),
        migrations.AddField(
            model_name="eventssnapshot",
            name="profile",
            field=models.ForeignKey(
                db_constraint=False,
                null=True,
                on_delete=django.db.models.deletion.DO_NOTHING,
                related_name="+",
                related_query_name="+",
                to="users.profile",
            ),
        ),
    ]
