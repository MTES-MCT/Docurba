from datetime import timedelta
from io import StringIO

import pytest
from django.core.management import call_command
from django.utils import timezone
from freezegun import freeze_time

from docurba.core.enums import ProcedureStatusChoices
from tests.core.factories import (
    CommuneFactory,
    EventFactory,
    ProcedureFactory,
)


@pytest.mark.django_db
class TestUpdateCommuneProcedureOpposability:
    def test_matching_opposability_not_exported(self) -> None:
        commune = CommuneFactory()
        procedure = ProcedureFactory(
            collectivite_porteuse=commune,
            with_perimetre=[commune],
        )
        EventFactory(
            procedure=procedure,
            event_type__impact=ProcedureStatusChoices.OPPOSABLE,
        )
        perimetre_line = procedure.perimetre_through.get()
        perimetre_line.opposable = True
        perimetre_line.save(update_fields=["opposable"])

        out = StringIO()
        call_command("update_commune_procedure_opposability", wet_run=False, stdout=out)

        assert out.getvalue() == "commune_procedure_id,old_opposable,new_opposable\n"

        perimetre_line.refresh_from_db()
        assert perimetre_line.opposable is True

    def test_differing_opposability_exported_and_updated_with_wet_run(self) -> None:
        commune = CommuneFactory()
        procedure = ProcedureFactory(
            collectivite_porteuse=commune,
            with_perimetre=[commune],
        )
        EventFactory(
            procedure=procedure,
            event_type__impact=ProcedureStatusChoices.OPPOSABLE,
        )
        # This perimetre line is not exported because its opposability is
        # already up to date.
        other_commune = CommuneFactory()
        other_procedure = ProcedureFactory(
            collectivite_porteuse=other_commune,
            with_perimetre=[other_commune],
        )
        EventFactory(
            procedure=other_procedure,
            event_type__impact=ProcedureStatusChoices.OPPOSABLE,
        )
        other_perimetre_line = other_procedure.perimetre_through.get()
        other_perimetre_line.opposable = True
        other_perimetre_line.save(update_fields=["opposable"])

        perimetre_line = procedure.perimetre_through.get()
        expected_csv = (
            "commune_procedure_id,old_opposable,new_opposable\n"
            f"{perimetre_line.id},False,True\n"
        )

        out = StringIO()
        call_command("update_commune_procedure_opposability", wet_run=False, stdout=out)

        assert expected_csv == out.getvalue()
        perimetre_line.refresh_from_db()
        assert perimetre_line.opposable is False

        out = StringIO()
        call_command("update_commune_procedure_opposability", wet_run=True, stdout=out)

        assert expected_csv == out.getvalue()
        perimetre_line.refresh_from_db()
        assert perimetre_line.opposable is True

    @freeze_time("2026-10-15")
    def test_outdated_opposable_reset_with_wet_run(self) -> None:
        # Historically flagged as opposable by Nuxt, but the last impactful
        # event is no longer opposable.
        now = timezone.now()
        commune = CommuneFactory()
        procedure = ProcedureFactory(
            collectivite_porteuse=commune,
            with_perimetre=[commune],
        )
        EventFactory(
            procedure=procedure,
            event_type__impact=ProcedureStatusChoices.OPPOSABLE,
            date_evenement=now - timedelta(days=30),
        )
        EventFactory(
            procedure=procedure,
            event_type__impact=ProcedureStatusChoices.ANNULE,
            date_evenement=now,
        )
        perimetre_line = procedure.perimetre_through.get()
        perimetre_line.opposable = True
        perimetre_line.save(update_fields=["opposable"])

        expected_csv = (
            "commune_procedure_id,old_opposable,new_opposable\n"
            f"{perimetre_line.id},True,False\n"
        )

        out = StringIO()
        call_command("update_commune_procedure_opposability", wet_run=False, stdout=out)

        assert expected_csv == out.getvalue()
        perimetre_line.refresh_from_db()
        assert perimetre_line.opposable is True

        out = StringIO()
        call_command("update_commune_procedure_opposability", wet_run=True, stdout=out)

        assert expected_csv == out.getvalue()
        perimetre_line.refresh_from_db()
        assert perimetre_line.opposable is False

    def test_secondary_procedure_line_reset_with_wet_run(self) -> None:
        # A secondary procedure can never be opposable: its perimetre lines
        # are reset, while the primary procedure keeps its opposability.
        commune = CommuneFactory()
        procedure_secondaire = ProcedureFactory(
            collectivite_porteuse=commune,
            with_perimetre=[commune],
            with_parente=True,
            parente__with_perimetre=[commune],
        )
        EventFactory(
            procedure=procedure_secondaire,
            event_type__impact=ProcedureStatusChoices.OPPOSABLE,
        )
        procedure_principale = procedure_secondaire.parente
        EventFactory(
            procedure=procedure_principale,
            event_type__impact=ProcedureStatusChoices.OPPOSABLE,
        )
        for procedure in (procedure_secondaire, procedure_principale):
            perimetre_line = procedure.perimetre_through.get()
            perimetre_line.opposable = True
            perimetre_line.save(update_fields=["opposable"])

        out = StringIO()
        call_command("update_commune_procedure_opposability", wet_run=True, stdout=out)

        secondary_line = procedure_secondaire.perimetre_through.get()
        primary_line = procedure_principale.perimetre_through.get()
        expected_csv = (
            "commune_procedure_id,old_opposable,new_opposable\n"
            f"{secondary_line.id},True,False\n"
        )
        assert expected_csv == out.getvalue()
        secondary_line.refresh_from_db()
        primary_line.refresh_from_db()
        assert secondary_line.opposable is False
        assert primary_line.opposable is True
