from datetime import date
from io import StringIO

import pytest
from django.core.management import call_command
from freezegun import freeze_time
from pytest_django import DjangoAssertNumQueries

from docurba.core.enums import ProcedureStatusChoices
from docurba.core.models import Event, Procedure
from tests.core.factories import EventFactory, EventTypeFactory, ProcedureFactory


@pytest.mark.django_db
class TestUpdateProcedureStatus:
    def _event_avec_impact(
        self,
        procedure: Procedure,
        impact: ProcedureStatusChoices,
        *,
        date_evenement: date,
    ) -> Event:
        event_type = EventTypeFactory(
            name=f"Type {impact} {date_evenement}", impact=impact
        )
        return EventFactory(
            procedure=procedure,
            event_type=event_type,
            date_evenement=date_evenement,
        )

    def test_statuts_identiques_non_exportes(self) -> None:
        procedure = ProcedureFactory(status=ProcedureStatusChoices.EN_COURS)

        out = StringIO()
        call_command("update_procedure_status", wet_run=False, stdout=out)

        assert out.getvalue() == "procedure_id,ancien_status,nouveau_status\n"

        procedure.refresh_from_db()
        assert procedure.status == ProcedureStatusChoices.EN_COURS

    def test_statut_different_exporte_et_mis_a_jour_avec_wet_run(self) -> None:
        procedure_differente = ProcedureFactory(status=ProcedureStatusChoices.OPPOSABLE)
        self._event_avec_impact(
            procedure_differente,
            ProcedureStatusChoices.ANNULE,
            date_evenement=date(2024, 6, 1),
        )
        # Cette procédure n'est pas exportée car son statut est déjà à jour.
        ProcedureFactory(status=ProcedureStatusChoices.EN_COURS)

        expected_csv = (
            "procedure_id,ancien_status,nouveau_status\n"
            f"{procedure_differente.id},opposable,annule\n"
        )

        out = StringIO()
        call_command("update_procedure_status", wet_run=False, stdout=out)

        assert expected_csv == out.getvalue()
        procedure_differente.refresh_from_db()
        assert procedure_differente.status == ProcedureStatusChoices.OPPOSABLE

        out = StringIO()
        call_command("update_procedure_status", wet_run=True, stdout=out)

        assert expected_csv == out.getvalue()
        procedure_differente.refresh_from_db()
        assert procedure_differente.status == ProcedureStatusChoices.ANNULE

    def test_procedure_secondaire_ignoree(self) -> None:
        # La procédure secondaire aurait un statut différent du calcul, mais
        # elle est ignorée par la commande.
        procedure = ProcedureFactory(
            status=ProcedureStatusChoices.OPPOSABLE,
            with_parente=True,
            parente__status=ProcedureStatusChoices.EN_COURS,
        )
        self._event_avec_impact(
            procedure,
            ProcedureStatusChoices.ANNULE,
            date_evenement=date(2024, 6, 1),
        )

        out = StringIO()
        call_command("update_procedure_status", wet_run=True, stdout=out)

        assert out.getvalue() == "procedure_id,ancien_status,nouveau_status\n"
        procedure.refresh_from_db()
        assert procedure.status == ProcedureStatusChoices.OPPOSABLE

    @pytest.mark.django_db
    @freeze_time("2026-10-15")
    def test_evenement_futur_ignore(self) -> None:
        # La commande passe la date du jour comme date_pivot : l'évènement
        # futur n'impacte pas le calcul, le statut est déjà à jour.
        procedure = ProcedureFactory(status=ProcedureStatusChoices.EN_COURS)
        self._event_avec_impact(
            procedure,
            ProcedureStatusChoices.OPPOSABLE,
            date_evenement=date(2026, 12, 1),
        )

        out = StringIO()
        call_command("update_procedure_status", wet_run=True, stdout=out)

        assert out.getvalue() == "procedure_id,ancien_status,nouveau_status\n"
        procedure.refresh_from_db()
        assert procedure.status == ProcedureStatusChoices.EN_COURS

    @pytest.mark.django_db
    def test_wet_run_mise_a_jour_en_un_seul_bulk(
        self, django_assert_num_queries: DjangoAssertNumQueries
    ) -> None:
        procedures = [
            ProcedureFactory(status=ProcedureStatusChoices.OPPOSABLE) for _ in range(3)
        ]
        for index, procedure in enumerate(procedures):
            self._event_avec_impact(
                procedure,
                ProcedureStatusChoices.ANNULE,
                date_evenement=date(2024, 6, 1 + index),
            )

        out = StringIO()
        # 1 requête pour les procédures + 1 pour le prefetch + 1 seul UPDATE.
        with django_assert_num_queries(3):
            call_command("update_procedure_status", wet_run=True, stdout=out)

        for procedure in procedures:
            procedure.refresh_from_db()
            assert procedure.status == ProcedureStatusChoices.ANNULE
