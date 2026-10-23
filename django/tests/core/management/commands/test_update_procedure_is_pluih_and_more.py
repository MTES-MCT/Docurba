import pytest
from django.core.management import call_command

from docurba.core.enums import BaseDocumentType, TypeDocument
from tests.core.factories import ProcedureFactory


@pytest.mark.django_db
class TestUpdateIsPluihAndMore:
    @pytest.mark.parametrize(
        "base_doc_type",
        [
            TypeDocument.POS,
            TypeDocument.PLU,
        ],
    )
    def test_excluded_doc_types(
        self,
        base_doc_type: str,
    ) -> None:
        procedure = ProcedureFactory(
            base_doc_type=base_doc_type,
            vaut_PDM=True,
        )
        assert procedure.doc_type == base_doc_type

        call_command("update_procedure_is_pluih_and_more", wet_run=True)
        procedure.refresh_from_db()
        assert procedure.doc_type == base_doc_type

    @pytest.mark.parametrize(
        "doc_type",
        [
            TypeDocument.PLUIM,
            TypeDocument.PLUISM,
        ],
    )
    def test_should_be_pdu(
        self,
        doc_type: TypeDocument,
    ) -> None:
        procedure = ProcedureFactory(
            base_doc_type=BaseDocumentType.PLU,
            doc_type=doc_type,
            from_sudocuh="123456789",
            vaut_PDM=False,
        )

        call_command("update_procedure_is_pluih_and_more", wet_run=True)
        procedure.refresh_from_db()
        assert procedure.vaut_PDM is True
        assert procedure.vaut_PLH is False

    @pytest.mark.parametrize(
        "doc_type",
        [
            TypeDocument.PLUIH,
            TypeDocument.PLUISH,
        ],
    )
    def test_should_be_pluih(
        self,
        doc_type: TypeDocument,
    ) -> None:
        procedure = ProcedureFactory(
            base_doc_type=BaseDocumentType.PLU,
            doc_type=doc_type,
            from_sudocuh="123456789",
            vaut_PDM=False,
        )

        call_command("update_procedure_is_pluih_and_more", wet_run=True)
        procedure.refresh_from_db()
        assert procedure.vaut_PDM is False
        assert procedure.vaut_PLH is True

    @pytest.mark.parametrize(
        "doc_type",
        [
            TypeDocument.PLUIHM,
            TypeDocument.PLUISHM,
        ],
    )
    def test_should_be_pdu_and_pluih(
        self,
        doc_type: TypeDocument,
    ) -> None:
        procedure = ProcedureFactory(
            base_doc_type=BaseDocumentType.PLU,
            doc_type=doc_type,
            from_sudocuh="123456789",
            vaut_PDM=False,
        )

        call_command("update_procedure_is_pluih_and_more", wet_run=True)
        procedure.refresh_from_db()
        assert procedure.vaut_PDM is True
        assert procedure.vaut_PLH is True

    @pytest.mark.parametrize(
        "base_doc_type",
        [
            TypeDocument.SCOT,
            TypeDocument.SD,
            TypeDocument.CC,
        ],
    )
    def test_should_not_be_pdu_and_pluih(
        self,
        base_doc_type: str,
    ) -> None:
        procedure = ProcedureFactory(
            base_doc_type=base_doc_type,
            doc_type=base_doc_type,
            vaut_PDM=True,
            vaut_PLH=True,
        )

        call_command("update_procedure_is_pluih_and_more", wet_run=True)
        procedure.refresh_from_db()
        assert procedure.vaut_PDM is False
        assert procedure.vaut_PLH is False

    @pytest.mark.parametrize(
        "base_doc_type",
        [
            TypeDocument.SCOT,
            TypeDocument.SD,
        ],
    )
    def test_should_be_scot(
        self,
        base_doc_type: str,
    ) -> None:
        procedure = ProcedureFactory(
            from_sudocuh=None,
            vaut_SCoT=False,
            base_doc_type=base_doc_type,
            doc_type=base_doc_type,
        )

        call_command("update_procedure_is_pluih_and_more", wet_run=True)
        procedure.refresh_from_db()
        assert procedure.vaut_SCoT is True

    @pytest.mark.parametrize(
        "base_doc_type",
        [
            TypeDocument.PLU,
            TypeDocument.POS,
            TypeDocument.CC,
        ],
    )
    def test_should_not_be_scot__plu(
        self,
        base_doc_type: str,
    ) -> None:
        procedure = ProcedureFactory(
            from_sudocuh=None,
            vaut_SCoT=True,
            base_doc_type=base_doc_type,
            doc_type=base_doc_type,
        )

        call_command("update_procedure_is_pluih_and_more", wet_run=True)
        procedure.refresh_from_db()
        assert procedure.vaut_SCoT is False

    @pytest.mark.parametrize(
        "doc_type",
        [
            TypeDocument.PLUI,
            TypeDocument.PLUIHM,
        ],
    )
    def test_should_not_be_scot__plu_variations(
        self,
        doc_type: str,
    ) -> None:
        procedure = ProcedureFactory(
            from_sudocuh=None,
            vaut_SCoT=True,
            base_doc_type=BaseDocumentType.PLU,
            doc_type=doc_type,
        )

        call_command("update_procedure_is_pluih_and_more", wet_run=True)
        procedure.refresh_from_db()
        assert procedure.vaut_SCoT is False

    def test_exclude_sudocuh_procedures(
        self,
    ) -> None:
        procedure = ProcedureFactory(
            from_sudocuh="12345678",
            vaut_SCoT=True,
            base_doc_type=BaseDocumentType.PLU,
        )

        call_command("update_procedure_is_pluih_and_more", wet_run=True)
        procedure.refresh_from_db()
        assert procedure.vaut_SCoT is True
