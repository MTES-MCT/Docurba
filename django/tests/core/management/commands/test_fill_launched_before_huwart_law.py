import datetime

import pytest
from django.core.management import call_command

from docurba.core.constants import HUWART_LAW_DATE
from docurba.core.enums import ProcedureType
from docurba.core.models import Procedure
from tests.core.factories import ProcedureFactory


@pytest.mark.django_db
class TestFillStartedBeforeHuwartLaw:
    def test_call_command_wet_run(
        self,
    ) -> None:
        procedure_who_started_before = ProcedureFactory(
            type=ProcedureType.MODIFICATION,
            with_event=True,
            with_event__type="Arrêté de lancement de la procédure",
            with_event__date_evenement=HUWART_LAW_DATE - datetime.timedelta(days=1),
        )

        procedure_without_event_before = ProcedureFactory(
            type=ProcedureType.MODIFICATION,
            last_updated_at=HUWART_LAW_DATE - datetime.timedelta(days=1),
        )
        procedure_without_event_after = ProcedureFactory(
            type=ProcedureType.MODIFICATION,
            last_updated_at=HUWART_LAW_DATE + datetime.timedelta(days=1),
        )

        procedure_from_sudocuh = ProcedureFactory(from_sudocuh="1234567")
        procedure_who_started_after = ProcedureFactory(
            type=ProcedureType.MODIFICATION,
            with_event=True,
            with_event__type="Arrêté de lancement de la procédure",
            with_event__date_evenement=HUWART_LAW_DATE + datetime.timedelta(days=1),
        )

        call_command("fill_started_before_huwart_law", wet_run=True)

        assert Procedure.objects.filter(started_before_huwart_law=True).count() == 4
        procedure_who_started_before.refresh_from_db()
        procedure_without_event_before.refresh_from_db()
        procedure_without_event_after.refresh_from_db()
        procedure_from_sudocuh.refresh_from_db()
        procedure_who_started_after.refresh_from_db()
        assert procedure_who_started_before.started_before_huwart_law is True
        assert procedure_without_event_before.started_before_huwart_law is True
        assert procedure_without_event_after.started_before_huwart_law is True
        assert procedure_from_sudocuh.started_before_huwart_law is True
        assert procedure_who_started_after.started_before_huwart_law is False
