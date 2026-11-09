import csv
import logging
from itertools import batched
from math import ceil

from django.core.management.base import BaseCommand, CommandParser
from django.db import transaction

from docurba.core.models import Procedure

BATCH_SIZE = 2000


class Command(BaseCommand):
    def add_arguments(self, parser: CommandParser) -> None:
        super().add_arguments(parser)
        parser.add_argument(
            "--mode",
            action="store",
            dest="mode",
            type=str,
            choices=["check", "update"],
            default="check",
        )

    def handle(self, mode: str, *args: list, **options: dict) -> None:  # noqa: ARG002
        logger = logging.getLogger(self.__class__.__module__)
        procedure_normalized_and_denormalized_fields = [
            field
            for items in Procedure.DYNAMIC_TO_DENORMALIZED_FIELDS.items()
            for field in items
        ]
        writer = csv.DictWriter(
            self.stdout,
            fieldnames=["procedure_id", *procedure_normalized_and_denormalized_fields],
            lineterminator="\n",
        )
        writer.writeheader()

        total_inconsistent_procedures_count = 0
        # 389 Docurba: des erreurs de i et l'ajout du S.
        # 25 Sudocuh: PLUH or PLUHM
        # Ignore sudocuh procedures until Octavie comes back.
        procedures_pks = Procedure.objects.values_list("pk", flat=True)

        batches = ceil(len(procedures_pks) / BATCH_SIZE)
        for i, batch_pks in enumerate(
            batched(procedures_pks, BATCH_SIZE, strict=False), 1
        ):
            logger.info("Checking up to %d procedures (%d/%d).", BATCH_SIZE, i, batches)
            qs = (
                Procedure.objects.filter(pk__in=batch_pks)
                .prefetch_related("perimetre")
                .select_related("collectivite_porteuse")
            )
            inconsistent_procedures = [
                procedure
                for procedure in qs
                if procedure.has_inconsistent_denormalized_fields()
            ]
            total_inconsistent_procedures_count += len(inconsistent_procedures)
            for procedure in inconsistent_procedures:
                writer.writerow(
                    {
                        "procedure_id": procedure.pk,
                        **{
                            field: getattr(procedure, field)
                            for field in procedure_normalized_and_denormalized_fields
                        },
                    }
                )

            if mode == "update":
                procedures = [
                    procedure.update_denormalized_fields(save=False)
                    for procedure in inconsistent_procedures
                ]
                with transaction.atomic():
                    Procedure.objects.bulk_update(
                        procedures,
                        fields=Procedure.DYNAMIC_TO_DENORMALIZED_FIELDS.values(),
                    )

        logger.info("%s inconsistent procedures", total_inconsistent_procedures_count)
