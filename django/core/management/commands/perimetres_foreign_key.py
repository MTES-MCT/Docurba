from django.core.management.base import BaseCommand

from core.models import CommuneProcedure


class Command(BaseCommand):
    def handle(self, *args, **options) -> None:  # noqa: ANN002, ANN003, ARG002
        foo = CommuneProcedure.objects.select_related("commune").filter(
            commune_direct=None
        )
        for bar in foo:
            bar.commune_direct = bar.commune
        CommuneProcedure.objects.bulk_update(foo, ["commune_direct_id"])


# ALTER TABLE "procedures_perimetres" ADD COLUMN "commune_direct_id" integer NULL CONSTRAINT "procedures_perimetre_commune_direct_id_f5d1c1c7_fk_core_comm" REFERENCES "core_commune"("collectivite_ptr_id") DEFERRABLE INITIALLY DEFERRED; SET CONSTRAINTS "procedures_perimetre_commune_direct_id_f5d1c1c7_fk_core_comm" IMMEDIATE;
# CREATE INDEX "procedures_perimetres_commune_direct_id_f5d1c1c7" ON "procedures_perimetres" ("commune_direct_id") INCLUDE ("procedure_id");
# CREATE INDEX "procedure_including_commune_direct_idx" ON "procedures_perimetres" ("procedure_id") INCLUDE ("commune_direct_id");
# CREATE INDEX "procedures_pkey_secondary_null" ON "procedures" ("id") WHERE "secondary_procedure_of" IS NULL;

# ⚠️ Cette requête SQL permettrait de rapidement mettre à jour les nouvelles entrées dans procedures_perimetres
# sans avoir à modifier drastiquement le script d'import nocturne ou le formulaire de création de procédure.
# UPDATE procedures_perimetres
# SET
# 	commune_direct_id = core_collectivite.id
# FROM
# 	core_collectivite
# WHERE
# 	core_collectivite.code_type = procedures_perimetres.commune_id
# 	AND (
# 		procedures_perimetres.commune_direct_id IS NULL
# 		OR (procedures_perimetres.commune_direct_id <> core_collectivite.id)
# 	);
