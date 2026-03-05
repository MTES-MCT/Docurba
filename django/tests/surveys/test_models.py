import pytest

from docurba.core.models import Procedure
from docurba.surveys.models import ProcedureSurvey, Survey
from tests.users.factories import create_user_and_profile


@pytest.mark.django_db
class TestSurveys:
    def test_fixtures(self) -> None:
        assert Survey.objects.count() == 1
        _, profile = create_user_and_profile(
            email="georges-eugene@haussmann.com", other_poste=["rédacteur", "maire"]
        )
        survey = Survey.objects.filter(name="zan_03_2026").first()
        procedure = Procedure.objects.create()
        ProcedureSurvey.objects.create(
            survey=survey, procedure=procedure, respondant=profile
        )
        assert procedure.surveys_answers.count() == 1
        assert profile.surveys_answers.count() == 1
        assert survey.procedures_through.count() == 1
