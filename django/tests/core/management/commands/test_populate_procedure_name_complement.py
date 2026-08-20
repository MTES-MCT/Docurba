import pytest
from django.core.management import call_command

from tests.core.factories import ProcedureFactory


@pytest.mark.django_db
class TestLinkEventsWithEventTypes:
    @pytest.mark.parametrize(
        (
            "create_args",
            "expected",
        ),
        [
            pytest.param({"name": "Test", "name_complement": ""}, "Test"),
            pytest.param(
                {"name": "Test", "name_complement": "Already set"}, "Already set"
            ),
            pytest.param({"name": None, "name_complement": ""}, ""),
            pytest.param({"name": "", "name_complement": ""}, ""),
        ],
    )
    def test_call_command_copy_data(
        self,
        create_args: dict[str],
        expected: str,
    ) -> None:

        procedure = ProcedureFactory(**create_args)

        call_command("populate_procedure_name_complement")

        procedure.refresh_from_db()

        assert procedure.name_complement == expected
        assert procedure.name == create_args["name"]
