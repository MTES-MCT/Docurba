from io import StringIO

import pytest
from django.core.management import call_command

from docurba.core.enums import ProcedureStatusChoices
from docurba.core.models import Procedure
from tests.core.factories import ProcedureFactory


@pytest.mark.django_db
class TestResetSecondaryProcedureStatus:
    def test_secondaire_avec_status_exportee_et_nullifiee(self) -> None:
        principale = ProcedureFactory()
        # Nous passons par un update ici pour contourner les nouvelles règles de validation dans Procedure.clean
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

    def test_autres_procedures_ignorees(self) -> None:
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
