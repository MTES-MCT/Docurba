import csv

from django.core.management.base import BaseCommand
from django.db import connection

DIFF_QUERY = """
WITH impactful_events AS (
	SELECT DISTINCT ON (e.procedure_id) e.procedure_id, e.project_id, e.date_iso, et.document_type AS document_type, et.impact as impact
	FROM doc_frise_events e
	JOIN core_eventtype et ON e.event_type_id = et.id
	WHERE e.is_valid IS TRUE
	AND e.archived_at IS NULL
	AND e.date_iso IS NOT NULL
	AND et.impact != ''
	ORDER BY e.procedure_id, e.date_iso DESC
), candidates AS (
	SELECT p.id AS procedure_id, e.project_id, e.date_iso, e.document_type, p.status AS old_status, CASE
		WHEN p.secondary_procedure_of IS NOT NULL THEN NULL
		WHEN e.impact IS NULL THEN 'en projet'
		ELSE e.impact
	END AS new_status
	FROM procedures p
	LEFT JOIN impactful_events e ON p.id = e.procedure_id
), inserts AS (
	SELECT c.procedure_id, c.project_id, c.date_iso + '1 hour'::INTERVAL AS date_iso, et.id AS event_type_id, et.name AS "type", et.sudocuh_code AS code,
    'private' AS visibility,
    TRUE AS is_valid,
    %(profile_id)s::uuid AS created_by_id,
    %(profile_id)s::uuid AS profile_id,
	%(description)s AS description
	FROM candidates c
	JOIN core_eventtype et ON c.document_type = et.document_type AND et.name = 'Caractère exécutoire'
	WHERE old_status = 'opposable' AND new_status = 'approuve'
)
"""

LIST_QUERY = (
    DIFF_QUERY
    + """
SELECT *  FROM inserts
"""
)

UPDATE_QUERY = (
    DIFF_QUERY
    + """
INSERT INTO doc_frise_events
(procedure_id, project_id, date_iso, event_type_id, type, code, visibility, is_valid, created_by_id, profile_id, description)
SELECT * FROM inserts
RETURNING procedure_id, project_id, date_iso, event_type_id, type, code, visibility, is_valid, created_by_id, profile_id, description
"""
)

DESCRIPTION = "Afin de mieux répondre à vos besoins et aux règles métier, nous faisons évoluer les règles de statut : cet événement a été ajouté pour rendre la procédure opposable. Pensez à renseigner la date réelle du caractère exécutoire et à changer la visibilité de l'événement. Si vous avez la moindre question, écrivez-nous à: contact@docurba.beta.gouv.fr"


class Command(BaseCommand):
    help = "Add 'Caractère exécutoire' system event to keep existing procedures 'opposable' since the addition of status 'approuve'"

    def add_arguments(self, parser: str) -> None:
        parser.add_argument(
            "profile_id",
            help="ID of system profile owning the new events",
        )
        parser.add_argument(
            "--wet-run",
            dest="wet_run",
            action="store_true",
            help="Persists changes in database",
        )

    def handle(
        self,
        *args: list,  # noqa: ARG002
        profile_id: str,
        wet_run: bool,
        **options: dict,  # noqa: ARG002
    ) -> None:
        writer = csv.writer(self.stdout, lineterminator="\n")
        writer.writerow(
            [
                "procedure_id",
                "project_id",
                "date_iso",
                "event_type_id",
                "type",
                "code",
                "visibility",
                "is_valid",
                "created_by_id",
                "profile_id",
                "description",
            ]
        )
        with connection.cursor() as cursor:
            cursor.execute(
                UPDATE_QUERY if wet_run else LIST_QUERY,
                {"profile_id": profile_id, "description": DESCRIPTION},
            )
            for row in cursor.fetchall():
                writer.writerow(row)
