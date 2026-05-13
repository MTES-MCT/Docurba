from typing import Any

from django.core.management.base import BaseCommand
from django.db.models import Exists, OuterRef

from docurba.core.constants import HUWART_LAW_DATE
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
                has_start_event_after_huwart_law=Exists(
                    Event.objects.filter(
                        procedure_id=OuterRef("pk"),
                        type__in=[
                            "Arrêté de lancement de la procédure",
                            "Délibération de prescription du conseil municipal ou communautaire",
                            "Délibération de l'établissement public qui prescrit",
                        ],
                        date_evenement__gte=HUWART_LAW_DATE,
                    )
                ),
            )
            .exclude(has_start_event_after_huwart_law=True)
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
