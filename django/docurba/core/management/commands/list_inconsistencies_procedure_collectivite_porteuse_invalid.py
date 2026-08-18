import csv

from django.core.management.base import BaseCommand
from django.db.models import Count, F, Max, OuterRef, Subquery

from docurba.core.enums import CommuneType
from docurba.core.models import CommuneProcedure, Procedure


class Command(BaseCommand):
    help = """
        List procedures for which the collectivite porteuse is invalid :
        - The collectivite porteuse of a procedure should be the commune when the perimeter of the procedure contains only this commune
    """

    def add_arguments(self, parser: str) -> None:
        parser.add_argument(
            "--wet-run",
            dest="wet_run",
            action="store_true",
            help="Update procedures by setting collectivite_porteuse_id to procedures_perimetres.collectivite_code",
        )

    def handle(self, *args: list, wet_run: bool, **options: dict) -> None:  # noqa: ARG002
        perimetres = (
            CommuneProcedure.objects.filter(
                collectivite_type=CommuneType.COM, procedure_id=OuterRef("id")
            )
            .values("procedure_id")
            .annotate(perimetre_count=Count("collectivite_code"))
            .filter(perimetre_count=1)
            .annotate(perimetre_code=Max("collectivite_code"))
            .values("perimetre_code")
        )

        procedures = (
            Procedure.objects.annotate(perimetre_code=Subquery(perimetres))
            .filter(perimetre_code__isnull=False)
            .exclude(perimetre_code=F("collectivite_porteuse_id"))
            .values("id", "collectivite_porteuse_id", "perimetre_code")
            .order_by("id")
        )

        writer = csv.writer(self.stdout, lineterminator="\n")

        writer.writerow(
            [
                "procedure_id",
                "procedure.collectivite_porteuse_id",
                "perimetre.collectivite_code",
            ]
        )
        for procedure in procedures.iterator():
            writer.writerow(
                [
                    procedure["id"],
                    procedure["collectivite_porteuse_id"],
                    procedure["perimetre_code"],
                ]
            )

        if wet_run:
            procedures.update(collectivite_porteuse_id=F("perimetre_code"))
