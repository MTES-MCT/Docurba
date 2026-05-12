import csv
import pathlib
from typing import Any

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db.models import Count, IntegerField, OuterRef, Q, Subquery
from django.db.models.functions import Coalesce

from docurba.core.enums import CommuneType, TypeCollectivite
from docurba.core.models import (
    CommuneProcedure,
    Procedure,
    TypeDocument,
)


class Command(BaseCommand):
    help = "Update procedure.doc_type when it should be a PLUI"

    def add_arguments(self, parser: str) -> None:
        parser.add_argument("--wet-run", dest="wet_run", action="store_true")
        parser.add_argument("--limit", type=int, dest="limit")

    def handle(self, *, wet_run: bool, limit: int, **options: dict[str, Any]) -> None:  # noqa: ARG002
        filename = pathlib.Path(settings.EXPORTS_DIR) / "from_plu_to_plui.csv"
        sub_query = Subquery(
            (
                CommuneProcedure.objects.filter(
                    commune__type=CommuneType.COM, procedure_id=OuterRef("id")
                )
                .values("procedure_id")
                .annotate(count=Count("pk"))
                .values("count")
            ),
            output_field=IntegerField(),
        )

        procedures_qs = (
            Procedure.objects.annotate(area_communes__count=Coalesce(sub_query, 0))
            .filter(doc_type="PLU")
            .select_related("collectivite_porteuse")
            .annotate(
                collectivite_porteuse_is_epci=Q(collectivite_porteuse__id__isnull=False)
                & Q(collectivite_porteuse__type__in=TypeCollectivite.epci().keys())
            )
            .filter(area_communes__count__gt=1)
        )

        self.stdout.write(f"Raw results to process: {procedures_qs.count()}")

        skipped_procedures_pk = procedures_qs.filter(
            collectivite_porteuse_is_epci=False, soft_delete=True
        ).values_list("pk", flat=True)
        for pk in skipped_procedures_pk:
            self.stdout.write(
                f"{pk} is not managed by an EPCI and is archived. Skipping."
            )

        procedures_qs = procedures_qs.filter(
            Q(collectivite_porteuse_is_epci=True)
            | Q(collectivite_porteuse_is_epci=False, soft_delete=False)
        )

        self.stdout.write(f"Procedures to be updated: {procedures_qs.count()}")

        procedures_to_update = []
        for procedure in procedures_qs.iterator(1000):
            procedure.doc_type = TypeDocument.PLUI
            procedure.previous_name = procedure.name
            if procedure.name:
                procedure.name = procedure.name.replace(" PLU ", " PLUi ")
            procedures_to_update.append(procedure)

        updated_counter = 0
        if wet_run:
            updated_counter = Procedure.objects.bulk_update(
                procedures_to_update, fields=["name", "doc_type"], batch_size=1000
            )

        with filename.open(mode="w+", newline="") as file:
            writer = csv.DictWriter(
                file,
                fieldnames=["id", "doc_type", "nom_avant", "nom_apres"],
                delimiter=";",
            )
            writer.writeheader()
            writer.writerows(
                [
                    {
                        "id": procedure.id,
                        "doc_type": procedure.doc_type,
                        "nom_avant": procedure.previous_name,
                        "nom_apres": procedure.name,
                    }
                    for procedure in procedures_to_update
                ]
            )
            writer.writerows(
                [
                    {"id": procedure, "doc_type": "PLU"}
                    for procedure in skipped_procedures_pk
                ]
            )

        self.stdout.write(f"Updated procedures: {updated_counter}")
