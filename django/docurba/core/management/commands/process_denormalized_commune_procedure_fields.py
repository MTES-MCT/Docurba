import csv
import logging
from datetime import timedelta
from itertools import batched
from math import ceil

from django.conf import settings
from django.core.management.base import BaseCommand, CommandParser
from django.db import models, transaction
from django.utils import timezone

from docurba.core.models import CommuneProcedure
from docurba.utils.slack import send_slack_message

BATCH_SIZE = 2000


class Command(BaseCommand):
    def add_arguments(self, parser: CommandParser) -> None:
        super().add_arguments(parser)
        parser.add_argument(
            "--mode",
            action="store",
            dest="mode",
            type=str,
            choices=["check", "update"],
            default="check",
        )
        parser.add_argument(
            "--tell-slack", dest="tell_slack", action="store_true", default=False
        )
        parser.add_argument(
            "--yesterday-only",
            dest="yesterday_only",
            action="store_true",
            default=False,
        )

    def handle(
        self,
        mode: str,
        tell_slack: bool = False,  # noqa: FBT001, FBT002
        yesterday_only: bool = False,  # noqa: FBT001, FBT002
        *args: list,  # noqa: ARG002
        **options: dict,  # noqa: ARG002
    ) -> None:
        logger = logging.getLogger(self.__class__.__module__)
        commune_procedure_normalized_and_denormalized_fields = [
            field
            for items in CommuneProcedure.DYNAMIC_TO_DENORMALIZED_FIELDS.items()
            for field in items
        ]
        writer = csv.DictWriter(
            self.stdout,
            delimiter=";",
            fieldnames=[
                "commune_procedure_id",
                *commune_procedure_normalized_and_denormalized_fields,
            ],
            lineterminator="\n",
        )
        writer.writeheader()

        total_inconsistent_commune_procedures_count = 0
        yesterday = (timezone.now() - timedelta(days=1)).day
        commune_procedure_qs = CommuneProcedure.objects.select_related("procedure")
        if yesterday_only:
            commune_procedure_qs = commune_procedure_qs.filter(
                models.Q(procedure__created_at__day=yesterday)
                | models.Q(procedure__last_updated_at__day=yesterday)
            )
        communes_procedures_pks = commune_procedure_qs.values_list("pk", flat=True)

        batches = ceil(len(communes_procedures_pks) / BATCH_SIZE)
        for i, batch_pks in enumerate(
            batched(communes_procedures_pks, BATCH_SIZE, strict=False), 1
        ):
            logger.info(
                "Checking up to %d CommuneProcedure (%d/%d).", BATCH_SIZE, i, batches
            )
            qs = CommuneProcedure.objects.filter(pk__in=batch_pks).select_related(
                "commune", "commune__departement"
            )
            inconsistent_objs = [
                commune_procedure
                for commune_procedure in qs
                if commune_procedure.has_inconsistent_denormalized_fields()
            ]
            total_inconsistent_commune_procedures_count += len(inconsistent_objs)
            for obj in inconsistent_objs:
                writer.writerow(
                    {
                        "commune_procedure_id": obj.pk,
                        **{
                            field: getattr(obj, field)
                            for field in commune_procedure_normalized_and_denormalized_fields
                        },
                    }
                )

            if mode == "update":
                communes_procedures = [
                    obj.update_denormalized_fields(save=False)
                    for obj in inconsistent_objs
                ]
                with transaction.atomic():
                    CommuneProcedure.objects.bulk_update(
                        communes_procedures,
                        fields=CommuneProcedure.DYNAMIC_TO_DENORMALIZED_FIELDS.values(),
                    )

        inconsistencies_msg = f"{total_inconsistent_commune_procedures_count} inconsistent communes_procedures"
        if tell_slack:
            send_slack_message(
                text=inconsistencies_msg,
                url=settings.SLACK_TECH_MONITORING_URL,
            )
        else:
            logger.info(inconsistencies_msg)
