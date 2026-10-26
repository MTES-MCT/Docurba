import csv

from django.core.management.base import BaseCommand
from django.db.models import Exists, OuterRef

from docurba.core.models import Collectivite, Procedure


class Command(BaseCommand):
    help = """
        List procedures for which no collectivite porteuse exists
    """

    def handle(self, *args: list, **options: dict) -> None:  # noqa: ARG002
        collectivites = Collectivite.objects.filter(
            code_insee_unique=OuterRef("collectivite_porteuse_id"),
        )
        procedures = Procedure.objects.filter(~Exists(collectivites)).order_by(
            "collectivite_porteuse_id"
        )

        writer = csv.writer(self.stdout, lineterminator="\n")

        writer.writerow(["procedure.collectivite_porteuse_id", "procedure_id"])
        for procedure in procedures.iterator():
            writer.writerow([procedure.collectivite_porteuse_id, procedure.id])
