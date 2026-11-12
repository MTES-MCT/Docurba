import csv
import uuid
from datetime import timedelta
from io import StringIO

import pytest
from django.core.management import call_command
from django.utils import timezone
from pytest_django import DjangoAssertNumQueries

from docurba.core import enums as core_enums
from docurba.core.models import Commune, Procedure
from tests.core.factories import (
    CollectiviteFactory,
    CommuneFactory,
    CommuneProcedureFactory,
    ProcedureFactory,
)


@pytest.mark.django_db
class TestProcessDenormalizedProcedureFields:
    def _create_inconsistent_procedure(
        self, communes: list[Commune], params: dict | None = None
    ) -> Procedure:
        now = timezone.now()
        yesterday = now - timedelta(days=1)
        params = {"created_at": yesterday} | params
        # Skip the save
        [procedure] = Procedure.objects.bulk_create(
            Procedure(
                base_doc_type=core_enums.BaseDocumentType.PLU,
                vaut_PDM=True,
                **params,
            )
            for _ in range(1)
        )
        # Because of some denormalized fields in CommuneProcedure,
        # we can't do procedure.perimetre.add(*communes)
        for commune in communes:
            CommuneProcedureFactory(procedure=procedure, commune=commune)
        return procedure

    def test_call_command__no_procedure(
        self,
        caplog: pytest.LogCaptureFixture,
        capsys: pytest.LogCaptureFixture,
    ) -> None:
        ProcedureFactory(base_doc_type=core_enums.BaseDocumentType.PLU, vaut_PDM=True)

        call_command("process_denormalized_procedure_fields")
        output = capsys.readouterr()

        # No procedure to update
        expected_csv = "procedure_id,dynamic_doc_type,doc_type\n"
        assert expected_csv == output.out
        assert caplog.messages[-1] == "0 inconsistent procedures"

    def test_call_command__inconsistent_procedures(
        self,
        caplog: pytest.LogCaptureFixture,
        capsys: pytest.LogCaptureFixture,
    ) -> None:
        communes = [
            CommuneFactory(code_insee="30188", code_insee_unique="30188"),
            CommuneFactory(code_insee="30189", code_insee_unique="30189"),
        ]
        self._create_inconsistent_procedure(
            communes=communes,
            params={"id": uuid.UUID("fb48c069-33c6-4ed2-9db3-054e99ea7981")},
        )

        expected_csv = {
            "procedure_id": "fb48c069-33c6-4ed2-9db3-054e99ea7981",
            "doc_type": "",
            "dynamic_doc_type": "PLUiM",
        }

        # Check by default.
        call_command("process_denormalized_procedure_fields")
        output = capsys.readouterr()

        reader = csv.DictReader(StringIO(output.out), delimiter=",")
        first_line = next(reader)
        assert reader.line_num == 2
        assert first_line == expected_csv

        procedure = Procedure.objects.get(pk="fb48c069-33c6-4ed2-9db3-054e99ea7981")
        assert procedure.doc_type is None

        assert caplog.messages[-1] == "[TEST] 1 inconsistent procedures"

        # Update mode
        call_command("process_denormalized_procedure_fields", mode="update")
        output = capsys.readouterr()

        reader = csv.DictReader(StringIO(output.out), delimiter=",")
        first_line = next(reader)
        assert reader.line_num == 2
        assert first_line == expected_csv
        assert caplog.messages[-2] == "=============================\nSlack message:"
        assert caplog.messages[-1] == "[TEST] 1 inconsistent procedures"

        procedure = Procedure.objects.get(pk="fb48c069-33c6-4ed2-9db3-054e99ea7981")
        assert procedure.doc_type == core_enums.TypeDocument.PLUIM

    def test_assert_num_queries(
        self, django_assert_num_queries: DjangoAssertNumQueries
    ) -> None:
        collectivite_porteuse = CollectiviteFactory()
        Procedure.objects.bulk_create(
            Procedure(
                id=uid,
                base_doc_type=core_enums.BaseDocumentType.PLU,
                vaut_PDM=True,
                created_at=timezone.now() - timedelta(days=1),
                collectivite_porteuse=collectivite_porteuse,
            )
            for uid in [
                uuid.UUID("fb48c069-33c6-4ed2-9db3-054e99ea7981"),
                uuid.UUID("fb48c069-33c6-4ed2-9db3-054e99ea7982"),
                uuid.UUID("fb48c069-33c6-4ed2-9db3-054e99ea7983"),
                uuid.UUID("fb48c069-33c6-4ed2-9db3-054e99ea7984"),
            ]
        )
        communes = [
            CommuneFactory(code_insee="30188", code_insee_unique="30188"),
            CommuneFactory(code_insee="30189", code_insee_unique="30189"),
        ]
        # Because of some denormalized fields in CommuneProcedure,
        # we can't do procedure.perimetre.add(*communes)
        for procedure in Procedure.objects.all():
            for commune in communes:
                CommuneProcedureFactory(procedure=procedure, commune=commune)
        # add perimetre
        with django_assert_num_queries(
            1  # get procedures's pk
            + 1  # batch qs
            + 1  # prefetch perimetre
        ):
            call_command("process_denormalized_procedure_fields")

        with django_assert_num_queries(
            1  # get procedures's pk
            + 1  # batch qs
            + 1  # prefetch perimetre
            + 1  # transaction savepoint
            + 1  # update
            + 1  # release transaction savepoint
        ):
            call_command("process_denormalized_procedure_fields", mode="update")

        for procedure in Procedure.objects.all():
            assert procedure.doc_type == core_enums.TypeDocument.PLUIM

    def test_ignored_procedures(self, caplog: pytest.LogCaptureFixture) -> None:
        now = timezone.now()
        yesterday_dt = now - timedelta(days=1)
        communes = [
            CommuneFactory(code_insee="30188", code_insee_unique="30188"),
            CommuneFactory(code_insee="30189", code_insee_unique="30189"),
        ]
        # Created two days ago
        procedure = self._create_inconsistent_procedure(
            communes=communes,
            params={
                "created_at": yesterday_dt - timedelta(days=2),
            },
        )

        call_command("process_denormalized_procedure_fields")
        assert caplog.messages[-1] == "0 inconsistent procedures"
        procedure.delete()

        # Updated more than 24h ago.
        procedure = self._create_inconsistent_procedure(
            communes=communes,
            params={
                "created_at": yesterday_dt - timedelta(days=1),
                "last_updated_at": yesterday_dt - timedelta(days=1),
            },
        )
        call_command("process_denormalized_procedure_fields")
        assert caplog.messages[-1] == "0 inconsistent procedures"
        procedure.delete()

        # Created less than 24h.
        procedure = self._create_inconsistent_procedure(
            communes=communes,
            params={
                "created_at": yesterday_dt,
                "last_updated_at": now,
            },
        )
        call_command("process_denormalized_procedure_fields")
        assert caplog.messages[-1] == "[TEST] 1 inconsistent procedures"
        procedure.delete()

        # Updated less than 24h.
        procedure = self._create_inconsistent_procedure(
            communes=communes,
            params={
                "created_at": yesterday_dt - timedelta(days=1),
                "last_updated_at": yesterday_dt,
            },
        )
        call_command("process_denormalized_procedure_fields")
        assert caplog.messages[-1] == "[TEST] 1 inconsistent procedures"
        procedure.delete()

        # Created today
        procedure = self._create_inconsistent_procedure(
            communes=communes,
            params={
                "created_at": now,
            },
        )
        call_command("process_denormalized_procedure_fields")
        assert caplog.messages[-1] == "0 inconsistent procedures"
        procedure.delete()

        # Updated today
        procedure = self._create_inconsistent_procedure(
            communes=communes,
            params={
                "created_at": yesterday_dt - timedelta(days=1),
                "last_updated_at": now,
            },
        )
        call_command("process_denormalized_procedure_fields")
        assert caplog.messages[-1] == "0 inconsistent procedures"
        procedure.delete()
