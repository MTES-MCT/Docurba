import csv

from django.core.management.base import BaseCommand

from docurba.core.models import Procedure


class Command(BaseCommand):
    help = "Export secondary procedures with a non-null status and optionally reset it to null"

    def add_arguments(self, parser: str) -> None:
        parser.add_argument(
            "--wet-run",
            dest="wet_run",
            action="store_true",
            help="Set procedures.status to null",
        )

    def handle(self, *args: list, wet_run: bool, **options: dict) -> None:  # noqa: ARG002
        queryset = Procedure.objects.filter(parente__isnull=False).exclude(
            status__isnull=True
        )

        writer = csv.writer(self.stdout, lineterminator="\n")

        writer.writerow(
            [
                "procedure_id",
                "procedure.status",
            ]
        )

        for procedure in queryset:
            writer.writerow(
                [
                    procedure.id,
                    procedure.status,
                ]
            )

            if wet_run:
                procedure.status = None
                procedure.save()
