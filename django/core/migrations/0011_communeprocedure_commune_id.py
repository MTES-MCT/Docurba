import django.db.models.functions.text
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0010_remove_event_date_evenement_string_and_more"),
        ("users", "0004_remove_profile_collectivite_id_profile_collectivite_and_more"),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[],
            state_operations=[
                migrations.AddField(
                    model_name="communeprocedure",
                    name="commune_id",
                    field=models.GeneratedField(
                        db_persist=True,
                        expression=django.db.models.functions.text.Concat(
                            "deprecated_nuxt_collectivite_code",
                            models.Value("_"),
                            "deprecated_nuxt_collectivite_type",
                        ),
                        output_field=models.CharField(),
                    ),
                ),
            ],
        )
    ]
