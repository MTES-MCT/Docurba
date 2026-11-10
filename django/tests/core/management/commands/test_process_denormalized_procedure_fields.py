import csv
import uuid
from io import StringIO

import pytest
from django.core.management import call_command
from pytest_django import DjangoAssertNumQueries

from docurba.core import enums as core_enums
from docurba.core.models import Procedure
from tests.core.factories import (
    CollectiviteFactory,
    CommuneFactory,
    CommuneProcedureFactory,
    ProcedureFactory,
)


@pytest.mark.django_db
class TestProcessDenormalizedProcedureFields:
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
        # Skip the save
        Procedure.objects.bulk_create(
            Procedure(
                id=uid,
                base_doc_type=core_enums.BaseDocumentType.PLU,
                vaut_PDM=True,
            )
            for uid in [
                uuid.UUID("fb48c069-33c6-4ed2-9db3-054e99ea7981"),
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

        assert caplog.messages[-1] == "1 inconsistent procedures"

        # Update mode
        call_command("process_denormalized_procedure_fields", mode="update")
        output = capsys.readouterr()

        reader = csv.DictReader(StringIO(output.out), delimiter=",")
        first_line = next(reader)
        assert reader.line_num == 2
        assert first_line == expected_csv
        assert caplog.messages[-1] == "1 inconsistent procedures"

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
