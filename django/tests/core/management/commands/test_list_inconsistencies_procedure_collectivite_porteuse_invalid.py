from io import StringIO

import pytest
from django.core.management import call_command

from docurba.core.enums import CommuneType
from tests.core.factories import CommuneFactory, ProcedureFactory


@pytest.mark.django_db
class TestLinkEventsWithEventTypes:
    def test_call_command(self) -> None:

        commune = CommuneFactory(code_insee="30032")
        procedure = ProcedureFactory(
            id="00000000-0000-0000-1111-000000000000",
            with_perimetre=[commune],
        )

        procedure_comd = ProcedureFactory(  # COMD are ignored when computing perimeter
            id="00000000-0000-0000-2222-000000000000",
            with_perimetre=[
                commune,
                CommuneFactory(code_insee="30034", type=CommuneType.COMD),
            ],
        )

        procedure_no_perim = ProcedureFactory()  # excluded because no perimeter
        procedure_multi_perim = ProcedureFactory(  # excluded because perimeter != 1
            with_perimetre=[commune, CommuneFactory(code_insee="30033")],
        )

        out = StringIO()
        call_command(
            "list_inconsistencies_procedure_collectivite_porteuse_invalid",
            "--wet-run",
            stdout=out,
        )
        expected = f"""procedure_id,procedure.collectivite_porteuse_id,perimetre.collectivite_code
{procedure.id},{procedure.collectivite_porteuse_id},{commune.code_insee_unique}
{procedure_comd.id},{procedure_comd.collectivite_porteuse_id},{commune.code_insee_unique}
"""
        assert expected == out.getvalue()

        procedure.refresh_from_db()
        assert procedure.collectivite_porteuse_id == commune.code_insee_unique

        procedure_comd.refresh_from_db()
        assert procedure_comd.collectivite_porteuse_id == commune.code_insee_unique

        previous_id = procedure_no_perim.collectivite_porteuse_id
        procedure_no_perim.refresh_from_db()
        assert procedure_no_perim.collectivite_porteuse_id == previous_id

        previous_id = procedure_multi_perim.collectivite_porteuse_id
        procedure_multi_perim.refresh_from_db()
        assert procedure_multi_perim.collectivite_porteuse_id == previous_id
