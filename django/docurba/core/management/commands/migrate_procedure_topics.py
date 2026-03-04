import csv
import pathlib
import re
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
            topic["display_name"]: topic["pk"]
            for topic in Topic.objects.values("pk", "display_name")
        }

        if limit:
            procedures_qs = procedures_qs[:limit]
        self.stdout.write(f"Results to process: {procedures_qs.count()}")

        procedures_topics_to_create = []
        procedures_to_update = []
        csv_output = []

        for procedure in procedures_qs.iterator(1000):
            former_commentaire = procedure.commentaire
            other_comment = ""
            other_comment_search = re.search(r"Autre - (.*$)", former_commentaire)
            comment_without_other = re.sub(r"Autre - .*$", "", former_commentaire)
            comment_without_other = re.sub(r", $", "", comment_without_other)
            topics = []
            has_error = False

            if other_comment_search:
                other_comment = other_comment_search.groups()[0].strip()

            if comment_without_other:
                # ", " is the way topics are concatenated today.
                # See https://github.com/MTES-MCT/Docurba/blob/987459223d4d4e046d55d4800f8245bb5ca6b6e7/nuxt/components/Procedures/InsertForm.vue#L363
                comment_without_other_topics = comment_without_other.split(", ")
                try:
                    [
                        topics_id_per_name[topic]
                        for topic in comment_without_other_topics
                    ]
                except KeyError as err:
                    self.stderr.write(f"{err} - procedure ID {procedure.id})")
                    has_error = True
                    continue

            if has_error:
                continue

            if other_comment:
                procedures_topics_to_create.append(
                    ProcedureTopic(
                        procedure_id=procedure.id,
                        topic_id=topics_id_per_name["Autre"],
                        comment=other_comment,
                    )
                )
                topics += [
                    "Autre",
                ]

            if comment_without_other:
                procedures_topics_to_create.extend(
                    [
                        ProcedureTopic(
                            procedure_id=procedure.id,
                            topic_id=topics_id_per_name[topic],
                        )
                        for topic in comment_without_other_topics
                    ]
                )
                topics.extend(comment_without_other_topics)

            procedure.commentaire = ""
            procedures_to_update.append(procedure)

            csv_output.append(
                {
                    "ancien_commentaire": former_commentaire,
                    "nouveau_commentaire": procedure.commentaire,
                    "objet_commentaire": other_comment,
                    "procedure_id": str(procedure.pk),
                    "objet_autre": "Autre" in topics,
                    "objet_enr": "Zones d'accélération ENR" in topics,
                    "objet_zan": "Trajectoire ZAN" in topics,
                    "objet_feu_de_foret": "Feu de forêt" in topics,
                    "objet_trait_de_cote": "Trait de côte" in topics,
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
                fieldnames=csv_output[0].keys(),
                delimiter=";",
            )
            writer.writeheader()
            writer.writerows(csv_output)

        self.stdout.write(
            f"Added procedures topics: {len(procedures_topics_to_create)}"
        )
        self.stdout.write(f"Updated procedures: {len(procedures_to_update)}")
        self.stdout.write(f"Result in: {filename}")
