import csv
import pathlib
import re
from itertools import batched
from typing import Any

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db.models import Q

from docurba.core.models import Procedure, ProcedureTopic, Topic


class Command(BaseCommand):
    help = "Move Sudocuh Procedure.commentaire to Procedure.comment_from_sudocuh"

    def add_arguments(self, parser: str) -> None:
        parser.add_argument("--wet-run", dest="wet_run", action="store_true")
        parser.add_argument("--limit", type=int, dest="limit")

    def handle(self, *, wet_run: bool, limit: int, **options: dict[str, Any]) -> None:  # noqa: ARG002
        filename = pathlib.Path(settings.EXPORTS_DIR) / "updated_procedure_topics.csv"
        procedures_qs = (
            Procedure.objects.filter(Q(from_sudocuh__isnull=True))
            .exclude(Q(commentaire__isnull=True) | Q(commentaire=""))
            .only(
                "pk",
                "commentaire",
                "from_sudocuh",
                "collectivite_porteuse",  # Mandatory because of procedureManager.get_queryset
            )
        )
        topics_id_per_name = {
            topic["name"]: topic["pk"] for topic in Topic.objects.values("pk", "name")
        }

        if limit:
            procedures_qs = procedures_qs[:limit]
        self.stdout.write(f"Results to process: {procedures_qs.count()}")

        procedures_topics_to_create = []
        procedures_to_update = []
        procedures_to_update_as_dict = []

        for procedure in procedures_qs.iterator(1000):
            has_other_topic = False
            has_enr_topic = False
            has_zan_topic = False
            has_forest_fire_topic = False
            has_coastline_topic = False

            former_commentaire = procedure.commentaire
            commentaire = procedure.commentaire
            # other_comment = re.search(r"Autre - (.*$)", commentaire)
            # comment_without_other = re.sub(r"Autre -.*$", "", commentaire)
            comment_without_other = procedure.commentaire

            topics = comment_without_other.split(",")
            for topic in topics:
                match topic:
                    case "Trajectoire ZAN":
                        has_zan_topic = True
                        procedures_topics_to_create.append(
                            ProcedureTopic(
                                procedure_id=procedure.id,
                                topics_id=topics_id_per_name[
                                    "zan"
                                ],  # TODO(cms): update to topic_id
                            )
                        )

            # procedure.comment_from_sudocuh = procedure.commentaire
            procedure.commentaire = ""
            # assert row["objet_trait_de_cote"] == "False"

            procedures_to_update.append(procedure)
            procedures_to_update_as_dict.append(
                {
                    "ancien_commentaire": former_commentaire,
                    "nouveau_commentaire": procedure.commentaire,
                    "procedure_id": str(procedure.pk),
                    "objet_autre": has_other_topic,
                    "objet_enr": has_enr_topic,
                    "objet_zan": has_zan_topic,
                    "objet_feu_foret": has_forest_fire_topic,
                    "objet_trait_de_cote": has_coastline_topic,
                }
            )

        if wet_run:
            ProcedureTopic.objects.bulk_create(
                procedures_topics_to_create, batch_size=1000
            )
            Procedure.objects.bulk_update(
                procedures_to_update,
                fields=["commentaire"],
                batch_size=1000,
            )

        with filename.open(mode="w+", newline="") as file:
            writer = csv.DictWriter(
                file,
                fieldnames=procedures_to_update_as_dict[0].keys(),
                delimiter=";",
            )
            writer.writeheader()
            writer.writerows(procedures_to_update_as_dict)

        self.stdout.write(f"Updated procedures: {len(procedures_topics_to_create)}")
        self.stdout.write(f"Result in: {filename}")
