from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import connection


def update_trigger_sql(nuxt3_url: str) -> str:
    return f"""
    ALTER TABLE doc_frise_events
    DISABLE TRIGGER trigger_event_procedure_status_handler;

    CREATE OR REPLACE FUNCTION public.event_procedure_status_handler() RETURNS trigger
        LANGUAGE plpgsql
        AS $$ declare procedure procedures; event_processed doc_frise_events;
        BEGIN
            IF TG_OP = 'UPDATE' OR TG_OP = 'INSERT' then event_processed := new;
            else event_processed := old;
            END IF;
            SELECT * into procedure FROM procedures WHERE id = event_processed.procedure_id;
            PERFORM set_procedure_status(procedure);
            /* NUXT3_API_URL is hardcoded here because this dump will disappear soon and I don't know how to change it quickly in SQL. */
            PERFORM net.http_get('{nuxt3_url}/api/urba/procedures/' || event_processed.procedure_id || '/update');
        return event_processed; END; $$;

            ALTER TABLE doc_frise_events
    ENABLE TRIGGER trigger_event_procedure_status_handler;
    """  # noqa: S608


class Command(BaseCommand):
    help = "Update the trigger calling Nuxt3's endpoint."

    def handle(self, *args: list, **options: dict) -> None:  # noqa: ARG002
        if not settings.NUXT3_API_URL:
            raise KeyError("NUXT3_API_URL is not set.")  # noqa: EM101, TRY003

        with connection.cursor() as cursor:
            cursor.execute(update_trigger_sql(nuxt3_url=settings.NUXT3_API_URL))
        self.stdout.write(
            "event_procedure_status_handler has been updated successfully."
        )
