import csv

from django.core.management.base import BaseCommand
from django.db import connection

DIFF_QUERY = """
WITH procedure_ids AS (
	SELECT DISTINCT procedure_id
    FROM doc_frise_events
    GROUP BY procedure_id, date_iso HAVING count(*) > 1
), events AS (
	SELECT procedure_id, e.id, e.date_iso,
	CASE et.impact
		WHEN 'en cours' THEN 1
        WHEN 'abandon' THEN 2
		WHEN 'approuve' THEN 3
		WHEN 'opposable' THEN 4
		WHEN 'annule' THEN 5
		WHEN 'abroge' THEN 6
		WHEN 'caduc' THEN 7
		ELSE 0
	END AS impact_priority, e.created_at, e.from_sudocuh
	FROM procedure_ids p
	JOIN doc_frise_events e USING(procedure_id)
	LEFT JOIN core_eventtype et ON et.id = e.event_type_id
    WHERE date_iso IS NOT NULL
), ordered AS (
	SELECT *, ROW_NUMBER() OVER w - 1 AS priority
	FROM events
	WINDOW w AS (PARTITION BY procedure_id, date_iso ORDER BY impact_priority, created_at, from_sudocuh)
), output AS (
	SELECT id, date_iso AS old_date_iso, date_iso + (priority || ' hour')::INTERVAL AS new_date_iso
	FROM ordered
	WHERE priority > 0
)
"""

LIST_QUERY = (
    DIFF_QUERY
    + """
SELECT * FROM output ORDER BY id
"""
)

UPDATE_QUERY = (
    DIFF_QUERY
    + """
, updated AS (
	UPDATE doc_frise_events AS e
	SET date_iso = o.new_date_iso
	FROM output o
	WHERE e.id = o.id
	RETURNING e.id, o.old_date_iso, o.new_date_iso
)
SELECT * FROM updated
ORDER BY id
"""
)


class Command(BaseCommand):
    help = "Update events date when they have the same date_iso per procedure_id. The new date is priorized by EventType.impact. Export the differences to CSV"

    def add_arguments(self, parser: str) -> None:
        parser.add_argument(
            "--wet-run",
            dest="wet_run",
            action="store_true",
            help="Update doc_frise_events.date_iso with the newly computed event date",
        )

    def handle(self, *args: list, wet_run: bool, **options: dict) -> None:  # noqa: ARG002
        writer = csv.writer(self.stdout, lineterminator="\n")
        writer.writerow(
            [
                "event_id",
                "old_date_iso",
                "new_date_iso",
            ]
        )
        with connection.cursor() as cursor:
            cursor.execute(UPDATE_QUERY if wet_run else LIST_QUERY)
            for row in cursor.fetchall():
                writer.writerow(row)
