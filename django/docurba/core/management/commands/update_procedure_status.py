import csv

from django.core.management.base import BaseCommand
from django.db import models

from docurba.core.models import Event, Procedure


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
        # distinct + order_by allows to keep only the most recent impactful event per procedure
        # https://docs.djangoproject.com/en/6.1/ref/models/querysets/#django.db.models.query.QuerySet.distinct
        # https://www.postgresql.org/docs/current/sql-select.html#SQL-DISTINCT
        events_qs = (
            Event.objects.filter_impactful()
            .order_by("procedure_id", "-date_evenement", "-created_at", "-from_sudocuh")
            .distinct("procedure_id")
        )
        queryset = Procedure.objects.filter(parente__isnull=True).prefetch_related(
            models.Prefetch("event_set", queryset=events_qs)
        )

        writer = csv.writer(self.stdout, lineterminator="\n")

        writer.writerow(
            [
                "procedure_id",
                "ancien_status",
                "nouveau_status",
            ]
        )

        procedures_to_update = []
        for procedure in queryset:
            status = procedure.compute_status()
            if procedure.status == status:
                continue

            writer.writerow(
                [
                    procedure.id,
                    procedure.status,
                    status,
                ]
            )

            if wet_run:
                procedure.status = status
                procedures_to_update.append(procedure)

        if procedures_to_update:
            Procedure.objects.bulk_update(
                procedures_to_update, ["status"], batch_size=1000
            )
