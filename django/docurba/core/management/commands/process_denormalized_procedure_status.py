import csv

from django.core.management.base import BaseCommand
from django.db import connection

DIFF_QUERY = """
WITH impactful_events AS (
	SELECT DISTINCT ON (e.procedure_id) e.procedure_id, et.impact as impact
	FROM doc_frise_events e
	JOIN core_eventtype et ON e.event_type_id = et.id
	WHERE e.is_valid IS TRUE
	AND e.archived_at IS NULL
	AND e.date_iso IS NOT NULL
	AND et.impact != ''
	ORDER BY e.procedure_id, e.date_iso DESC
), candidates AS (
	SELECT p.id, p.status AS old_status, CASE
		WHEN p.secondary_procedure_of IS NOT NULL THEN NULL
		WHEN e.impact IS NULL THEN 'en projet'
		ELSE e.impact
	END AS new_status
	FROM procedures p
	LEFT JOIN impactful_events e ON p.id = e.procedure_id
), output AS (
    SELECT * FROM candidates
    WHERE COALESCE(old_status, '') != COALESCE(new_status, '')
)
"""

LIST_QUERY = (
    DIFF_QUERY
    + """
SELECT *  FROM output
"""
)

UPDATE_QUERY = (
    DIFF_QUERY
    + """
UPDATE procedures AS p
SET status = o.new_status
FROM output o
WHERE p.id = o.id
RETURNING p.id, o.old_status, o.new_status
"""
)


class Command(BaseCommand):
    help = "Compare procedures.status (Nuxt side) with the newly computed status and export the differences to CSV"

    def add_arguments(self, parser: str) -> None:
        parser.add_argument(
            "--wet-run",
            dest="wet_run",
            action="store_true",
            help="Update procedures.status with the newly computed status",
        )

    def handle(self, *args: list, wet_run: bool, **options: dict) -> None:  # noqa: ARG002
        writer = csv.writer(self.stdout, lineterminator="\n")
        writer.writerow(
            [
                "procedure_id",
                "ancien_status",
                "nouveau_status",
            ]
        )
        with connection.cursor() as cursor:
            cursor.execute(UPDATE_QUERY if wet_run else LIST_QUERY)
            for row in cursor.fetchall():
                writer.writerow(row)
