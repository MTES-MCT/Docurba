import logging

from django.core.management.base import BaseCommand, CommandParser

from docurba.core.models import Procedure

# si intercommunal ET is_pdu = false ET is_pluih = true alors doc_type = PLUiH
# si intercommunal ET is_pdu = true ET is_pluih = true alors doc_type = PLUiHM
# si intercommunal ET is_pdu = true ET is_pluih = false alors doc_type = PLUiM
# si intercommunal ET is_sectoriel ET is_pdu = true ET is_pluih = false alors doc_type = PLUiSM
# si intercommunal ET is_sectoriel ET is_pdu = false ET is_pluih = true alors doc_type = PLUiSH
# si intercommunal ET is_sectoriel ET is_pluih = true ET is_pdu = true alors doc_type = PLUiSHM


class Command(BaseCommand):
    def add_arguments(self, parser: CommandParser) -> None:
        super().add_arguments(parser)
        parser.add_argument(
            "--wet-run",
            action="store_true",
            default=False,
            help="Update Sudocuh's procedure.doc_type.",
        )

    def handle(self, *args: list, **options: dict) -> None:  # noqa: ARG002
        logger = logging.getLogger(self.__class__.__module__)
        # .with_perimetre_without_deleguees_count() and .with_collectivite_porteuse_communes_adherentes_count()
        # are already called on Procedure.objets.get_queryset()
        qs = Procedure.objects.exclude(from_sudocuh__isnull=True)
        procedures_to_update = []

        logger.info("Updating %s procedures", qs.count())
        for procedure in qs:
            new_doc_type = procedure.type_document
            if procedure.doc_type != new_doc_type:
                procedure.doc_type = new_doc_type
                procedures_to_update.append(procedure)

        logger.info("Total procedures: %s", qs.count())
        logger.info("Procedures to update: %s", len(procedures_to_update))

        if options["wet_run"]:
            Procedure.objects.bulk_update(
                procedures_to_update, fields=["doc_type"], batch_size=200
            )

        logger.info("Update is over!")
