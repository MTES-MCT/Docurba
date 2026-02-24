from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0011_communeprocedure_commune_id"),
    ]

    operations = [
        migrations.RunSQL(
            sql="""ALTER TABLE "doc_frise_events"
            ALTER COLUMN "actors" SET DATA TYPE jsonb,
            ALTER COLUMN "attachements" SET DATA TYPE jsonb
            """,
            reverse_sql="""ALTER TABLE "doc_frise_events"
            ALTER COLUMN "actors" SET DATA TYPE json,
            ALTER COLUMN "attachements" SET DATA TYPE json
            """,
        )
    ]
