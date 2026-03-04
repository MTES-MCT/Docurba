import csv
from pathlib import Path

import pytest
from django.core.management import call_command
from pytest_django.fixtures import SettingsWrapper

from docurba.core.models import Procedure, Topic


@pytest.mark.django_db
class TestMigrateProceduretopics:
    # def _assert_stdout(self, stdout) -> None:  # noqa: ANN001
    #     stdout_formatted = stdout.splitlines()[:2]
    #     assert stdout_formatted == [
    #         "Results to process: 4",
    #         "Updated procedures: 4",
    #     ]

    def test_call_command_simple_case(
        self,
        capsys: pytest.CaptureFixture[str],
        settings: SettingsWrapper,
        tmp_path: Path,
    ) -> None:
        settings.EXPORTS_DIR = tmp_path

        zan_topic = Topic.objects.get(name="zan")
        procedure = Procedure.objects.create(
            commentaire=zan_topic.display_name,
        )
        # Assert null comments are not taken into account.
        Procedure.objects.create(commentaire=None)
        # Assert blank comments are not taken into account.
        Procedure.objects.create(commentaire="")

        call_command("migrate_procedure_topics", wet_run=True)
        stdout, _ = capsys.readouterr()

        with Path.open(
            Path(settings.EXPORTS_DIR) / "updated_procedure_topics.csv"
        ) as csvfile:
            results = list(csv.DictReader(csvfile, delimiter=";"))
            assert len(results) == 1
            row = results[0]
            assert row["ancien_commentaire"] == zan_topic.display_name
            assert row["nouveau_commentaire"] == ""
            assert row["objet_autre"] == "False"
            assert row["objet_trait_de_cote"] == "False"
            assert row["objet_enr"] == "False"
            assert row["objet_zan"] == "True"
            assert row["objet_feu_foret"] == "False"
            assert row["procedure_id"] == str(procedure.pk)

        # self._assert_stdout(stdout)
        assert Procedure.objects.filter(commentaire="").count() == 2
        procedure.refresh_from_db()
        assert procedure.topics.count() == 1
        assert procedure.topics.first().name == "zan"

    # TESTS:
    # Two objects
    # Only other
    # Two objects and other
