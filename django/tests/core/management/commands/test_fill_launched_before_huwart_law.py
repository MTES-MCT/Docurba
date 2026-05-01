import datetime

import pytest
from django.core.management import call_command

from docurba.core.constants import HUWART_LAW_DATE
from docurba.core.enums import ProcedureType
from docurba.core.models import Procedure
from tests.core.factories import EventFactory, ProcedureFactory


@pytest.mark.django_db
class TestFillStartedBeforeHuwartLaw:
    def test_call_command_wet_run(
        self,
    ) -> None:
        procedure = ProcedureFactory(type=ProcedureType.MODIFICATION)
        procedure.event_set.add(
            EventFactory(
                type="Arrêté de lancement de la procédure",
                date_evenement=HUWART_LAW_DATE - datetime.timedelta(days=1),
            )
        )
        procedure_from_sudocuh = ProcedureFactory(from_sudocuh="1234567")
        procedure_who_started_after = ProcedureFactory(type=ProcedureType.MODIFICATION)
        procedure_who_started_after.event_set.add(
            EventFactory(
                type="Arrêté de lancement de la procédure",
                date_evenement=HUWART_LAW_DATE + datetime.timedelta(days=1),
            )
        )
        ProcedureFactory(type=ProcedureType.ELABORATION)

        call_command("fill_started_before_huwart_law", wet_run=True)

        assert Procedure.objects.filter(started_before_huwart_law=True).count() == 2
        procedure.refresh_from_db()
        procedure_from_sudocuh.refresh_from_db()
        procedure_who_started_after.refresh_from_db()
        assert procedure.started_before_huwart_law is True
        assert procedure_from_sudocuh.started_before_huwart_law is True
        assert procedure_who_started_after.started_before_huwart_law is False
