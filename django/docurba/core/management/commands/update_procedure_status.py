import csv

from django.core.management.base import BaseCommand
from django.db import models
from django.utils import timezone

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
        date_pivot = timezone.now().date()
        events_qs = Event.objects.with_impact(date_pivot)
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
            computed_status = procedure.compute_status(date_pivot)
            computed_value = computed_status.value if computed_status else None
            if procedure.status == computed_value:
                continue

            writer.writerow(
                [
                    procedure.id,
                    procedure.status,
                    computed_value,
                ]
            )

            if wet_run:
                procedure.status = computed_value
                procedures_to_update.append(procedure)

        if procedures_to_update:
            Procedure.objects.bulk_update(
                procedures_to_update, ["status"], batch_size=1000
            )
