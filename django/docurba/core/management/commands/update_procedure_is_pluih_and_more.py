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
            help="Update procedure is_* denormalized fields.",
        )

    def handle(self, *args: list, **options: dict) -> None:  # noqa: ARG002
        logger = logging.getLogger(self.__class__.__module__)
        procedure_qs = Procedure.objects.prefetch_related("perimetre")

        # toutes les procédures qui ont un doc_type PLUiM, PLUiHM, PLUiMS doivent avoir is_pdu = true , sinon = false
        # is_pdu
        # In Nuxt it was alsways set to null.
        query = models.Q(
            doc_type__in=[TypeDocument.PLUIM, TypeDocument.PLUIHM, TypeDocument.PLUISM]
        )  # not PLUiSHM ?
        should_be_pdu = procedure_qs.filter(query & models.Q(vaut_PDM=False))
        should_not_be_pdu = procedure_qs.filter(~query & models.Q(vaut_PDM=True))
        logger.info("Should be PDU: %s", should_be_pdu.count())
        logger.info("Should not be PDU: %s", should_not_be_pdu.count())
        if options["wet_run"]:
            should_be_pdu.update(vaut_PDM=True)  # 9
            should_not_be_pdu.update(vaut_PDM=False)  # 27

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
            should_be_pluih.update(vaut_PLH=True)  # 12
            should_not_be_pluih.update(vaut_PLH=False)  # 11

        # is_scot
        # toutes les procédures qui ont doc_type = SD ou SCoT ont is_scot = true, sinon = false sauf pour l'historique Sudocuh *=*⚠️ is_scot peut être true même si doc_type ≠ SD ou SCoT si et uniquement si from sudocuh = oui ⚠️
        should_be_scot = procedure_qs.filter(
            models.Q(from_sudocuh__isnull=True)
            & models.Q(doc_type__in=["SD", "SCOT"])
            & models.Q(vaut_SCoT=False)
        )
        should_not_be_scot = procedure_qs.filter(
            models.Q(from_sudocuh__isnull=True)
            & ~models.Q(doc_type__in=["SD", "SCOT"])
            & models.Q(vaut_SCoT=True)
        )
        logger.info("Should be SCOT: %s", should_be_scot.count())
        logger.info("Should not be SCOT: %s", should_not_be_scot.count())
        if options["wet_run"]:
            should_be_scot.update(vaut_SCoT=True)  # 132
            should_not_be_scot.update(vaut_SCoT=False)  # 0

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
                    "Lien",
                    "Nom (dynamique)",
                    "Périmètre",
                    "Collectivité porteuse",
                    "Devrait être is_pdu",
                    "Ne devrait pas être is_pdu",
                    "Devrait être is_pluih",
                    "Ne devrait pas être is_pluih",
                    "Devrait être SCoT",
                    "Ne devrait pas être SCoT",
                ]
            )

            for procedure in should_be_pdu:
                writer.writerow(
                    [
                        procedure.id,
                        procedure.from_sudocuh,
                        procedure.doc_type,
                        procedure.get_absolute_url(),
                        procedure.computed_name,
                        list(procedure.perimetre.values_list("code_insee", flat=True)),
                        procedure.collectivite_porteuse.nom,
                        "True",
                        "False",
                        "False",
                        "False",
                        "False",
                        "False",
                    ]
                )
            for procedure in should_not_be_pdu:
                writer.writerow(
                    [
                        procedure.id,
                        procedure.from_sudocuh,
                        procedure.doc_type,
                        procedure.get_absolute_url(),
                        procedure.computed_name,
                        list(procedure.perimetre.values_list("code_insee", flat=True)),
                        procedure.collectivite_porteuse.nom,
                        "False",
                        "True",
                        "False",
                        "False",
                        "False",
                        "False",
                    ]
                )
            for procedure in should_be_pluih:
                writer.writerow(
                    [
                        procedure.id,
                        procedure.from_sudocuh,
                        procedure.doc_type,
                        procedure.get_absolute_url(),
                        procedure.computed_name,
                        list(procedure.perimetre.values_list("code_insee", flat=True)),
                        procedure.collectivite_porteuse.nom,
                        "False",
                        "False",
                        "True",
                        "False",
                        "False",
                        "False",
                    ]
                )
            for procedure in should_not_be_pluih:
                writer.writerow(
                    [
                        procedure.id,
                        procedure.from_sudocuh,
                        procedure.doc_type,
                        procedure.get_absolute_url(),
                        procedure.computed_name,
                        list(procedure.perimetre.values_list("code_insee", flat=True)),
                        procedure.collectivite_porteuse.nom,
                        "False",
                        "False",
                        "False",
                        "True",
                        "False",
                        "False",
                    ]
                )
            for procedure in should_be_scot:
                writer.writerow(
                    [
                        procedure.id,
                        procedure.from_sudocuh,
                        procedure.doc_type,
                        procedure.get_absolute_url(),
                        procedure.computed_name,
                        list(procedure.perimetre.values_list("code_insee", flat=True)),
                        procedure.collectivite_porteuse.nom,
                        "False",
                        "False",
                        "False",
                        "False",
                        "True",
                        "False",
                    ]
                )
            for procedure in should_not_be_scot:
                writer.writerow(
                    [
                        procedure.id,
                        procedure.from_sudocuh,
                        procedure.doc_type,
                        procedure.get_absolute_url(),
                        procedure.computed_name,
                        list(procedure.perimetre.values_list("code_insee", flat=True)),
                        procedure.collectivite_porteuse.nom,
                        "False",
                        "False",
                        "False",
                        "False",
                        "False",
                        "True",
                    ]
                )

        logger.info("Update is over!")
