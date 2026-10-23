import csv
import logging
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

    def handle(self, *args: list, **options: dict) -> None:  # noqa: ARG002, C901, PLR0912
        logger = logging.getLogger(self.__class__.__module__)
        procedure_qs = Procedure.objects.exclude(
            doc_type__in=[TypeDocument.POS, TypeDocument.PLU]
        ).prefetch_related("perimetre")
        to_be_updated_procedures = []

        # toutes les procédures qui ont un doc_type PLUiM, PLUiHM, PLUiMS, PLUISHM doivent avoir is_pdu = true , sinon = false
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

        # toutes les procédures qui ont un doc_type PLUiH, PLUiHM, PLUiSH, PLUiSHM ont is_pluih = true, sinon false
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
        # toutes les procédures qui ont doc_type = SD ou SCoT ont is_scot = true, sinon = false sauf pour l'historique Sudocuh *=*⚠️ is_scot peut être true même si doc_type ≠ SD ou SCoT si et uniquement si from sudocuh = oui ⚠️
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

        export_file = (
            Path(settings.EXPORTS_DIR) / "update_procedure_is_pluih_and_more.csv"
        )
        logger.info("Exporting results to %s", export_file)
        with Path.open(export_file, "w") as file:
            writer = csv.writer(file, delimiter=";", lineterminator="\n")

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

            for procedure in sorted(to_be_updated_procedures, key=lambda line: line.pk):
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

        logger.info("Update is over!")
