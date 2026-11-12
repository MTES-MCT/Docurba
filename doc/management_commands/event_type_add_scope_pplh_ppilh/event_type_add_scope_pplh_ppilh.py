from django.core.management.base import BaseCommand
from django.db import connection, transaction

UPDATE_SCOPE_QUERY = """
WITH t1 AS (SELECT * FROM core_eventtype WHERE '{scope}' = ANY ({field}) AND NOT '{scope}lh' = ANY ({field}))
UPDATE core_eventtype AS et
SET {field} = array_append(et.{field}, '{scope}lh')
FROM t1
WHERE et.id = t1.id;
"""


class Command(BaseCommand):
    help = "Add scopes pplh and ppilh to scope_list & scope_sugg containing pp and ppi scopes"

    def handle(self, *args: list, **options: dict) -> None:  # noqa: ARG002
        queries = [
            UPDATE_SCOPE_QUERY.format(field="scope_list", scope="pp"),
            UPDATE_SCOPE_QUERY.format(field="scope_list", scope="ppi"),
            UPDATE_SCOPE_QUERY.format(field="scope_sugg", scope="pp"),
            UPDATE_SCOPE_QUERY.format(field="scope_sugg", scope="ppi"),
        ]
        with transaction.atomic(), connection.cursor() as cursor:
            for query in queries:
                cursor.execute(query)

        self.stdout.write(
            "core_eventtype.scope_list & scope_sugg have been updated successfully."
        )
