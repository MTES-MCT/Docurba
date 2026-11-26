import pytest
from django.core.management import call_command

from docurba.core import enums as core_enums
from docurba.core import models as core_models
from tests.core.factories import CommuneFactory, ProcedureFactory


@pytest.mark.django_db
class TestUpdateCommuneProcedureMissingCommune:
    def test_no_save(
        self, caplog: pytest.LogCaptureFixture, capsys: pytest.LogCaptureFixture
    ) -> None:
        commune = CommuneFactory(code_insee="30189", type=core_enums.CommuneType.COM)
        procedure = ProcedureFactory(
            with_perimetre=True, with_perimetre__list=[commune], for_snapshot=True
        )
        commune_procedure = core_models.CommuneProcedure.objects.get(
            procedure_id=procedure.pk
        )
        commune_procedure.collectivite_type = core_enums.CommuneType.COMD
        commune_procedure.save()
        with pytest.raises(core_models.Commune.DoesNotExist):
            commune_procedure.commune  # noqa: B018

        call_command("update_commune_procedure_missing_commune")
        commune_procedure.refresh_from_db()
        assert caplog.messages == [
            "Checking communes procedures (1/1).",
            "A COMD became a COM.; Procedure: 1cd65b57-7027-4aa5-8d19-5e1baf8d6f09; commune: 30189;",
            "Not existing: 0",
            "Can be updated: 1",
            "Deleted objects: 0",
            "Successfully updated 1 CommuneProcedure",
        ]
        output = capsys.readouterr()
        assert (
            output.out
            == "action,old_type,new_type,old_commune_id,new_commune_id,procedure_link\nupdated,COMD,COM,30189_COMD,30189_COM,http://localhost:8000/frise/1cd65b57-7027-4aa5-8d19-5e1baf8d6f09\n"
        )

        assert commune_procedure.commune_id == "30189_COMD"
        assert commune_procedure.collectivite_type == core_enums.CommuneType.COMD
        assert commune_procedure.old_collectivite_type == ""

    def test_comd_to_com__no_deletion(self, caplog: pytest.LogCaptureFixture) -> None:
        # # cp.collectivite_code is right but cp.collectivite_type is wrong.
        # # Try to find the commune only if there is one match.
        # # It was a COMD, now it's a COM.
        commune = CommuneFactory(code_insee="30189", type=core_enums.CommuneType.COM)
        procedure = ProcedureFactory(
            with_perimetre=True, with_perimetre__list=[commune], for_snapshot=True
        )
        commune_procedure = core_models.CommuneProcedure.objects.get(
            procedure_id=procedure.pk
        )
        commune_procedure.collectivite_type = core_enums.CommuneType.COMD
        commune_procedure.save()
        with pytest.raises(core_models.Commune.DoesNotExist):
            commune_procedure.commune  # noqa: B018

        call_command("update_commune_procedure_missing_commune", wet_run=True)
        commune_procedure.refresh_from_db()
        assert caplog.messages == [
            "Checking communes procedures (1/1).",
            "A COMD became a COM.; Procedure: 1cd65b57-7027-4aa5-8d19-5e1baf8d6f09; commune: 30189;",
            "Not existing: 0",
            "Can be updated: 1",
            "Deleted objects: 0",
            "Successfully updated 1 CommuneProcedure",
        ]
        assert commune_procedure.commune_id == "30189_COM"
        assert commune_procedure.collectivite_type == core_enums.CommuneType.COM
        assert commune_procedure.old_collectivite_type == core_enums.CommuneType.COMD

    def test_comd_to_com__deletion(self, caplog: pytest.LogCaptureFixture) -> None:
        # # cp.collectivite_code is right but cp.collectivite_type is wrong.
        # # Try to find the commune only if there is one match.
        # # It was a COMD, now it's a COM.
        commune = CommuneFactory(code_insee="30189", type=core_enums.CommuneType.COM)
        procedure = ProcedureFactory(
            with_perimetre=True, with_perimetre__list=[commune], for_snapshot=True
        )
        [commune_procedure] = core_models.CommuneProcedure.objects.bulk_create(
            [
                core_models.CommuneProcedure(
                    procedure_id=procedure.pk,
                    collectivite_type=core_enums.CommuneType.COMD,
                    collectivite_code=commune.code_insee,
                )
            ]
        )
        assert procedure.perimetre_through.count() == 2
        with pytest.raises(core_models.Commune.DoesNotExist):
            commune_procedure.commune  # noqa: B018

        call_command("update_commune_procedure_missing_commune", wet_run=True)
        commune_procedure.refresh_from_db()
        assert procedure.perimetre_through.count() == 1
        # assert commune is None
        assert caplog.messages == [
            "Checking communes procedures (1/1).",
            "A COMD became a COM.; Procedure: 1cd65b57-7027-4aa5-8d19-5e1baf8d6f09; commune: 30189;",
            "Not existing: 0",
            "Can be updated: 1",
            "Deleted objects: 1",
            "Successfully updated 1 CommuneProcedure",
        ]
        assert commune_procedure.commune_id == "30189_COM"
        assert commune_procedure.collectivite_type == core_enums.CommuneType.COM
        assert commune_procedure.old_collectivite_type == core_enums.CommuneType.COMD

    def test_com_to_comd_creation(self, caplog: pytest.LogCaptureFixture) -> None:
        # # It was a COM, now it's a COMD.
        # # Case 1: the new commune is not part of the perimetre. We should create it.
        commune_nouvelle = CommuneFactory(
            code_insee="30192", type=core_enums.CommuneType.COM
        )
        commune = CommuneFactory(
            code_insee="30193",
            type=core_enums.CommuneType.COMD,
            nouvelle=commune_nouvelle,
        )
        procedure = ProcedureFactory(
            with_perimetre=True, with_perimetre__list=[commune], for_snapshot=True
        )
        commune_procedure = core_models.CommuneProcedure.objects.get(
            procedure_id=procedure.pk
        )
        commune_procedure.collectivite_type = core_enums.CommuneType.COM
        commune_procedure.save()
        with pytest.raises(core_models.Commune.DoesNotExist):
            commune_procedure.commune  # noqa: B018

        call_command("update_commune_procedure_missing_commune", wet_run=True)
        commune_procedure.refresh_from_db()
        assert caplog.messages == [
            "Checking communes procedures (1/1).",
            "A COM became a COMD.; Procedure: 1cd65b57-7027-4aa5-8d19-5e1baf8d6f09; commune: 30193;",
            "Creating a CommuneProcedure: 1cd65b57-7027-4aa5-8d19-5e1baf8d6f09; commune: 30193; nouvelle 30192",
            "Not existing: 0",
            "Can be updated: 1",
            "Deleted objects: 0",
            "Successfully updated 1 CommuneProcedure",
        ]
        assert commune_procedure.commune_id == "30193_COMD"
        assert commune_procedure.collectivite_type == core_enums.CommuneType.COMD
        assert commune_procedure.old_collectivite_type == core_enums.CommuneType.COM
        assert procedure.perimetre_through.count() == 2
        assert procedure.perimetre.count() == 2
        assert procedure.perimetre.filter(pk=commune_nouvelle.pk).exists()

    def test_com_to_comd_no_creation(self, caplog: pytest.LogCaptureFixture) -> None:
        # # It was a COM, now it's a COMD.
        # # Case 2: the new commune was already part of the perimetre. We should not create it.
        commune_nouvelle = CommuneFactory(
            code_insee="30194", type=core_enums.CommuneType.COM
        )
        commune = CommuneFactory(
            code_insee="30195",
            type=core_enums.CommuneType.COMD,
            nouvelle=commune_nouvelle,
        )
        procedure = ProcedureFactory(
            with_perimetre=True,
            with_perimetre__list=[commune, commune_nouvelle],
            for_snapshot=True,
        )
        commune_procedure = core_models.CommuneProcedure.objects.get(
            procedure_id=procedure.pk,
            commune=commune,
        )
        commune_procedure.collectivite_type = core_enums.CommuneType.COM
        commune_procedure.save()
        with pytest.raises(core_models.Commune.DoesNotExist):
            commune_procedure.commune  # noqa: B018

        call_command("update_commune_procedure_missing_commune", wet_run=True)
        commune_procedure.refresh_from_db()
        assert caplog.messages == [
            "Checking communes procedures (1/1).",
            "A COM became a COMD.; Procedure: 1cd65b57-7027-4aa5-8d19-5e1baf8d6f09; commune: 30195;",
            "Not existing: 0",
            "Can be updated: 1",
            "Deleted objects: 0",
            "Successfully updated 1 CommuneProcedure",
        ]
        assert commune_procedure.commune_id == "30195_COMD"
        assert commune_procedure.collectivite_type == core_enums.CommuneType.COMD
        assert commune_procedure.old_collectivite_type == core_enums.CommuneType.COM
        assert procedure.perimetre_through.count() == 2
        assert procedure.perimetre.count() == 2
        assert (
            procedure.perimetre.get(pk=commune_nouvelle.pk).type
            == core_enums.CommuneType.COM
        )
        assert (
            procedure.perimetre.get(pk=commune.pk).type == core_enums.CommuneType.COMD
        )

    def test_multiple_communes_found(self, caplog: pytest.LogCaptureFixture) -> None:
        # Multiple communes found.
        commune_nouvelle = CommuneFactory(
            code_insee="30196",
            code_insee_unique="30196",
            type=core_enums.CommuneType.COM,
        )
        commune = CommuneFactory(
            code_insee="30196",
            code_insee_unique="",  # This is how it is stored today.
            type=core_enums.CommuneType.COMD,
            nouvelle=commune_nouvelle,
        )
        procedure = ProcedureFactory(
            with_perimetre=True, with_perimetre__list=[commune]
        )
        commune_procedure = core_models.CommuneProcedure.objects.get(
            procedure_id=procedure.pk
        )
        commune_procedure.collectivite_type = core_enums.CommuneType.COMA
        commune_procedure.save()

        call_command("update_commune_procedure_missing_commune", wet_run=True)
        commune_procedure.refresh_from_db()
        assert caplog.messages == [
            "Checking communes procedures (1/1).",
            "Multiple communes found. Skipping. 30196",
            "Not existing: 0",
            "Can be updated: 1",
            "Deleted objects: 0",
            "Successfully updated 0 CommuneProcedure",
        ]
        assert commune_procedure.collectivite_type == core_enums.CommuneType.COMA

    def test_commune_not_found(self, caplog: pytest.LogCaptureFixture) -> None:
        # Commune not found.
        commune = CommuneFactory(
            code_insee="30197",
            type=core_enums.CommuneType.COM,
        )
        procedure = ProcedureFactory(
            with_perimetre=True, with_perimetre__list=[commune]
        )
        commune_procedure = core_models.CommuneProcedure.objects.get(
            procedure_id=procedure.pk
        )
        commune_procedure.collectivite_code = "00000"
        commune_procedure.save()

        call_command("update_commune_procedure_missing_commune", wet_run=True)
        commune_procedure.refresh_from_db()
        assert caplog.messages == [
            "Checking communes procedures (1/1).",
            "Commune not existing. 00000",
            "Not existing: 1",
            "Can be updated: 1",
            "Deleted objects: 0",
            "Successfully updated 0 CommuneProcedure",
        ]
        assert commune_procedure.collectivite_code == "00000"
        assert commune_procedure.collectivite_type == commune.type
        assert commune_procedure.commune_id == "00000_COM"

    def test_ignored_correct_pk(self, caplog: pytest.LogCaptureFixture) -> None:
        commune = CommuneFactory(code_insee="30188")
        procedure = ProcedureFactory(
            with_perimetre=True, with_perimetre__list=[commune]
        )
        call_command("update_commune_procedure_missing_commune", wet_run=True)
        commune_procedure = core_models.CommuneProcedure.objects.get(
            procedure_id=procedure.pk
        )
        assert caplog.messages == [
            "Not existing: 0",
            "Can be updated: 0",
            "Deleted objects: 0",
            "Successfully updated 0 CommuneProcedure",
        ]
        commune_procedure.refresh_from_db()
        assert commune_procedure.commune_id == commune.collectivite_ptr_id
