import pytest
from django.core.management import call_command

from tests.core.factories import EventTypeFactory


@pytest.mark.django_db
class TestLinkEventsWithEventTypes:
    @pytest.mark.parametrize(
        (
            "initial_scope",
            "expected_scope",
        ),
        [
            pytest.param(
                ["pp", "ppi", "m", "ms"], ["pp", "ppi", "m", "ms", "pplh", "ppilh"]
            ),
            pytest.param(["pp", "m", "ms"], ["pp", "m", "ms", "pplh"]),
            pytest.param(["ppi", "m", "ms"], ["ppi", "m", "ms", "ppilh"]),
            pytest.param(
                ["pp", "ppi", "m", "ms", "pplh", "ppilh"],
                ["pp", "ppi", "m", "ms", "pplh", "ppilh"],
            ),
            pytest.param(["pp", "m", "ms", "pplh"], ["pp", "m", "ms", "pplh"]),
            pytest.param(["ppi", "m", "ms", "ppilh"], ["ppi", "m", "ms", "ppilh"]),
            pytest.param(["m", "ms", "pplh"], ["m", "ms", "pplh"]),
            pytest.param(["m", "ms", "ppilh"], ["m", "ms", "ppilh"]),
        ],
    )
    def test_call_command_add_scope(
        self,
        initial_scope: list[str],
        expected_scope: list[str],
    ) -> None:

        event_type = EventTypeFactory(
            scope_list=initial_scope,
            scope_sugg=initial_scope,
        )

        call_command("event_type_add_scope_pplh_ppilh")

        event_type.refresh_from_db()

        assert event_type.scope_list == expected_scope
        assert event_type.scope_sugg == expected_scope
