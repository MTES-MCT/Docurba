from django.core.management.base import BaseCommand
from django.db import connection, transaction

LINK_EVENT_TYPE_ID_QUERY = """
/* Link event with event_type depending on document_type and (name or sudocuh_name or sudocuh_code) */
WITH events_with_event_type AS (
    SELECT
        e.id AS event_id,
        et.id AS event_type_id
    FROM doc_frise_events e
    JOIN procedures p ON p.id = e.procedure_id
    JOIN core_eventtype et ON (CASE
           WHEN p.doc_type IN ('SCOT', 'SD') AND et.document_type = 'SCOT' THEN 1
           WHEN p.doc_type = 'CC' AND et.document_type = 'CC' THEN 1
           WHEN p.doc_type IN ('PLU', 'PLUi', 'PLUiH', 'PLUiHM', 'PLUiM', 'POS') AND et.document_type = 'PLU' THEN 1
           ELSE 0
           END = 1) AND (
        (COALESCE(e.type, '') != '' AND (e.type = et.name OR e.type = et.sudocuh_name)) OR
        (COALESCE(e.code, '') != '' AND e.code NOT IN ('AVISETAT', 'AUTRE') AND e.code = et.sudocuh_code)
    )
    WHERE e.event_type_id IS NULL
), updated_events AS (
    UPDATE doc_frise_events AS e
    SET event_type_id = et.event_type_id
    FROM events_with_event_type et
    WHERE id = et.event_id
    RETURNING e.*
)
INSERT INTO "history_eventsnapshot"
    ("code", "date_iso", "description", "event_type_id", "from_sudocuh", "procedure_id", "profile_id", "type", "pgh_context_id", "pgh_created_at", "pgh_label", "pgh_obj_id")
    SELECT "code", "date_iso", "description", "event_type_id", "from_sudocuh", "procedure_id", "profile_id", "type", _pgh_attach_context(), NOW(), 'update', "id"
from updated_events;
;

/* Link event with event_type with specific mappings */
WITH mapping AS (SELECT * FROM (VALUES
    ('PLU', 'Débat sur le PADD en conseil municipal', 'Débat sur le PADD en conseil municipal ou communautaire'),
    ('PLU', 'Avis de l''Etat', 'Réception de l''avis de l''État'),
    ('CC', 'Caractère éxécutoire', 'Caractère exécutoire'),
    ('PLU', E'Dérogation au principe d''urbanisation limitée -> consultation CDPENAF\n(délai 3 mois) et saisine Préfet pour avis (4 mois)', E'Dérogation au principe d''urbanisation limitée -> consultation CDPENAF\n(délai 2 mois) et saisine Préfet pour avis (4 mois)'),
    ('PLU', 'Avis des services de l''Etat', 'Réception de l''avis de l''État'),
    ('PLU', 'Avis des services de l''État', 'Réception de l''avis de l''État'),
    ('CC', 'Abrogation : arrêté préfectoral', 'Arrêté préfectoral d''abrogation de la carte communale'),
    ('PLU', 'Avis CDPENAF', 'Réception de l''avis de la CDPENAF'),
    ('CC', 'Abrogation : délibération communautaire', 'Délibération communal ou communautaire d’abrogation de la carte communale'),
    ('PLU', 'Avis Etat', 'Réception de l''avis de l''État'),
    ('PLU', 'Bilan de la concertation', 'Délibération de bilan de la concertation'),
    ('PLU', 'Avis de la DDT', 'Réception de l''avis de l''État')
) AS t (code, event_name, type_name)), events_with_event_type AS (
    SELECT
    e.id AS event_id, et.id AS event_type_id
    FROM mapping
    JOIN doc_frise_events e ON e.type = mapping.event_name
    JOIN "procedures" p ON p.id = e.procedure_id AND (CASE
           WHEN p.doc_type IN ('SCOT', 'SD') AND mapping.code = 'SCOT' THEN 1
           WHEN p.doc_type = 'CC' AND mapping.code = 'CC' THEN 1
           WHEN p.doc_type IN ('PLU', 'PLUi', 'PLUiH', 'PLUiHM', 'PLUiM', 'POS') AND mapping.code = 'PLU' THEN 1
           ELSE 0
           END = 1)
    JOIN core_eventtype et ON et.document_type = mapping.code AND et.name = mapping.type_name
    WHERE e.event_type_id IS NULL
), updated_events AS (
    UPDATE doc_frise_events AS e
    SET event_type_id = et.event_type_id
    FROM events_with_event_type et
    WHERE id = et.event_id
    RETURNING e.*
)
INSERT INTO "history_eventsnapshot"
    ("code", "date_iso", "description", "event_type_id", "from_sudocuh", "procedure_id", "profile_id", "type", "pgh_context_id", "pgh_created_at", "pgh_label", "pgh_obj_id")
    SELECT "code", "date_iso", "description", "event_type_id", "from_sudocuh", "procedure_id", "profile_id", "type", _pgh_attach_context(), NOW(), 'update', "id"
from updated_events;
;
"""  # noqa: RUF001


class Command(BaseCommand):
    help = "Link/unlink event with event_type (doc_frise_events.event_type_id)"

    def handle(self, *args: list, **options: dict) -> None:  # noqa: ARG002
        with connection.cursor() as cursor:
            try:
                cursor.execute("ALTER TABLE doc_frise_events DISABLE TRIGGER USER")
                with transaction.atomic():
                    cursor.execute(LINK_EVENT_TYPE_ID_QUERY)
            finally:
                cursor.execute("ALTER TABLE doc_frise_events ENABLE TRIGGER USER")

        self.stdout.write(
            "doc_frise_events.event_type_id has been updated successfully."
        )
