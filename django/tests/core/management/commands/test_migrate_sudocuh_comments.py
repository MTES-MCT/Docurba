import csv
from pathlib import Path

import pytest
from django.core.management import call_command
from pytest_django.fixtures import SettingsWrapper

from docurba.core.models import Procedure


@pytest.mark.django_db
class TestMigrateSudocuhComments:
    def _assert_csv_output(self, filepath: Path) -> None:
        with Path.open(filepath) as csvfile:
            results = list(csv.DictReader(csvfile, delimiter=";"))
            assert len(results) == 4
            row = results[0]
            assert row["ancien_commentaire"] == "0 Un commentaire très intéressant."
            assert (
                row["nouveau_commentaire_sudocuh"]
                == "0 Un commentaire très intéressant."
            )
            assert row["nouveau_commentaire"] == ""
            assert row["from_sudocuh_id"] == "0"

    def _assert_stdout(self, stdout) -> None:  # noqa: ANN001
        stdout_formatted = stdout.splitlines()[:2]
        assert stdout_formatted == [
            "Results to process: 4",
            "Updated procedures: 4",
        ]

    def test_call_command_dry_run(
        self,
        capsys: pytest.CaptureFixture[str],
        settings: SettingsWrapper,
        tmp_path: Path,
    ) -> None:
        settings.EXPORTS_DIR = tmp_path
        filepath = Path(settings.EXPORTS_DIR) / "sudocuh_comments.csv"
        for i in range(4):
            Procedure.objects.create(
                commentaire=f"{i} Un commentaire très intéressant.", from_sudocuh=i
            )
        # Assert null comments are not taken into account.
        Procedure.objects.create(commentaire=None, from_sudocuh=5)
        # Assert blank comments are not taken into account.
        Procedure.objects.create(commentaire="", from_sudocuh=6)

        call_command("migrate_sudocuh_comments", wet_run=False)
        stdout, _ = capsys.readouterr()
        self._assert_csv_output(filepath=filepath)
        self._assert_stdout(stdout)
        assert Procedure.objects.filter(commentaire__isnull=False).count() == 5
        assert Procedure.objects.filter(comment_from_sudocuh="").count() == 6

    def test_call_command_wet_run(
        self,
        capsys: pytest.CaptureFixture[str],
        settings: SettingsWrapper,
        tmp_path: Path,
    ) -> None:
        settings.EXPORTS_DIR = tmp_path
        filepath = Path(settings.EXPORTS_DIR) / "sudocuh_comments.csv"
        for i in range(4):
            Procedure.objects.create(
                commentaire=f"{i} Un commentaire très intéressant.", from_sudocuh=i
            )

        call_command("migrate_sudocuh_comments", wet_run=True)
        stdout, _ = capsys.readouterr()
        self._assert_csv_output(filepath=filepath)
        self._assert_stdout(stdout)
        assert Procedure.objects.filter(commentaire="").count() == 4
        assert Procedure.objects.filter(comment_from_sudocuh="").count() == 0
