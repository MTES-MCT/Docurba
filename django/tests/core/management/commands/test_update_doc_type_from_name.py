import pytest
from django.core.management import call_command

from docurba.core.enums import TypeDocument
from tests.core.factories import ProcedureFactory


@pytest.mark.django_db
class TestUpdateSudocuhDocType:
    @pytest.mark.parametrize(
        (
            "doc_type_in_name",
            "expected_doc_type",
        ),
        [
            pytest.param("PLUiH", TypeDocument.PLUIH),
            pytest.param("PLUiHM", TypeDocument.PLUIHM),
            pytest.param("PLUiM", TypeDocument.PLUIM),
            pytest.param("PLUiSM", TypeDocument.PLUISM),
            pytest.param("PLUiSH", TypeDocument.PLUISH),
            pytest.param("PLUiSHM", TypeDocument.PLUISHM),
            # ignore case
            pytest.param("pluiH", TypeDocument.PLUIH),
            # other types
            pytest.param("SCOT", TypeDocument.PLU),
            pytest.param("SD", TypeDocument.PLU),
        ],
    )
    def test_call_command_change_doc_type(
        self,
        doc_type_in_name: str,
        expected_doc_type: TypeDocument,
    ) -> None:

        procedure = ProcedureFactory(
            doc_type=TypeDocument.PLU,
            from_sudocuh="123456789",
            name=f"blah blah {doc_type_in_name} more blah blah",
        )

        call_command("update_doc_type_from_name", wet_run=True)

        procedure.refresh_from_db()

        assert procedure.doc_type == expected_doc_type

    def test_call_command_ignore_docurba_procedures(
        self,
    ) -> None:

        procedure = ProcedureFactory(
            doc_type=TypeDocument.PLU,
            from_sudocuh=None,
            name="blah blah PLUiHM more blah blah",
        )

        call_command("update_doc_type_from_name", wet_run=True)

        procedure.refresh_from_db()

        assert procedure.doc_type == TypeDocument.PLUIHM
