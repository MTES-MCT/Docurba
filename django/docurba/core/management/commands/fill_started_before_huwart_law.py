from typing import Any

from django.core.management.base import BaseCommand
from django.db.models import Exists, OuterRef, Q

from docurba.core.constants import HUWART_LAW_DATE
from docurba.core.enums import ProcedureType
from docurba.core.models import Event, Procedure


class Command(BaseCommand):
    help = "Update the procedures.started_before_loi_huwart column."

    def add_arguments(self, parser: str) -> None:
        parser.add_argument("--wet-run", dest="wet_run", action="store_true")
        parser.add_argument("--limit", type=int, dest="limit")

    def handle(self, *, wet_run: bool, limit: int, **options: dict[str, Any]) -> None:  # noqa: ARG002
        procedures_qs = (
            Procedure.objects.annotate(
                # PLU and POS only.
                # There are 2080 different event types currently in production.
                has_start_event=Exists(
                    Event.objects.filter(
                        procedure_id=OuterRef("pk"),
                        type__in=[
                            "Arrêté de lancement de la procédure",
                            "Délibération de prescription du conseil municipal ou communautaire",
                        ],
                        date_evenement__lt=HUWART_LAW_DATE,
                    )
                )
            )
            .filter(
                Q(
                    type__in=[
                        ProcedureType.MODIFICATION,
                        ProcedureType.MODIFICATION_SIMPLIFIEE,
                        ProcedureType.REVISION_MS_RA,
                        ProcedureType.REVISION_ALLEGEE,
                        ProcedureType.REVISION_SIMPLIFIEE,
                    ],
                    has_start_event=True,
                    from_sudocuh__isnull=True,
                )
                | Q(from_sudocuh__isnull=False)
            )
            .only(
                "started_before_huwart_law",
            )
        )
        if limit:
            procedures_qs = procedures_qs[:limit]
        self.stdout.write(f"Results to process: {procedures_qs.count()}")

        updated_procedures = 0
        if wet_run:
            updated_procedures = procedures_qs.update(
                started_before_huwart_law=True,
            )

        self.stdout.write(f"Updated procedures: {updated_procedures}")
