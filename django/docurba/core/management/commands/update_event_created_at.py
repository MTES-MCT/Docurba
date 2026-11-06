import csv

from django.core.management.base import BaseCommand
from django.db import connection

DIFF_QUERY = """
WITH procedure_ids AS (
	SELECT procedure_id, created_at
    FROM doc_frise_events
    GROUP BY procedure_id, created_at HAVING count(*) > 1
), events AS (
	SELECT
		e.id,
		e.created_at,
		ROW_NUMBER() OVER w - 1 AS event_weight, /* microseconds */
		CASE
			et.impact
			WHEN 'en cours' THEN 1
			WHEN 'approuve' THEN 2
			WHEN 'abandon' THEN 3
			WHEN 'opposable' THEN 4
			WHEN 'annule' THEN 5
			WHEN 'abroge' THEN 6
			WHEN 'caduc' THEN 7
			ELSE 0
		END AS impact_weight /* milliseconds */
	FROM doc_frise_events e
        JOIN procedure_ids p ON e.procedure_id = p.procedure_id AND e.created_at = p.created_at
        LEFT JOIN core_eventtype et ON e.event_type_id = et.id
	WINDOW w AS (PARTITION BY e.procedure_id, e.created_at ORDER BY e.date_iso, e.from_sudocuh)
), output AS (
	SELECT id,
	created_at AS old_created_at,
	created_at + (event_weight || ' us')::interval + (impact_weight || ' ms')::INTERVAL AS new_created_at
	FROM events
    WHERE event_weight != 0 OR impact_weight != 0
)
"""

LIST_QUERY = (
    DIFF_QUERY
    + """
SELECT id, to_char(old_created_at, 'yyyy-mm-dd hh24:mi:ss:us'), to_char(new_created_at, 'yyyy-mm-dd hh24:mi:ss:us') FROM output
"""
)

UPDATE_QUERY = (
    DIFF_QUERY
    + """
UPDATE doc_frise_events AS e
SET created_at = o.new_created_at
FROM output o
WHERE e.id = o.id
RETURNING e.id, to_char(o.old_created_at, 'yyyy-mm-dd hh24:mi:ss:us'), to_char(o.new_created_at, 'yyyy-mm-dd hh24:mi:ss:us')
"""
)


class Command(BaseCommand):
    help = "Update events creation date when they have the same created_at per procedure_id. The new created_at is priorized by EventType.impact. Export the differences to CSV"

    def add_arguments(self, parser: str) -> None:
        parser.add_argument(
            "--wet-run",
            dest="wet_run",
            action="store_true",
            help="Update doc_frise_events.created_at with the newly computed creation date",
        )

    def handle(self, *args: list, wet_run: bool, **options: dict) -> None:  # noqa: ARG002
        writer = csv.writer(self.stdout, lineterminator="\n")
        writer.writerow(
            [
                "event_id",
                "old_created_at",
                "new_created_at",
            ]
        )
        with connection.cursor() as cursor:
            cursor.execute(UPDATE_QUERY if wet_run else LIST_QUERY)
            for row in cursor.fetchall():
                writer.writerow(row)
