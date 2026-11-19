import csv
from datetime import date

from django.core.management.base import BaseCommand
from django.db import connection
from django.utils import timezone

from docurba.utils.date import end_of_day

DIFF_QUERY = """
WITH impactful_events AS (
	SELECT DISTINCT ON (p.id) p.id AS procedure_id, e.id AS event_id, e.type, e.date_iso, et.impact,
    CASE et.document_type WHEN 'SCOT' THEN 'SCOT' WHEN 'SD' THEN 'SCOT' ELSE 'PLAN' END AS document_type
	FROM doc_frise_events e
	JOIN core_eventtype et ON e.event_type_id = et.id
	JOIN procedures p ON e.procedure_id = p.id
	WHERE p.secondary_procedure_of IS NULL
	and p.archived IS FALSE
	and e.is_valid IS TRUE
	and e.archived_at IS NULL
	and e.date_iso IS NOT NULL
    AND e.date_iso <= %(date_pivot)s
	and et.impact != ''
	ORDER BY p.id, e.date_iso DESC
), opposable_procedure_for_commune AS (
	SELECT DISTINCT ON (pp.collectivite_code, pp.collectivite_type, e.document_type) pp.id
	FROM procedures_perimetres pp
	JOIN impactful_events e ON e.procedure_id = pp.procedure_id
	WHERE e.impact ='opposable'
	ORDER BY pp.collectivite_code, pp.collectivite_type, e.document_type, e.date_iso DESC
), output AS (
	SELECT pp.id, opposable AS old_opposable, (opp.id IS NOT NULL) AS new_opposable
	FROM procedures_perimetres pp
	LEFT JOIN opposable_procedure_for_commune opp ON pp.id = opp.id
	WHERE opposable != (opp.id IS NOT NULL)
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
UPDATE procedures_perimetres AS pp
SET opposable = o.new_opposable
FROM output o
WHERE pp.id = o.id
RETURNING pp.id, o.old_opposable, o.new_opposable
"""
)


class Command(BaseCommand):
    help = "Compare CommuneProcedure.opposable with the computed opposability and export the differences to CSV"

    def add_arguments(self, parser: str) -> None:
        parser.add_argument(
            "--date_pivot",
            help="Date until which events are taken into account. Defaults to timezone.localdate",
        )
        parser.add_argument(
            "--wet-run",
            dest="wet_run",
            action="store_true",
            help="Update CommuneProcedure.opposable with the computed opposability",
        )

    def handle(
        self,
        *args: list,  # noqa: ARG002
        date_pivot: str,
        wet_run: bool,
        **options: dict,  # noqa: ARG002
    ) -> None:
        writer = csv.writer(self.stdout, lineterminator="\n")
        writer.writerow(
            [
                "commune_procedure_id",
                "old_opposable",
                "new_opposable",
            ]
        )

        _date_pivot = (
            date.fromisoformat(date_pivot) if date_pivot else timezone.localdate()
        )
        with connection.cursor() as cursor:
            cursor.execute(
                UPDATE_QUERY if wet_run else LIST_QUERY,
                {"date_pivot": end_of_day(_date_pivot)},
            )
            for row in cursor.fetchall():
                writer.writerow(row)
