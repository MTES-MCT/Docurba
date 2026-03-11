import csv
from pathlib import Path

import pytest
from django.core.management import call_command
from pytest_django.fixtures import SettingsWrapper

from docurba.core.models import Procedure, Topic


@pytest.mark.django_db
class TestMigrateProceduretopics:
    @pytest.mark.parametrize(
        (
            "commentaire",
            "topic_column_name_in_csv",
            "expected_created_topics",
            "other_topic_comment",
        ),
        [
            pytest.param("Trajectoire ZAN", ["objet_zan"], ["zan"], "", id="zan"),
            pytest.param(
                "Zones d'accélération ENR", ["objet_enr"], ["enr"], "", id="enr"
            ),
            pytest.param(
                "Trait de côte",
                ["objet_trait_de_cote"],
                ["coastline"],
                "",
                id="trait_de_cote",
            ),
            pytest.param(
                "Feu de forêt",
                ["objet_feu_de_foret"],
                ["forest_fire"],
                "",
                id="feu_de_foret",
            ),
            pytest.param(
                "Feu de forêt, Trait de côte",
                ["objet_feu_de_foret", "objet_trait_de_cote"],
                ["forest_fire", "coastline"],
                "",
                id="two_topics",
            ),
            pytest.param(
                "Autre - -> Ouvrir à l'urbanisation dix zones classées en XXX / Création et modification d'OAP afin d'encadrer l'urbanisation de certains secteurs en zone urbaine /Modification du plan de zonage --> Évolution du règlement écrit (clôtures, piscines, ...) ",
                ["objet_autre"],
                ["other"],
                "-> Ouvrir à l'urbanisation dix zones classées en XXX / Création et modification d'OAP afin d'encadrer l'urbanisation de certains secteurs en zone urbaine /Modification du plan de zonage --> Évolution du règlement écrit (clôtures, piscines, ...)",
                id="other_topic",
            ),
            pytest.param(
                "Trajectoire ZAN, Zones d'accélération ENR, Autre - Révision générale du PLU d'Aramon",
                ["objet_zan", "objet_enr", "objet_autre"],
                ["zan", "enr", "other"],
                "Révision générale du PLU d'Aramon",
                id="zan_enr_and_other",
            ),
        ],
    )
    def test_call_command_simple_case(  # noqa: PLR0913
        self,
        capsys: pytest.CaptureFixture[str],
        settings: SettingsWrapper,
        tmp_path: Path,
        commentaire: str,
        topic_column_name_in_csv: list,
        expected_created_topics: str,
        other_topic_comment: str,
    ) -> None:
        settings.EXPORTS_DIR = tmp_path

        procedure = Procedure.objects.create(
            commentaire=commentaire,
        )
        topics = Topic.objects.filter(name__in=expected_created_topics)
        # Assert null comments are not taken into account.
        Procedure.objects.create(commentaire=None)
        # Assert blank comments are not taken into account.
        Procedure.objects.create(commentaire="")

        call_command("migrate_procedure_topics", wet_run=True)
        stdout, _ = capsys.readouterr()
        csv_topics_column_names = [
            "objet_enr",
            "objet_trait_de_cote",
            "objet_zan",
            "objet_feu_de_foret",
            "objet_autre",
        ]
        csv_topic_col_names = {
            csv_col: "True" if csv_col in topic_column_name_in_csv else "False"
            for csv_col in csv_topics_column_names
        }

        with Path.open(
            Path(settings.EXPORTS_DIR) / "updated_procedure_topics.csv"
        ) as csvfile:
            results = list(csv.DictReader(csvfile, delimiter=";"))
            assert len(results) == 1
            row = results[0]
            assert row["ancien_commentaire"] == commentaire
            assert row["nouveau_commentaire"] == ""
            assert row["objet_commentaire"] == other_topic_comment
            assert [row[col] == "True" for col in topic_column_name_in_csv]
            for col_name, col_value in csv_topic_col_names.items():
                assert row[col_name] == col_value

            assert row["procedure_id"] == str(procedure.pk)

        stdout_formatted = stdout.splitlines()[:3]
        assert stdout_formatted == [
            "Results to process: 1",
            f"Added procedures topics: {len(topics)}",
            "Updated procedures: 1",
        ]

        assert Procedure.objects.filter(commentaire="").count() == 2
        procedure.refresh_from_db()
        assert procedure.topics.count() == topics.count()
        assert sorted(procedure.topics.values_list("name", flat=True)) == sorted(
            expected_created_topics
        )
        if other_topic_comment:
            assert (
                procedure.topics_through.filter(topic__name="other").get().comment
                == other_topic_comment
            )
