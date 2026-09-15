from io import StringIO

import pytest
from django.core.management import call_command

from tests.core.factories import ProcedureFactory


@pytest.mark.django_db
class TestLinkEventsWithEventTypes:
    def test_call_command(self) -> None:

        ProcedureFactory()  # Ok
        procedure = ProcedureFactory(
            collectivite_porteuse_id=66554
        )  # Invalid as 66554 doesn't exists

        out = StringIO()
        call_command(
            "list_inconsistencies_procedure_collectivite_porteuse_inexisting",
            stdout=out,
        )
        expected = f"""procedure.collectivite_porteuse_id,procedure_id
{procedure.collectivite_porteuse_id},{procedure.id}
"""
        assert expected == out.getvalue()
