import csv
import re

from django.core.management.base import BaseCommand

from docurba.core.enums import CommuneType
from docurba.core.models import Procedure


class Command(BaseCommand):
    help = "Compute procedure.name_complement based on procedure.name"

    def add_arguments(self, parser: str) -> None:
        parser.add_argument(
            "--wet-run",
            dest="wet_run",
            action="store_true",
            help="Update procedures.name_complement",
        )

    def handle(self, *args: list, wet_run: bool, **options: dict) -> None:  # noqa: ARG002

        queryset = (
            Procedure.objects.select_related("collectivite_porteuse")
            .prefetch_related("perimetre_through__commune")
            .exclude(name="")
            .exclude(name__isnull=True)
            .filter(name_complement="")
        )

        writer = csv.writer(self.stdout, lineterminator="\n")

        writer.writerow(
            [
                "procedure_id",
                "procedure.name_complement",
                "procedure.name",
            ]
        )

        for procedure in queryset.iterator(chunk_size=200):
            perimetre = procedure.perimetre_through.filter(
                collectivite_type=CommuneType.COM
            )

            name = ""
            name_patterns = []
            if len(perimetre) == 1:
                name = perimetre.first().commune.nom
                name_patterns.append(name)
            if procedure.collectivite_porteuse:
                name = name or procedure.collectivite_porteuse.nom
                name_patterns.append(procedure.collectivite_porteuse.nom)

            # Dans certains cas liés à des erreurs d'intégrité, il n'est pas possible de lier une procédure à une collectivite_porteuse
            # Il n'est donc pas possible de générer de nom dynamique
            # On est par conséquent obligé d'ignorer ces procédures
            if not name:
                continue

            numero = ""
            if procedure.numero:
                numero = f"{procedure.numero} "

            dynamic_name = f"{procedure.type} {numero}de {procedure.doc_type} {name}"

            name_complement = ""

            # On saute les procédures pour lesquelles le nom dynamique est identique à la valeur du champ "name"
            # car il n'y a pas de complement du nom dans ce cas
            if procedure.name == dynamic_name:
                continue

            pattern = rf"^.*?({'|'.join(name_patterns)})\s?(.*)$"
            match = re.match(pattern, procedure.name, flags=re.IGNORECASE)

            name_complement = match.group(2) if match else procedure.name

            if name_complement and wet_run:
                procedure.name_complement = name_complement
                procedure.save()

            writer.writerow(
                [
                    procedure.id,
                    name_complement,
                    procedure.name,
                ]
            )
