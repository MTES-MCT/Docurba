from io import StringIO

import pytest
from django.core.management import call_command

from docurba.core.enums import ProcedureStatusChoices
from docurba.core.models import Procedure
from tests.core.factories import ProcedureFactory


@pytest.mark.django_db
class TestResetSecondaryProcedureStatus:
    def test_secondary_with_status_exported_and_nullified(self) -> None:
        principale = ProcedureFactory()
        # We are going through an update here to bypass the new validation rules in Procedure.clean
        secondaire = ProcedureFactory(parente=principale, status=None)
        Procedure.objects.filter(id=secondaire.id).update(
            status=ProcedureStatusChoices.OPPOSABLE
        )

        expected_csv = (
            "procedure_id,procedure.status\n"
            f"{secondaire.id},{ProcedureStatusChoices.OPPOSABLE}\n"
        )

        out = StringIO()
        call_command("reset_secondary_procedure_status", wet_run=False, stdout=out)

        assert expected_csv == out.getvalue()

        secondaire.refresh_from_db()
        assert secondaire.status == ProcedureStatusChoices.OPPOSABLE

        out = StringIO()
        call_command("reset_secondary_procedure_status", wet_run=True, stdout=out)

        assert expected_csv == out.getvalue()

        secondaire.refresh_from_db()
        assert secondaire.status is None

    def test_others_procedures_ignored(self) -> None:
        principale = ProcedureFactory(status=ProcedureStatusChoices.EN_COURS)
        secondaire_sans_status = ProcedureFactory(parente=principale, status=None)

        expected_csv = "procedure_id,procedure.status\n"

        out = StringIO()
        call_command("reset_secondary_procedure_status", wet_run=False, stdout=out)

        assert expected_csv == out.getvalue()

        out = StringIO()
        call_command("reset_secondary_procedure_status", wet_run=True, stdout=out)

        assert expected_csv == out.getvalue()

        principale.refresh_from_db()
        secondaire_sans_status.refresh_from_db()
        assert principale.status == ProcedureStatusChoices.EN_COURS
        assert secondaire_sans_status.status is None
