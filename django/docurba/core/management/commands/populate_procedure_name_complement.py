import csv
import re

from django.core.management.base import BaseCommand

from docurba.core.enums import CommuneType
from docurba.core.models import Procedure, TypeDocument


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
        valid_types = r"Abrogation|Elaboration|Mise à jour|Mise en compatibilité|Modification simplifiée|Modification|Révision à modalité simplifiée ou Révision allégée|Révision allégée \(ou RMS\)|Révision allégée|Révision simplifiée|Révision"
        valid_doc_types = "|".join(
            sorted([*TypeDocument.values, "PLUS", "SCOTS"], reverse=True)
        )

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
            name_pattern = []
            if len(perimetre) == 1:
                name = perimetre.first().commune.nom
                name_pattern.append(name)
            if procedure.collectivite_porteuse:
                name = name or procedure.collectivite_porteuse.nom
                name_pattern.append(procedure.collectivite_porteuse.nom)

            # Dans certains cas liés à des erreurs d'intégrité, il n'est pas possible de lier une procédure à une collectivite_porteuse
            # Il n'est donc pas possible de générer de nom dynamique
            # On est par conséquent obligé d'ignorer ces procédures
            if not name:
                continue

            numero = ""
            numero_pattern = [r"n?°?\s*\d+"]
            if procedure.numero:
                numero = f"{procedure.numero} "
                numero_pattern.insert(0, procedure.numero)

            dynamic_name = f"{procedure.type} {numero}de {procedure.doc_type} {name}"

            # On saute les procédures pour lesquelles le nom dynamique est identique à la valeur du champ "name"
            # car il n'y a pas de complement du nom dans ce cas
            if procedure.name == dynamic_name:
                continue

            flags = re.IGNORECASE

            name = procedure.name

            # On saute les procédures dont la valeur du champ "nom" est entièrement en majuscule
            # car il n'y a pas de complement du nom dans ce cas parmis les données en base (comportement historique ?)
            if name.isupper():
                continue

            # Ce pattern correspond aux variantes des noms dynmaiques parmis les données présentes en base
            # Il est défini en fonction des données de chaque procédure
            pattern = rf"^(({valid_types})\s+)?(({'|'.join(numero_pattern)})\s+)?(de\s+)?(({valid_doc_types})\s+)?(({'|'.join(name_pattern)})\s*)"

            # On enleve du nom ce qui s'apparente à un nom dynamique possible (type? numero? de? doc_type? nom_commune|nom_collectivite_porteuse )
            name = re.sub(
                pattern,
                "",
                procedure.name,
                flags=re.IGNORECASE,
            )

            # Parmis les données en base, toutes celles préfixées par SD ou SCOT ne contiennent pas de compléments du nom
            name = re.sub(r"^(SD|SCOT).*$", "", name, count=1, flags=flags)

            # un peu de nettoyage tiré du jeu de donnée en base
            name = name.strip("- |:()[]")

            if name:
                # Si name survit a tous ces (mal)traitements, alors c'est un bon candidat pour devenir name_complement
                writer.writerow(
                    [
                        procedure.id,
                        name,
                        procedure.name,
                    ]
                )
                if wet_run:
                    procedure.name_complement = name
                    procedure.save()
