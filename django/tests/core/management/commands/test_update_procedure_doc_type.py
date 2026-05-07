import pytest
from django.core.management import call_command

from docurba.core.enums import CommuneType, TypeCollectivite
from docurba.core.models import TypeDocument, ViewCommuneAdhesionsDeep
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
    ) -> None:
        # La règle métier : ajouter un i à PLU pour tous les types des procédures PLU ayant plusieurs communes dans leur périmètre sans compter les COMD ou COMA.
        # La collectivité porteuse de ces procédures est forcément un EPCI.

        # Nominal case: perimetre counts 1 commune.
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

        assert plu_procedure.perimetre.count() == 1
        assert should_be_plui_procedure.perimetre.count() == 2
        assert should_be_plui_with_comd_procedure.perimetre.count() == 3
        assert plu_with_comd_procedure.perimetre.count() == 2

        # Add PLUiS
        #  Il s'agit d'un PLUiS quand 1<'nombre de communes du périmètre de la procédure' < 'nombre de communes du périmètre de l'EPCI porteur'.

        call_command("update_procedure_doc_type", wet_run=True)

        stdout, _ = capsys.readouterr()
        stdout_formatted = stdout.splitlines()
        assert stdout_formatted == [
            "Raw results to process: 2",
            "Procedures 'sectorielles' to be updated: 0",
            "Procedures not 'sectorielles' to be updated: 2",
            "Updated procedures 'sectorielles': 0",
            "Updated procedures not 'sectorielles': 2",
        ]
        plu_procedure.refresh_from_db()
        assert plu_procedure.doc_type == TypeDocument.PLU
        plu_with_comd_procedure.refresh_from_db()
        assert plu_with_comd_procedure.doc_type == TypeDocument.PLU
        should_be_plui_procedure.refresh_from_db()
        assert should_be_plui_procedure.doc_type == TypeDocument.PLUI
        should_be_plui_with_comd_procedure.refresh_from_db()
        assert should_be_plui_with_comd_procedure.doc_type == TypeDocument.PLUI

    def test_call_command_groupement_porteur_not_epci(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        plui_perimetre = CommuneFactory.create_batch(2)
        collectivite_porteuse_plui = CollectiviteFactory(
            type=TypeCollectivite.COM,
        )
        collectivite_porteuse_plui.collectivites_adherentes.add(*plui_perimetre)
        procedure = ProcedureFactory(
            collectivite_porteuse=collectivite_porteuse_plui,
            doc_type=TypeDocument.PLU,
            with_perimetre=plui_perimetre,
        )
        call_command("update_procedure_doc_type", wet_run=True)
        stdout, _ = capsys.readouterr()
        stdout_formatted = stdout.splitlines()
        assert stdout_formatted == [
            "Raw results to process: 1",
            f"{procedure.pk} is not managed by an EPCI. Skipping.",
            "Procedures 'sectorielles' to be updated: 0",
            "Procedures not 'sectorielles' to be updated: 0",
            "Updated procedures 'sectorielles': 0",
            "Updated procedures not 'sectorielles': 0",
        ]
        assert procedure.doc_type == TypeDocument.PLU

    def test_call_command_pluis(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        plui_perimetre = CommuneFactory.create_batch(2)
        collectivite_porteuse_plui = CollectiviteFactory(
            type=TypeCollectivite.CC,
        )
        collectivite_porteuse_plui.collectivites_adherentes.add(*plui_perimetre)
        procedure = ProcedureFactory(
            collectivite_porteuse=collectivite_porteuse_plui,
            doc_type=TypeDocument.PLU,
            with_perimetre=plui_perimetre,
        )
        # Now add a new commune in the groupement area. The PLUI should be "sectoriel" because it concerns
        # only a subarea of the groupement area.
        collectivite_porteuse_plui.collectivites_adherentes.add(CommuneFactory())
        ViewCommuneAdhesionsDeep._refresh_materialized_view()  # noqa: SLF001

        call_command("update_procedure_doc_type", wet_run=True)
        stdout, _ = capsys.readouterr()
        stdout_formatted = stdout.splitlines()
        assert stdout_formatted == [
            "Raw results to process: 1",
            "Procedures 'sectorielles' to be updated: 1",
            "Procedures not 'sectorielles' to be updated: 0",
            "Updated procedures 'sectorielles': 1",
            "Updated procedures not 'sectorielles': 0",
        ]
        procedure.refresh_from_db()
        assert procedure.doc_type == TypeDocument.PLUIS
