from io import StringIO

import pytest
from django.core.management import call_command

from docurba.core.models import TypeDocument
from tests.core.factories import CommuneFactory, ProcedureFactory


@pytest.mark.django_db
class TestLinkEventsWithEventTypes:
    @pytest.mark.parametrize(
        (
            "create_args",
            "expected",
            "needs_update",
        ),
        [
            pytest.param(
                {"name": "Test", "name_complement": "Already set"},
                "Already set",
                False,  # existing name_complement : skipped
            ),
            pytest.param(
                {"name": None, "name_complement": ""}, "", False
            ),  # no name : skipped
            pytest.param(
                {"name": "", "name_complement": ""}, "", False
            ),  # no name : skipped
            pytest.param(  # no perimetre name : skipped
                {"name": "Test", "name_complement": "", "collectivite_porteuse": None},
                "",
                False,
            ),
            pytest.param(  # dynamic_name == name : skipped
                {
                    "name": "Élaboration 1 de PLUi CC du test",
                    "name_complement": "",
                    "type": "Élaboration",
                    "doc_type": TypeDocument.PLUI,
                    "numero": "1",
                    "collectivite_porteuse__nom": "CC du test",
                },
                "",
                False,
            ),
            pytest.param(  # dynamic_name == name : skipped (no numero)
                {
                    "name": "Élaboration de PLUi CC du test",
                    "name_complement": "",
                    "type": "Élaboration",
                    "doc_type": TypeDocument.PLUI,
                    "collectivite_porteuse__nom": "CC du test",
                },
                "",
                False,
            ),
            pytest.param(  # dynamic_name == name : skipped (perimetre == 1)
                {
                    "name": "Élaboration 1 de PLU suite-de-test",
                    "name_complement": "",
                    "type": "Élaboration",
                    "doc_type": TypeDocument.PLU,
                    "numero": "1",
                    "with_perimetre": "suite-de-test",
                },
                "",
                False,
            ),
            pytest.param(
                {  # perimetre name found in procedure.name : name_complement is extracted
                    "name": "Élaboration 1 de PLUi CC du test avec un complément du nom",
                    "name_complement": "",
                    "collectivite_porteuse__nom": "CC du test",
                },
                "avec un complément du nom",
                True,
            ),
            pytest.param(  # perimetre name found in procedure.name : name_complement is extracted (perimetre == 1)
                {
                    "name": "Élaboration 1 de PLU suite-de-test avec un complément du nom",
                    "name_complement": "",
                    "with_perimetre": "suite-de-test",
                },
                "avec un complément du nom",
                True,
            ),
            pytest.param(  # perimetre name found in procedure.name : name_complement is extracted (cc_nom is used for matching even if perimetre == 1)
                {
                    "name": "Élaboration 1 de CC du test avec un complément du nom",
                    "name_complement": "",
                    "with_perimetre": "suite-de-test",
                    "collectivite_porteuse__nom": "CC du test",
                },
                "avec un complément du nom",
                True,
            ),
            pytest.param(
                {
                    # perimetre name not found in procedure.name : name_complement is procedure_name
                    "name": "SCOT Du test",
                    "name_complement": "",
                    "collectivite_porteuse__nom": "SCOT du grand test septentrional",
                },
                "SCOT Du test",
                True,
            ),
        ],
    )
    def test_call_command_copy_data(
        self,
        create_args: dict[str],
        expected: str,
        needs_update: bool,  # noqa: FBT001
    ) -> None:

        if "with_perimetre" in create_args:
            create_args["with_perimetre"] = [
                CommuneFactory(nom=create_args["with_perimetre"])
            ]
        procedure = ProcedureFactory(**create_args)

        expected_csv = "procedure_id,procedure.name_complement,procedure.name\n"

        if needs_update:
            expected_csv += f"{procedure.id},{expected},{procedure.name}\n"

        out = StringIO()
        call_command("populate_procedure_name_complement", wet_run=False, stdout=out)

        assert expected_csv == out.getvalue()

        procedure.refresh_from_db()

        assert procedure.name_complement == create_args["name_complement"]
        assert procedure.name == create_args["name"]

        out = StringIO()
        call_command("populate_procedure_name_complement", wet_run=True, stdout=out)
        assert expected_csv == out.getvalue()

        procedure.refresh_from_db()

        assert procedure.name_complement == expected
        assert procedure.name == create_args["name"]
