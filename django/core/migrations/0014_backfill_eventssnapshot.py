from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0013_eventssnapshot_event_insert_insert_and_more"),
    ]

    operations = [
        migrations.RunSQL(
            """
        ALTER TABLE doc_frise_events
            DISABLE TRIGGER handle_updated_at,
            DISABLE TRIGGER trigger_event_procedure_status_handler;

        UPDATE doc_frise_events
        SET
            is_valid = is_valid;


        ALTER TABLE doc_frise_events
            ENABLE TRIGGER handle_updated_at,
            ENABLE TRIGGER trigger_event_procedure_status_handler;
        """,
            reverse_sql=migrations.RunSQL.noop,
        )
    ]
