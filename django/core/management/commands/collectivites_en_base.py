from json import loads
from pathlib import Path

from django.core.management.base import BaseCommand

from core.models import Collectivite, Commune, Departement, Region

NUXT_DATA = (
    Path(__file__).parent.parent.parent.parent.parent
    / "nuxt"
    / "server-middleware"
    / "Data"
)


class Command(BaseCommand):
    def handle(self, *args, **options) -> None:  # noqa: ANN002, ANN003, ARG002
        Commune.objects.all().delete()
        Collectivite.objects.all().delete()
        Departement.objects.all().delete()
        Region.objects.all().delete()
        self.stdout.write("All existing data deleted.")

        regions_json = loads((NUXT_DATA / "INSEE" / "regions.json").read_text())
        regions = Region.objects.bulk_create(
            [
                Region(code_insee=region["code"], nom=region["intituleSansArticle"])
                for region in regions_json
            ]
        )
        regions_by_code = {region.code_insee: region for region in regions}
        self.stdout.write(f"{len(regions)} regions loaded.")

        departements_json = loads(
            (NUXT_DATA / "INSEE" / "departements.json").read_text()
        )
        departements = Departement.objects.bulk_create(
            [
                Departement(
                    code_insee=departement["code"],
                    nom=departement["intituleSansArticle"],
                    region=regions_by_code[departement["region"]["code"]],
                )
                for departement in departements_json
            ]
        )
        departements_by_code = {
            departement.code_insee: departement for departement in departements
        }
        self.stdout.write(f"{len(departements)} departements loaded.")

        groupements_json = loads(
            (NUXT_DATA / "referentiels" / "groupements_2024.json").read_text()
        )
        groupements = Collectivite.objects.bulk_create(
            [
                Collectivite(
                    id=f"{groupement['code']}_{groupement['type']}",
                    code_insee=groupement["code"],
                    type=groupement["type"],
                    nom=groupement["intitule"],
                    departement=departements_by_code[groupement["departementCode"]],
                    competence_plan=groupement["competencePLU"],
                    competence_schema=groupement["competenceSCOT"],
                )
                for groupement in groupements_json
            ]
        )
        groupements_by_code = {
            groupement.code_insee: groupement for groupement in groupements
        }
        self.stdout.write(f"{len(groupements)} groupements loaded.")

        Collectivite.adhesions.through.objects.bulk_create(
            [
                Collectivite.adhesions.through(
                    from_collectivite=groupements_by_code[groupement["code"]],
                    to_collectivite=groupements_by_code[membre_de["code"]],
                )
                for groupement in groupements_json
                for membre_de in groupement["groupements"]
            ],
            ignore_conflicts=True,
        )
        self.stdout.write("Groupement relationships loaded.")

        communes_json = loads(
            (NUXT_DATA / "referentiels" / "communes.json").read_text()
        )
        communes_by_code = {}
        for commune in communes_json:
            if commune["type"] == "COM":
                commune_instance = Commune.objects.create(
                    id=f"{commune['code']}_{commune['type']}",
                    code_insee=commune["code"],
                    type=commune["type"],
                    nom=commune["intitule"],
                    departement=departements_by_code[commune["departementCode"]],
                    competence_plan=commune["competencePLU"],
                    competence_schema=commune["competenceSCOT"],
                    intercommunalite=groupements_by_code.get(
                        commune["intercommunaliteCode"]
                    ),
                )
                communes_by_code[commune_instance.code_insee] = commune_instance
        self.stdout.write(f"{len(communes_by_code)} communes of type 'COM' loaded.")

        Collectivite.adhesions.through.objects.bulk_create(
            [
                Collectivite.adhesions.through(
                    from_collectivite=communes_by_code[commune["code"]],
                    to_collectivite=groupements_by_code[membre_de["code"]],
                )
                for commune in communes_json
                for membre_de in commune["groupements"]
            ]
        )
        self.stdout.write("Commune relationships loaded.")

        for commune in communes_json:
            if commune["type"] != "COM":
                commune_parente = communes_by_code[commune["codeParent"]]
                Commune.objects.create(
                    id=f"{commune['code']}_{commune['type']}",
                    code_insee=commune["code"]
                    if commune_parente.code_insee != commune["code"]
                    else None,
                    type=commune["type"],
                    nom=commune["intitule"],
                    nouvelle=commune_parente,
                    departement=commune_parente.departement,
                    competence_plan=commune["competencePLU"],
                    competence_schema=commune["competenceSCOT"],
                )
        self.stdout.write("Other types of communes loaded.")
