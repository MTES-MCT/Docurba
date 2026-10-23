import pytest
from django.core.management import call_command

from docurba.core.enums import TypeDocument
from tests.core.factories import CollectiviteFactory, CommuneFactory, ProcedureFactory


@pytest.mark.django_db
class TestUpdateSudocuhDocType:
    # si intercommunal ET is_pdu = false ET is_pluih = true alors doc_type = PLUiH
    # si intercommunal ET is_pdu = true ET is_pluih = true alors doc_type = PLUiHM
    # si intercommunal ET is_pdu = true ET is_pluih = false alors doc_type = PLUiM
    @pytest.mark.parametrize(
        (
            "is_pdu",
            "is_pluih",
            "expected_doc_type",
        ),
        [
            pytest.param(False, True, TypeDocument.PLUIH),
            pytest.param(True, True, TypeDocument.PLUIHM),
            pytest.param(True, False, TypeDocument.PLUIM),
        ],
    )
    def test_intercommunal(
        self,
        is_pdu: bool,  # noqa: FBT001
        is_pluih: bool,  # noqa: FBT001
        expected_doc_type: TypeDocument,
    ) -> None:
        communes = CommuneFactory.create_batch(2)
        procedure = ProcedureFactory(
            doc_type=TypeDocument.PLU,
            from_sudocuh="123456789",
            vaut_PDM=is_pdu,
            vaut_PLH=is_pluih,
            with_perimetre=communes,
        )

        call_command("update_doc_type", wet_run=True)
        procedure.refresh_from_db()
        assert procedure.doc_type == expected_doc_type

    # si intercommunal ET is_sectoriel ET is_pdu = false ET is_pluih = true alors doc_type = PLUiSH
    # si intercommunal ET is_sectoriel ET is_pluih = true ET is_pdu = true alors doc_type = PLUiSHM
    # si intercommunal ET is_sectoriel ET is_pdu = true ET is_pluih = false alors doc_type = PLUiSM
    @pytest.mark.parametrize(
        (
            "is_pdu",
            "is_pluih",
            "expected_doc_type",
        ),
        [
            pytest.param(False, True, TypeDocument.PLUISH),
            pytest.param(True, True, TypeDocument.PLUISHM),
            pytest.param(True, False, TypeDocument.PLUISM),
        ],
    )
    def test_intercommunal_sectoriel(
        self,
        is_pdu: bool,  # noqa: FBT001
        is_pluih: bool,  # noqa: FBT001
        expected_doc_type: TypeDocument,
    ) -> None:
        communes = CommuneFactory.create_batch(3)
        collectivite_porteuse = CollectiviteFactory(
            with_members=True,
            with_members__list=communes,
        )
        procedure = ProcedureFactory(
            doc_type=TypeDocument.PLU,
            from_sudocuh="123456789",
            vaut_PDM=is_pdu,
            vaut_PLH=is_pluih,
            with_perimetre=communes[:2],
            collectivite_porteuse=collectivite_porteuse,
        )

        call_command("update_doc_type", wet_run=True)
        procedure.refresh_from_db()
        assert procedure.doc_type == expected_doc_type

    def test_docurba_procedures_ignored(
        self,
    ) -> None:
        communes = CommuneFactory.create_batch(2)
        procedure = ProcedureFactory(
            doc_type=TypeDocument.PLU, from_sudocuh=None, with_perimetre=communes
        )

        call_command("update_doc_type", wet_run=True)

        procedure.refresh_from_db()

        assert procedure.doc_type == TypeDocument.PLU

    def test_to_pluis(
        self,
    ) -> None:
        communes = CommuneFactory.create_batch(3)
        collectivite_porteuse = CollectiviteFactory(
            with_members=True,
            with_members__list=communes,
        )
        procedure = ProcedureFactory(
            doc_type=TypeDocument.PLU,
            from_sudocuh="123456789",
            with_perimetre=communes[:2],
            collectivite_porteuse=collectivite_porteuse,
        )
        call_command("update_doc_type", wet_run=True)

        procedure.refresh_from_db()

        assert procedure.doc_type == TypeDocument.PLUIS
