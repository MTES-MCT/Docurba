import csv
import pathlib

import pytest
from django.core.management import call_command
from pytest_django.fixtures import SettingsWrapper

from docurba.core.enums import CommuneType, TypeCollectivite
from docurba.core.models import (
    TypeDocument,
)
from tests.core.factories import (
    CollectiviteFactory,
    CommuneFactory,
    ProcedureFactory,
)


@pytest.mark.django_db
class TestUpdateProcedureDocType:
    def test_call_command_wet_run(
        self,
        capsys: pytest.CaptureFixture[str],
        settings: SettingsWrapper,
        tmp_path: pathlib.Path,
    ) -> None:
        settings.EXPORTS_DIR = tmp_path
        ###### IGNORED
        # Typical PLU: perimetre counts 1 commune.
        collectivite_porteuse_plu = CommuneFactory()
        plu_perimetre = [collectivite_porteuse_plu]
        plu_procedure = ProcedureFactory(
            collectivite_porteuse=collectivite_porteuse_plu,
            doc_type=TypeDocument.PLU,
            with_perimetre=plu_perimetre,
        )

        # COMD case: perimetre counts 2 communes but it should count as one
        # because procedures don't apply anymore to COMD. They can be ignored.
        collectivite_porteuse_plu_with_comd = CommuneFactory()
        plu_with_comd_perimetre = [
            collectivite_porteuse_plu_with_comd,
            CommuneFactory(type=CommuneType.COMD),
        ]
        plu_with_comd_procedure = ProcedureFactory(
            collectivite_porteuse=collectivite_porteuse_plu_with_comd,
            doc_type=TypeDocument.PLU,
            with_perimetre=plu_with_comd_perimetre,
        )

        # COMD only should be ignored.
        comd = [
            CommuneFactory(type=CommuneType.COMD),
        ]
        ProcedureFactory(
            collectivite_porteuse=comd[0],
            doc_type=TypeDocument.PLU,
            with_perimetre=comd,
        )

        # Doc types other than PLU should be ignored.
        scot_perimetre = CommuneFactory.create_batch(2)
        collectivite_porteuse_scot = CollectiviteFactory(
            type=TypeCollectivite.CC,
        )
        collectivite_porteuse_scot.collectivites_adherentes.add(*scot_perimetre)
        scot = ProcedureFactory(
            collectivite_porteuse=collectivite_porteuse_scot,
            doc_type=TypeDocument.SCOT,
            with_perimetre=scot_perimetre,
        )

        ###### INCLUDED
        plui_perimetre = CommuneFactory.create_batch(2)
        collectivite_porteuse_plui = CollectiviteFactory(
            type=TypeCollectivite.CC,
        )
        collectivite_porteuse_plui.collectivites_adherentes.add(*plui_perimetre)
        should_be_plui_procedure = ProcedureFactory(
            collectivite_porteuse=collectivite_porteuse_plui,
            doc_type=TypeDocument.PLU,
            with_perimetre=plui_perimetre,
        )

        # Several communes including one COMD. It should be a PLUI.
        plui_with_comd_perimetre = [
            *CommuneFactory.create_batch(2),
            CommuneFactory(type=CommuneType.COMD),
        ]
        collectivite_porteuse_plui_with_comd = CollectiviteFactory(
            type=TypeCollectivite.CC,
        )
        collectivite_porteuse_plui_with_comd.collectivites_adherentes.add(
            *plui_with_comd_perimetre
        )
        should_be_plui_with_comd_procedure = ProcedureFactory(
            collectivite_porteuse=collectivite_porteuse_plui_with_comd,
            doc_type=TypeDocument.PLU,
            with_perimetre=plui_with_comd_perimetre,
        )

        # Collectivite porteuse does not exist anymore. It should be a PLUI.
        should_be_plui_collectivite_porteuse_missing = ProcedureFactory(
            collectivite_porteuse_id="123456789",
            doc_type=TypeDocument.PLU,
            with_perimetre=CommuneFactory.create_batch(2),
        )

        assert plu_procedure.perimetre.count() == 1
        assert plu_with_comd_procedure.perimetre.count() == 2
        assert scot.perimetre.count() == 2
        assert should_be_plui_procedure.perimetre.count() == 2
        assert should_be_plui_with_comd_procedure.perimetre.count() == 3
        assert should_be_plui_collectivite_porteuse_missing.perimetre.count() == 2

        call_command("update_procedure_doc_type", wet_run=True)

        stdout, _ = capsys.readouterr()
        stdout_formatted = stdout.splitlines()
        assert stdout_formatted == [
            "Raw results to process: 3",
            "Procedures to be updated: 3",
            "Updated procedures: 3",
        ]
        plu_procedure.refresh_from_db()
        assert plu_procedure.doc_type == TypeDocument.PLU
        plu_with_comd_procedure.refresh_from_db()
        assert plu_with_comd_procedure.doc_type == TypeDocument.PLU
        scot.refresh_from_db()
        assert scot.doc_type == TypeDocument.SCOT

        should_be_plui_procedure.refresh_from_db()
        assert should_be_plui_procedure.doc_type == TypeDocument.PLUI
        should_be_plui_with_comd_procedure.refresh_from_db()
        assert should_be_plui_with_comd_procedure.doc_type == TypeDocument.PLUI
        should_be_plui_collectivite_porteuse_missing.refresh_from_db()
        assert (
            should_be_plui_collectivite_porteuse_missing.doc_type == TypeDocument.PLUI
        )
        filename = pathlib.Path(settings.EXPORTS_DIR) / "from_plu_to_plui.csv"
        with filename.open() as csvfile:
            results = list(csv.DictReader(csvfile, delimiter=";"))
            assert len(results) == 3

    def test_call_command_groupement_porteur_not_epci(
        self,
        capsys: pytest.CaptureFixture[str],
        settings: SettingsWrapper,
        tmp_path: pathlib.Path,
    ) -> None:
        settings.EXPORTS_DIR = tmp_path
        perimetre = CommuneFactory.create_batch(2)
        collectivite_porteuse_plui = CollectiviteFactory(
            type=TypeCollectivite.COM,
        )
        collectivite_porteuse_plui.collectivites_adherentes.add(*perimetre)
        should_be_plui_procedure = ProcedureFactory(
            collectivite_porteuse=collectivite_porteuse_plui,
            doc_type=TypeDocument.PLU,
            with_perimetre=perimetre,
        )

        collectivite_porteuse_plui_archived = CollectiviteFactory(
            type=TypeCollectivite.COM,
        )
        collectivite_porteuse_plui_archived.collectivites_adherentes.add(*perimetre)
        archived_procedure = ProcedureFactory(
            collectivite_porteuse=collectivite_porteuse_plui_archived,
            doc_type=TypeDocument.PLU,
            with_perimetre=perimetre,
            soft_delete=True,
        )

        call_command("update_procedure_doc_type", wet_run=True)
        stdout, _ = capsys.readouterr()
        stdout_formatted = stdout.splitlines()
        assert stdout_formatted == [
            "Raw results to process: 2",
            f"{archived_procedure.pk} is not managed by an EPCI and is archived. Skipping.",
            "Procedures to be updated: 1",
            "Updated procedures: 1",
        ]

        should_be_plui_procedure.refresh_from_db()
        archived_procedure.refresh_from_db()
        assert should_be_plui_procedure.doc_type == TypeDocument.PLUI
        assert archived_procedure.doc_type == TypeDocument.PLU

        filename = pathlib.Path(settings.EXPORTS_DIR) / "from_plu_to_plui.csv"
        with filename.open() as csvfile:
            results = list(csv.DictReader(csvfile, delimiter=";"))
            assert len(results) == 2

    def test_call_command_update_procedure_name(
        self,
        settings: SettingsWrapper,
        tmp_path: pathlib.Path,
    ) -> None:
        settings.EXPORTS_DIR = tmp_path
        perimetre = CommuneFactory.create_batch(2)
        collectivite_porteuse_plui = CollectiviteFactory(
            type=TypeCollectivite.COM,
        )
        collectivite_porteuse_plui.collectivites_adherentes.add(*perimetre)
        procedure_with_hardcoded_name = ProcedureFactory(
            collectivite_porteuse=collectivite_porteuse_plui,
            doc_type=TypeDocument.PLU,
            with_perimetre=perimetre,
            name="Mise à jour de PLU Est Ensemble",
        )
        procedure_without_hardcoded_name = ProcedureFactory(
            collectivite_porteuse=collectivite_porteuse_plui,
            doc_type=TypeDocument.PLU,
            with_perimetre=perimetre,
            name="",
        )
        call_command("update_procedure_doc_type", wet_run=True)
        procedure_with_hardcoded_name.refresh_from_db()
        procedure_without_hardcoded_name.refresh_from_db()
        assert procedure_with_hardcoded_name.name == "Mise à jour de PLUi Est Ensemble"
        assert procedure_without_hardcoded_name.name == ""
