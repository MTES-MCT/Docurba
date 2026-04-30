import pytest

from docurba.core.models import Procedure
from docurba.surveys.models import ProcedureSurvey, Survey
from tests.core.factories import CollectiviteFactory
from tests.users.factories import ProfileFactory


@pytest.mark.django_db
class TestSurveys:
    def test_fixtures(self) -> None:
        assert Survey.objects.count() == 1
        profile = ProfileFactory(other_poste=["rédacteur", "maire"])
        collectivite = CollectiviteFactory()
        survey = Survey.objects.filter(name="zan_03_2026").first()
        procedure = Procedure.objects.create()
        ProcedureSurvey.objects.create(
            survey=survey,
            procedure=procedure,
            respondant=profile,
            collectivite_code=collectivite,
        )
        assert procedure.surveys_answers.count() == 1
        assert profile.surveys_answers.count() == 1
        assert survey.procedures_through.count() == 1
