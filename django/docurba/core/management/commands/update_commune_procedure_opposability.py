import csv

from django.core.management.base import BaseCommand
from django.db import models

from docurba.core.models import Commune, CommuneProcedure, Event


class Command(BaseCommand):
    help = "Compare CommuneProcedure.opposable with the computed opposability and export the differences to CSV"

    def add_arguments(self, parser: str) -> None:
        parser.add_argument(
            "--wet-run",
            dest="wet_run",
            action="store_true",
            help="Update CommuneProcedure.opposable with the computed opposability",
        )

    def handle(self, *args: list, wet_run: bool, **options: dict) -> None:  # noqa: ARG002
        communes = (
            Commune.objects.filter(procedures_through__isnull=False)
            .distinct()
            .prefetch_related(
                models.Prefetch(
                    "procedures_through",
                    queryset=CommuneProcedure.objects.select_related(
                        "procedure"
                    ).prefetch_related(
                        models.Prefetch(
                            "procedure__event_set",
                            queryset=Event.objects.filter_impactful(),
                        )
                    ),
                ),
            )
        )

        writer = csv.writer(self.stdout, lineterminator="\n")
        writer.writerow(
            [
                "commune_procedure_id",
                "old_opposable",
                "new_opposable",
            ]
        )

        perimetre_lines_to_update = []
        for commune in communes:
            opposable_line_ids = {
                line.id for line in CommuneProcedure.get_opposables_for_commune(commune)
            }
            for perimetre_line in commune.procedures_through.all():
                opposable = perimetre_line.id in opposable_line_ids
                if perimetre_line.opposable == opposable:
                    continue

                writer.writerow(
                    [
                        perimetre_line.id,
                        perimetre_line.opposable,
                        opposable,
                    ]
                )

                if wet_run:
                    perimetre_line.opposable = opposable
                    perimetre_lines_to_update.append(perimetre_line)

        if perimetre_lines_to_update:
            CommuneProcedure.objects.bulk_update(
                perimetre_lines_to_update, ["opposable"], batch_size=1000
            )
