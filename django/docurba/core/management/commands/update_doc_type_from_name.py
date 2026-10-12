import logging

from django.core.management.base import BaseCommand, CommandParser
from django.db.models import Case, F, Value, When

from docurba.core.models import Procedure, TypeDocument


class Command(BaseCommand):
    def add_arguments(self, parser: CommandParser) -> None:
        super().add_arguments(parser)
        parser.add_argument(
            "--wet-run",
            action="store_true",
            default=False,
            help="Update Sudocuh's procedure.doc_type depending on procedure.name.",
        )

    def handle(self, *args: list, **options: dict) -> None:  # noqa: ARG002
        logger = logging.getLogger(self.__class__.__module__)
        qs = Procedure.objects.annotate(
            new_doc_type=Case(
                When(name__icontains="PLUiH ", then=Value(TypeDocument.PLUIH)),
                When(name__icontains="PLUiHM ", then=Value(TypeDocument.PLUIHM)),
                When(name__icontains="PLUiM ", then=Value(TypeDocument.PLUIM)),
                When(name__icontains="PLUiSM ", then=Value(TypeDocument.PLUISM)),
                When(name__icontains="PLUiSH ", then=Value(TypeDocument.PLUISH)),
                When(name__icontains="PLUiSHM ", then=Value(TypeDocument.PLUISHM)),
                default=F("doc_type"),
            )
        )
        qs = qs.exclude(doc_type=F("new_doc_type"))

        logger.info("Updating %s procedures", qs.count())
        for procedure in qs:
            logger.info(
                "ID: %s | doc_type: %s | name: %s | new_doc_type: %s",
                procedure.id,
                procedure.doc_type,
                procedure.name,
                procedure.new_doc_type,
            )

        if options["wet_run"]:
            qs.update(doc_type=F("new_doc_type"))

        logger.info("Update is over!")
