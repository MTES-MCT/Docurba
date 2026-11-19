import csv
import logging
from itertools import batched
from math import ceil

from django.core.management.base import BaseCommand
from django.db import models, transaction

from docurba.core.enums import CommuneType
from docurba.core.models import Commune, CommuneProcedure

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Update commune_procedure whenever possible."

    def add_arguments(self, parser: str) -> None:
        parser.add_argument(
            "--wet-run",
            dest="wet_run",
            action="store_true",
            help="Persists changes in database",
        )

    def handle(  # noqa: C901, PLR0912, PLR0915
        self,
        *args: list,  # noqa: ARG002
        wet_run: bool,
        **options: dict,  # noqa: ARG002
    ) -> None:
        cp_pks = CommuneProcedure.objects.filter(
            ~models.Exists(Commune.objects.filter(id=models.OuterRef("commune_id")))
        ).values_list("pk", flat=True)
        can_be_updated_counter = 0
        to_be_deleted_counter = 0
        updated_counter = 0
        not_existing_counter = 0

        writer = csv.DictWriter(
            self.stdout,
            fieldnames=[
                "action",
                "old_type",
                "new_type",
                "old_commune_id",
                "new_commune_id",
                "procedure_link",
            ],
            lineterminator="\n",
        )
        writer.writeheader()

        batches = ceil(len(cp_pks) / 2000)
        for i, batch_pks in enumerate(batched(cp_pks, 2000, strict=False), 1):
            to_be_created = []
            to_be_updated = []
            to_be_deleted = []
            logger.info("Checking communes procedures (%d/%d).", i, batches)
            qs = CommuneProcedure.objects.filter(
                pk__in=batch_pks
            ).select_related(
                "procedure"
            )  # can't use select related because it creates an inner join, not a left join.
            for cp in qs:
                pk = cp.commune_id
                can_be_updated_counter += 1
                cp.old_commune_id = cp.commune_id
                results = Commune.objects.filter(code_insee=cp.collectivite_code)
                match results.count():
                    case 0:
                        # Commune does not exist. Stop here.
                        not_existing_counter += 1
                        logger.info(
                            "Commune not existing. %s",
                            cp.collectivite_code,
                        )
                        continue
                    case 1:
                        found_commune = results.first()
                        logger.info(
                            "A %s became a %s.; Procedure: %s; commune: %s;",
                            cp.collectivite_type,
                            found_commune.type,
                            cp.procedure.pk,
                            found_commune.code_insee,
                        )
                        if (
                            cp.collectivite_type != CommuneType.COM
                            and found_commune.type == CommuneType.COM
                        ):
                            # We should delete the "old nouvelle commune" from the "perimetre".
                            existing_com = cp.procedure.perimetre_through.filter(
                                commune__code_insee=found_commune.code_insee,
                                commune__type=CommuneType.COM,
                            )
                            if existing_com.exists():
                                to_be_deleted_counter += 1
                                to_be_deleted.append(existing_com.get())
                        elif (
                            cp.collectivite_type == CommuneType.COM
                            and found_commune.type != CommuneType.COM
                        ):
                            nouvelle_code_insee = found_commune.nouvelle.code_insee
                            if (
                                nouvelle_code_insee
                                not in cp.procedure.perimetre_through.values_list(
                                    "commune__code_insee", flat=True
                                )
                            ):
                                # Add it
                                logger.info(
                                    "Creating a CommuneProcedure: %s; commune: %s; nouvelle %s",
                                    cp.procedure.pk,
                                    found_commune.code_insee,
                                    nouvelle_code_insee,
                                )
                                new_cp = CommuneProcedure(
                                    collectivite_code=found_commune.nouvelle.code_insee,
                                    collectivite_type=found_commune.nouvelle.type,
                                    procedure_id=cp.procedure_id,
                                    opposable=False,
                                )
                                to_be_created.append(new_cp)

                        cp.old_collectivite_type = cp.collectivite_type
                        cp.collectivite_type = found_commune.type
                        pk = found_commune.id
                        updated_counter += 1
                    case _:
                        logger.info(
                            "Multiple communes found. Skipping. %s",
                            cp.collectivite_code,
                        )
                        continue
                cp.commune_id = pk
                to_be_updated.append(cp)

            for cp in to_be_updated:
                writer.writerow(
                    {
                        "action": "updated",
                        "old_type": cp.old_collectivite_type,
                        "new_type": cp.collectivite_type,
                        "old_commune_id": cp.old_commune_id,
                        "new_commune_id": cp.commune_id,
                        "procedure_link": cp.procedure.get_absolute_url(),
                    }
                )
            for cp in to_be_created:
                writer.writerow(
                    {
                        "action": "created",
                        "old_type": "",
                        "new_type": cp.collectivite_type,
                        "old_commune_id": "",
                        "new_commune_id": cp.commune_id,
                        "procedure_link": cp.procedure.get_absolute_url(),
                    }
                )
            for cp in to_be_deleted:
                writer.writerow(
                    {
                        "action": "deleted",
                        "old_type": "",
                        "new_type": cp.collectivite_type,
                        "old_commune_id": "",
                        "new_commune_id": cp.commune_id,
                        "procedure_link": cp.procedure.get_absolute_url(),
                    }
                )
            if wet_run:
                with transaction.atomic():
                    CommuneProcedure.objects.filter(
                        id__in=[o.id for o in to_be_deleted]
                    ).delete()
                    CommuneProcedure.objects.bulk_create(to_be_created)
                    CommuneProcedure.objects.bulk_update(
                        to_be_updated,
                        fields=[
                            "commune_id",
                            "collectivite_type",
                            "old_collectivite_type",
                        ],
                    )

        logger.info("Not existing: %s", not_existing_counter)
        logger.info("Can be updated: %s", can_be_updated_counter)
        logger.info("Deleted objects: %s", to_be_deleted_counter)
        logger.info("Successfully updated %s CommuneProcedure", updated_counter)
