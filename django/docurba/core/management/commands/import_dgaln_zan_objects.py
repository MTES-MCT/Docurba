import csv
import pathlib
from typing import Any

from django.conf import settings
from django.core.management.base import BaseCommand

from docurba.core.models import Procedure, ProcedureTopic, Topic


def write_to_file(filename: str, data: list) -> None:
    log_file = pathlib.Path(settings.EXPORTS_DIR) / filename
    with log_file.open("w+") as file:
        writer = csv.writer(
            file,
            delimiter=";",
        )
        for pk in data:
            writer.writerow([pk])


class Command(BaseCommand):
    help = "Add ZAN object for procedures in a given file."

    def add_arguments(self, parser: str) -> None:
        parser.add_argument("--wet-run", dest="wet_run", action="store_true")
        parser.add_argument("--import-filename", type=str, dest="import_filename")

    def handle(
        self,
        *,
        wet_run: bool,
        import_filename: str,
        **options: dict[str, Any],  # noqa: ARG002
    ) -> None:
        import_filename = pathlib.Path(settings.EXPORTS_DIR) / import_filename
        zan_topic_id = Topic.objects.get(name="zan").pk

        zan_procedures = ProcedureTopic.objects.filter(topic_id=zan_topic_id)
        self.stdout.write(
            f"Docurba procedures tagged with ZAN: {zan_procedures.count()}"
        )
        write_to_file(
            "docurba_zan_procedures_debut.csv",
            zan_procedures.values_list("procedure_id", flat=True),
        )

        with pathlib.Path.open(import_filename) as file:
            data = csv.reader(file, delimiter=",")
            next(data)
            procedure_uuids_to_be_updated = [row[0] for row in data]
        self.stdout.write(
            f"Procedures tagged as ZAN in the last survey: {len(procedure_uuids_to_be_updated)}"
        )

        found_procedures_qs = Procedure.objects.filter(
            pk__in=procedure_uuids_to_be_updated
        ).only(
            "pk",
        )
        self.stdout.write(
            f"Procedures in database to update: {found_procedures_qs.count()}"
        )

        # Transform UUID in string to compare it to data from file.
        pks = [str(pk) for pk in found_procedures_qs.values_list("pk", flat=True)]
        not_found_procedures = [
            pk for pk in procedure_uuids_to_be_updated if pk not in pks
        ]
        write_to_file("not_found_procedures.csv", not_found_procedures)
        self.stdout.write(f"Not found procedures: {len(not_found_procedures)}")

        tagged_zan_procedures_qs = (
            Procedure.objects.filter(
                topics_through__topic_id=zan_topic_id,
                pk__in=procedure_uuids_to_be_updated,
            )
            .only("pk")
            .select_related("topics_through")
        )
        already_zan_pks = [
            str(pk) for pk in tagged_zan_procedures_qs.values_list("pk", flat=True)
        ]
        self.stdout.write(f"Already ZAN: {len(already_zan_pks)}")
        if already_zan_pks:
            write_to_file("already_zan.csv", already_zan_pks)

        # Filter not found and already tagged procedures.
        exclusions = not_found_procedures + already_zan_pks
        to_be_updated_ids = [
            pk for pk in procedure_uuids_to_be_updated if pk not in exclusions
        ]
        self.stdout.write(f"To be updated: {len(to_be_updated_ids)}")

        procedure_topics_to_create = {
            ProcedureTopic(procedure_id=pk, topic_id=zan_topic_id)
            for pk in to_be_updated_ids
        }

        write_to_file("updated_procedures.csv", to_be_updated_ids)
        if wet_run:
            ProcedureTopic.objects.bulk_create(
                procedure_topics_to_create, batch_size=1000
            )
