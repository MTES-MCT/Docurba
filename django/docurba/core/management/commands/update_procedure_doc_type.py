from typing import Any

from django.core.management.base import BaseCommand
from django.db.models import Case, Count, F, IntegerField, OuterRef, Q, Subquery, When
from django.db.models.functions import Coalesce

from docurba.core.enums import CommuneType, TypeCollectivite
from docurba.core.models import (
    CommuneProcedure,
    Procedure,
    TypeDocument,
)


class Command(BaseCommand):
    help = "Move Sudocuh Procedure.commentaire to Procedure.comment_from_sudocuh"

    def add_arguments(self, parser: str) -> None:
        parser.add_argument("--wet-run", dest="wet_run", action="store_true")
        parser.add_argument("--limit", type=int, dest="limit")

    def handle(self, *, wet_run: bool, limit: int, **options: dict[str, Any]) -> None:  # noqa: ARG002
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

        is_sectoriel = Case(
            When(
                Q(area_communes__count__lt=F("communes_adherentes__count")),
                then=True,
            ),
            # area_communes > communes_adherentes: 34 procedures.
            # area_communes == communes_adherentes: 4103 procedures.
            When(
                Q(area_communes__count__gte=F("communes_adherentes__count")),
                then=False,
            ),
        )
        procedures_qs = (
            Procedure.objects.annotate(area_communes__count=Coalesce(sub_query, 0))
            .with_communes_counts()  # should be with_communes_adherentes__count
            .annotate(is_sectoriel=is_sectoriel)
            .select_related("collectivite_porteuse")
            .annotate(
                collectivite_porteuse_is_epci=Q(
                    collectivite_porteuse__type__in=TypeCollectivite.epci().keys()
                )
            )
            .filter(area_communes__count__gt=1)
        )

        self.stdout.write(f"Raw results to process: {procedures_qs.count()}")

        skipped_procedures_pk = procedures_qs.filter(
            collectivite_porteuse_is_epci=False
        ).values_list("pk", flat=True)
        for pk in skipped_procedures_pk:
            self.stdout.write(f"{pk} is not managed by an EPCI. Skipping.")

        procedures_qs = procedures_qs.filter(collectivite_porteuse_is_epci=True)
        procedures_qs_sectoriel = procedures_qs.filter(is_sectoriel=True)
        procedures_qs_not_sectoriel = procedures_qs.filter(is_sectoriel=False)

        self.stdout.write(
            f"Procedures 'sectorielles' to be updated: {procedures_qs_sectoriel.count()}"
        )
        self.stdout.write(
            f"Procedures not 'sectorielles' to be updated: {procedures_qs_not_sectoriel.count()}"
        )

        updated_sectoriel_counter = 0
        updated_not_sectoriel_counter = 0
        if wet_run:
            updated_sectoriel_counter = procedures_qs_sectoriel.update(
                doc_type=TypeDocument.PLUIS
            )
            updated_not_sectoriel_counter = procedures_qs_not_sectoriel.update(
                doc_type=TypeDocument.PLUI
            )

        self.stdout.write(
            f"Updated procedures 'sectorielles': {updated_sectoriel_counter}"
        )
        self.stdout.write(
            f"Updated procedures not 'sectorielles': {updated_not_sectoriel_counter}"
        )
