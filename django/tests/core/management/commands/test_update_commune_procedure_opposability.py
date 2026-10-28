from datetime import date
from io import StringIO
from uuid import uuid4

import pytest
from django.core.management import call_command
from pytest_django import DjangoAssertNumQueries

from docurba.core.enums import ProcedureStatusChoices
from docurba.core.models import Commune, Event, Procedure
from tests.core.factories import (
    CommuneFactory,
    EventFactory,
    EventTypeFactory,
    ProcedureFactory,
)


@pytest.mark.django_db
class TestUpdateCommuneProcedureOpposability:
    def _create_impactful_event(
        self,
        procedure: Procedure,
        impact: ProcedureStatusChoices,
        *,
        date_evenement: date,
    ) -> Event:
        # The uuid suffix prevents unique constraint violations when several
        # events share the same date and impact.
        event_type = EventTypeFactory(
            name=f"Type {impact} {date_evenement} {uuid4().hex[:8]}", impact=impact
        )
        return EventFactory(
            procedure=procedure,
            event_type=event_type,
            date_evenement=date_evenement,
        )

    def _create_procedure_on_commune(
        self, commune: Commune, **kwargs: dict
    ) -> Procedure:
        return ProcedureFactory(
            collectivite_porteuse=commune,
            with_perimetre=[commune],
            **kwargs,
        )

    def test_matching_opposability_not_exported(self) -> None:
        commune = CommuneFactory()
        procedure = self._create_procedure_on_commune(commune)
        self._create_impactful_event(
            procedure,
            ProcedureStatusChoices.OPPOSABLE,
            date_evenement=date(2025, 1, 1),
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
        procedure = self._create_procedure_on_commune(commune)
        self._create_impactful_event(
            procedure,
            ProcedureStatusChoices.OPPOSABLE,
            date_evenement=date(2025, 1, 1),
        )
        # This perimetre line is not exported because its opposability is
        # already up to date.
        other_commune = CommuneFactory()
        other_procedure = self._create_procedure_on_commune(other_commune)
        self._create_impactful_event(
            other_procedure,
            ProcedureStatusChoices.OPPOSABLE,
            date_evenement=date(2024, 6, 1),
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

    def test_outdated_opposable_reset_with_wet_run(self) -> None:
        # Historically flagged as opposable by Nuxt, but the last impactful
        # event is no longer opposable.
        commune = CommuneFactory()
        procedure = self._create_procedure_on_commune(commune)
        self._create_impactful_event(
            procedure,
            ProcedureStatusChoices.OPPOSABLE,
            date_evenement=date(2024, 6, 1),
        )
        self._create_impactful_event(
            procedure,
            ProcedureStatusChoices.ANNULE,
            date_evenement=date(2025, 1, 1),
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
        procedure_secondaire = self._create_procedure_on_commune(
            commune,
            with_parente=True,
            parente__with_perimetre=[commune],
        )
        self._create_impactful_event(
            procedure_secondaire,
            ProcedureStatusChoices.OPPOSABLE,
            date_evenement=date(2025, 6, 1),
        )
        procedure_principale = procedure_secondaire.parente
        self._create_impactful_event(
            procedure_principale,
            ProcedureStatusChoices.OPPOSABLE,
            date_evenement=date(2024, 6, 1),
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

    def test_wet_run_updates_in_a_single_bulk(
        self, django_assert_num_queries: DjangoAssertNumQueries
    ) -> None:
        for _ in range(3):
            commune = CommuneFactory()
            procedure = self._create_procedure_on_commune(commune)
            self._create_impactful_event(
                procedure,
                ProcedureStatusChoices.OPPOSABLE,
                date_evenement=date(2025, 1, 1),
            )

        out = StringIO()
        # 1 query for communes + 2 for the prefetches + a single UPDATE.
        with django_assert_num_queries(4):
            call_command(
                "update_commune_procedure_opposability", wet_run=True, stdout=out
            )

        for procedure in Procedure.objects.all():
            assert procedure.perimetre_through.get().opposable is True
