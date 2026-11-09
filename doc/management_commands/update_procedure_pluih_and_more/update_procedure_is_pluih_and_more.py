import contextlib
import csv
import io
import logging
from functools import partial
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandParser
from django.db import models
from docurba.core.enums import TypeDocument
from docurba.core.models import Procedure


class Command(BaseCommand):
    def add_arguments(self, parser: CommandParser) -> None:
        super().add_arguments(parser)
        parser.add_argument(
            "--wet-run",
            action="store_true",
            default=False,
            help="Clean procedure is_* fields.",
        )
        parser.add_argument(
            "--output",
            action="store",
            dest="output",
            type=str,
            choices=["stdout", "file"],
        )

    def _write_rows(self, writer: io.StringIO, procedures: list) -> None:
        writer.writerow(
            [
                "ID",
                "Sudocuh ID",
                "Type de document",
                "is_pdu",
                "is_pluih",
                "is_scot",
                "Lien",
                "Nom (dynamique)",
                "Collectivité porteuse",
                "Périmètre",
            ]
        )

        for procedure in sorted(procedures, key=lambda line: line.pk):
            writer.writerow(
                [
                    procedure.id,
                    procedure.from_sudocuh,
                    procedure.doc_type,
                    procedure.vaut_PDM,
                    procedure.vaut_PLH,
                    procedure.vaut_SCoT,
                    procedure.get_absolute_url(),
                    procedure.computed_name,
                    procedure.collectivite_porteuse.nom
                    if procedure.collectivite_porteuse
                    else "",
                    list(procedure.perimetre.values_list("code_insee", flat=True)),
                ]
            )

    def handle(self, *args: list, **options: dict) -> None:
        logger = logging.getLogger(self.__class__.__module__)
        procedure_qs = Procedure.objects.exclude(
            doc_type__in=[TypeDocument.POS, TypeDocument.PLU]
        ).prefetch_related("perimetre")
        to_be_updated_procedures = []

        # is_pdu
        # In Nuxt it was always set to null.
        query = models.Q(
            doc_type__in=[
                TypeDocument.PLUIM,
                TypeDocument.PLUIHM,
                TypeDocument.PLUISM,
                TypeDocument.PLUISHM,
            ]
        )
        should_be_pdu = procedure_qs.filter(query & models.Q(vaut_PDM=False))
        should_not_be_pdu = procedure_qs.filter(~query & models.Q(vaut_PDM=True))
        logger.info("Should be PDU: %s", should_be_pdu.count())
        logger.info("Should not be PDU: %s", should_not_be_pdu.count())

        if options["wet_run"]:
            should_be_pdu = should_be_pdu.update(vaut_PDM=True)  # 10
            should_not_be_pdu = should_not_be_pdu.update(vaut_PDM=False)
        else:
            for procedure in should_be_pdu:
                procedure.vaut_PDM = True
                to_be_updated_procedures.append(procedure)
            for procedure in should_not_be_pdu:
                procedure.vaut_PDM = False
                to_be_updated_procedures.append(procedure)

        # is_pluih
        # in Nuxt it was: is_pluih: this.typeDu === 'PLUiH'
        query = models.Q(
            doc_type__in=[
                TypeDocument.PLUIH,
                TypeDocument.PLUIHM,
                TypeDocument.PLUISH,
                TypeDocument.PLUISHM,
            ]
        )
        should_be_pluih = procedure_qs.filter(query & models.Q(vaut_PLH=False))
        should_not_be_pluih = procedure_qs.filter(~query & models.Q(vaut_PLH=True))
        logger.info("Should be PLH: %s", should_be_pluih.count())
        logger.info("Should not be PLH: %s", should_not_be_pluih.count())

        if options["wet_run"]:
            should_be_pluih = should_be_pluih.update(vaut_PLH=True)  # 17
            should_not_be_pluih = should_not_be_pluih.update(vaut_PLH=False)
        else:
            for procedure in should_be_pluih:
                procedure.vaut_PLH = True
                to_be_updated_procedures.append(procedure)
            for procedure in should_not_be_pluih:
                procedure.vaut_PLH = False
                to_be_updated_procedures.append(procedure)

        # is_scot
        should_be_scot = Procedure.objects.filter(
            models.Q(from_sudocuh__isnull=True)
            & models.Q(doc_type__in=["SD", "SCOT"])
            & models.Q(vaut_SCoT=False)
        ).prefetch_related("perimetre")
        should_not_be_scot = Procedure.objects.filter(
            models.Q(from_sudocuh__isnull=True)
            & ~models.Q(doc_type__in=["SD", "SCOT"])
            & models.Q(vaut_SCoT=True)
        ).prefetch_related("perimetre")
        logger.info("Should be SCOT: %s", should_be_scot.count())
        logger.info("Should not be SCOT: %s", should_not_be_scot.count())

        if options["wet_run"]:
            should_be_scot.update(vaut_SCoT=True)  # 146
            should_not_be_scot.update(vaut_SCoT=False)
        else:
            for procedure in should_be_scot:
                procedure.vaut_SCoT = True
                to_be_updated_procedures.append(procedure)
            for procedure in should_not_be_scot:
                procedure.vaut_SCoT = False
                to_be_updated_procedures.append(procedure)

        if options.get("output") == "file":
            export_file = (
                Path(settings.EXPORTS_DIR) / "update_procedure_is_pluih_and_more.csv"
            )
            logger.info("Exporting results to %s", export_file)
            context_method = partial(Path.open, export_file, "w")

        else:
            logger.info("Exporting results to stdout.")
            context_method = partial(contextlib.nullcontext)

        with (
            context_method() as file,
            contextlib.redirect_stdout(file or self.stdout) as f,
        ):
            writer = csv.writer(f, delimiter=";", lineterminator="\n")
            self._write_rows(writer=writer, procedures=to_be_updated_procedures)

        logger.info("Update is over!")
