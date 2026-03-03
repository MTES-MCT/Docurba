import csv
import pathlib
from typing import Any

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db.models import Q

from docurba.core.models import Procedure


class Command(BaseCommand):
    help = "Move Sudocuh Procedure.commentaire to Procedure.comment_from_sudocuh"

    def add_arguments(self, parser: str) -> None:
        parser.add_argument("--wet-run", dest="wet_run", action="store_true")
        parser.add_argument("--limit", type=int, dest="limit")

    def handle(self, *, wet_run: bool, limit: int, **options: dict[str, Any]) -> None:  # noqa: ARG002
        filename = pathlib.Path(settings.EXPORTS_DIR) / "sudocuh_comments.csv"
        procedures_qs = (
            Procedure.objects.filter(Q(from_sudocuh__isnull=False))
            .exclude(Q(commentaire__isnull=True) | Q(commentaire=""))
            .only(
                "pk",
                "commentaire",
                "comment_from_sudocuh",
                "from_sudocuh",
                "collectivite_porteuse",  # Mandatory because of procedureManager.get_queryset
            )
        )
        if limit:
            procedures_qs = procedures_qs[:limit]
        self.stdout.write(f"Results to process: {procedures_qs.count()}")

        procedures_to_update = []
        procedures_to_update_as_dict = []

        for procedure in procedures_qs.iterator(1000):
            former_commentaire = procedure.commentaire
            procedure.comment_from_sudocuh = procedure.commentaire
            procedure.commentaire = ""
            procedures_to_update.append(procedure)
            procedures_to_update_as_dict.append(
                {
                    "ancien_commentaire": former_commentaire,
                    "nouveau_commentaire_sudocuh": procedure.comment_from_sudocuh,
                    "nouveau_commentaire": procedure.commentaire,
                    "from_sudocuh_id": procedure.from_sudocuh,
                }
            )

        if wet_run:
            Procedure.objects.bulk_update(
                procedures_to_update,
                batch_size=1000,
                fields=["commentaire", "comment_from_sudocuh"],
            )

        with filename.open(mode="w+", newline="") as file:
            writer = csv.DictWriter(
                file,
                fieldnames=procedures_to_update_as_dict[0].keys(),
                delimiter=";",
            )
            writer.writeheader()
            writer.writerows(procedures_to_update_as_dict)

        self.stdout.write(f"Updated procedures: {len(procedures_to_update)}")
        self.stdout.write(f"Result in: {filename}")
