import csv
import logging
from itertools import batched
from math import ceil

from django.core.management.base import BaseCommand, CommandParser
from django.db import transaction
from docurba.core.models import Procedure

# si intercommunal ET is_pdu = false ET is_pluih = true alors doc_type = PLUiH
# si intercommunal ET is_pdu = true ET is_pluih = true alors doc_type = PLUiHM
# si intercommunal ET is_pdu = true ET is_pluih = false alors doc_type = PLUiM
# si intercommunal ET is_sectoriel ET is_pdu = true ET is_pluih = false alors doc_type = PLUiSM
# si intercommunal ET is_sectoriel ET is_pdu = false ET is_pluih = true alors doc_type = PLUiSH
# si intercommunal ET is_sectoriel ET is_pluih = true ET is_pdu = true alors doc_type = PLUiSHM

BATCH_SIZE = 200


class Command(BaseCommand):
    def add_arguments(self, parser: CommandParser) -> None:
        super().add_arguments(parser)
        parser.add_argument(
            "--wet-run",
            action="store_true",
            default=False,
            help="Update Sudocuh's procedure.doc_type.",
        )

    def handle(self, *args: list, **options: dict) -> None:
        logger = logging.getLogger(self.__class__.__module__)
        # .with_perimetre_without_deleguees_count() and .with_collectivite_porteuse_communes_adherentes_count()
        # are already called on Procedure.objets.get_queryset()
        procedures_to_update_pks = Procedure.objects.exclude(
            from_sudocuh__isnull=True
        ).values_list("pk", flat=True)
        logger.info("Updating %s procedures", len(procedures_to_update_pks))
        updated_procedures_pks = []
        batches = ceil(len(procedures_to_update_pks) / BATCH_SIZE)
        for i, batch_pks in enumerate(
            batched(procedures_to_update_pks, BATCH_SIZE, strict=False), 1
        ):
            logger.info("Updating up to %d procedures (%d/%d).", BATCH_SIZE, i, batches)
            procedures_to_update = []
            qs = Procedure.objects.filter(pk__in=batch_pks)
            for procedure in qs:
                new_doc_type = procedure.type_document
                if procedure.doc_type != new_doc_type:
                    procedure.doc_type = new_doc_type
                    procedures_to_update.append(procedure)
                    updated_procedures_pks.append(procedure.pk)

            if options["wet_run"]:
                with transaction.atomic():
                    Procedure.objects.bulk_update(
                        procedures_to_update, fields=["doc_type"], batch_size=200
                    )
        writer = csv.writer(self.stdout, lineterminator="\n")
        writer.writerow(["procedure_id"])
        for procedure_pk in updated_procedures_pks:
            writer.writerow([procedure_pk])

        logger.info("%s procedures were updated", len(updated_procedures_pks))
        logger.info("Update is over!")
