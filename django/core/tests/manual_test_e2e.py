import hashlib
import logging
from datetime import UTC, datetime, timedelta
from pathlib import Path
from urllib.request import urlretrieve

import polars as pl
import polars.testing
import pytest
from django.conf import settings
from django.db import connections
from django.test import Client
from environ import Env
from pytest_django import DjangoAssertNumQueries

from core.models import communes


# https://pytest-django.readthedocs.io/en/latest/database.html#using-an-existing-external-database-for-tests
# https://github.com/pytest-dev/pytest-django/issues/643
@pytest.fixture(scope="module")
def django_db_setup(django_db_modify_db_settings: None) -> None:
    # remove cached_property of connections.settings from the cache
    del connections.__dict__["settings"]

    settings.DATABASES["default"] = Env().db("PRODUCTION_DATABASE_URL")

    # re-configure the settings given the changed database config
    connections._settings = connections.configure_settings(settings.DATABASES)
    # open a connection to the database with the new database config
    connections["default"] = connections.create_connection("default")


# FIXME: Problème sur 91390/8a0f3202-6721-4b60-ac63-7363319539b8
# Approbation pas détectée. Est-ce un problème de normalisation unicode ?
DATE_DAPPROBATION_MAL_DETECTEE = [
    ("09106", "93de19ac-d609-4b26-8651-6c43ed5a2a8a"),
    ("09106", "51ded599-7b22-44ca-b740-bf8b7475f266"),
    ("09168", "93de19ac-d609-4b26-8651-6c43ed5a2a8a"),
    ("09168", "5f8cf12b-4d7a-4ad6-a30e-5c10c2421ba5"),
    ("09249", "93de19ac-d609-4b26-8651-6c43ed5a2a8a"),
    ("09249", "da8a2cca-e609-41ee-948d-5b492793dead"),
    ("09305", "93de19ac-d609-4b26-8651-6c43ed5a2a8a"),
    ("09305", "8724af17-193f-44a7-80c4-ce7469866b86"),
    ("12066", "2940c934-d3f2-43d4-8678-21a9c3a5e3db"),
    ("12066", "5bdf7888-9b63-4a32-983f-7fe55a3c5ab0"),
    ("12076", "2940c934-d3f2-43d4-8678-21a9c3a5e3db"),
    ("12076", "027741b2-9d93-4606-94fb-43dca8655ba5"),
    ("12138", "2940c934-d3f2-43d4-8678-21a9c3a5e3db"),
    ("12138", "76d95ba8-510c-4bfc-b7d8-f49d3e4bc822"),
    ("12161", "2940c934-d3f2-43d4-8678-21a9c3a5e3db"),
    ("12161", "761923eb-ef9a-4836-809a-8fef427aba9c"),
    ("12165", "2940c934-d3f2-43d4-8678-21a9c3a5e3db"),
    ("12165", "da0a633d-2570-4ceb-9090-699f6eaf3d40"),
    ("12215", "2940c934-d3f2-43d4-8678-21a9c3a5e3db"),
    ("12215", "c0d393f7-bae3-4a6f-b83c-3d4f6c0d5769"),
    ("12221", "2940c934-d3f2-43d4-8678-21a9c3a5e3db"),
    ("12221", "d6bda473-bbb4-4dae-9fac-14fe9bcbd60f"),
    ("12254", "2940c934-d3f2-43d4-8678-21a9c3a5e3db"),
    ("12254", "9b13518b-8b4d-469c-b0b2-32b5af930342"),
    ("12288", "2940c934-d3f2-43d4-8678-21a9c3a5e3db"),
    ("12288", "e28018e0-6306-4c0d-a74c-ebdc7c2386e8"),
    ("14365", "2f9b15b9-81fd-4634-8be9-119d41e0c45f"),
    ("14365", "f58c3625-b5b3-45a5-aff1-c47c99822518"),
]

PROCEDURE_DABROGATION = [
    ("15006", "475f2868-afb8-4dc9-8ca4-06e5a6a49333"),
    ("15006", "506775b3-abdf-4e5b-b73b-0d882363ebd7"),
]
LEGITIMATE_DIFFERENCES = [
    # df2439d9-ba4f-4cba-9fcf-c8ed3a52b24c est un SCoT opposable mais pas pour 01155
    ("01155", "40e4f479-d0f1-4d2d-9f80-6760c44b22e5"),
    *DATE_DAPPROBATION_MAL_DETECTEE,
    *PROCEDURE_DABROGATION,
]


class TestPerimetres:
    def _retrieve_nuxt(self, original: str) -> pl.DataFrame:
        cached_csv = (
            Path("core/tests/nuxt_snapshots")
            / hashlib.md5(original.encode(), usedforsecurity=False).hexdigest()
        )
        if not cached_csv.exists() or (
            datetime.now(UTC) - datetime.fromtimestamp(cached_csv.stat().st_mtime, UTC)
            > timedelta(hours=1)
        ):
            logging.warning("Refreshing CSV")
            urlretrieve(Env().str("UPSTREAM_NUXT") + original, cached_csv)  # noqa: S310
        nuxt = pl.read_csv(
            cached_csv,
            try_parse_dates=True,
            schema_overrides={
                "departement": pl.String(),
                "collectivite_code": pl.String(),
            },
        ).sort("collectivite_code", "collectivite_type", "procedure_id")
        nuxt.drop_in_place("id")
        nuxt.drop_in_place("added_at")
        nuxt.drop_in_place("procedures")
        return nuxt

    @pytest.mark.django_db
    def Ztest_all(
        self, client: Client, django_assert_num_queries: DjangoAssertNumQueries
    ) -> None:
        nuxt = self._retrieve_nuxt("/api/urba/exports/perimetres")
        assert len(nuxt) == 141871

        with django_assert_num_queries(2):
            response = client.get("/api/perimetres")

        django = pl.read_csv(
            response.content,
            try_parse_dates=True,
            schema_overrides={
                "departement": pl.String(),
                "collectivite_code": pl.String(),
            },
        )
        # nuxtset = {
        #     f"{a['procedure_id']}_{a['collectivite_code']}" for a in nuxt.to_dicts()
        # }
        # djangoset = {
        #     f"{a['procedure_id']}_{a['collectivite_code']}" for a in django.to_dicts()
        # }
        # assert nuxtset == djangoset
        limit = 4000
        polars.testing.assert_frame_equal(
            nuxt.limit(limit).sort(
                "collectivite_code", "collectivite_type", "procedure_id"
            ),
            django.limit(limit).sort(
                "collectivite_code", "collectivite_type", "procedure_id"
            ),
        )

    # FIXME Ne pas oublier la corse
    @pytest.mark.parametrize("departement", [f"{i:0>2}" for i in range(24, 25)])
    @pytest.mark.django_db
    def test_departement(
        self,
        client: Client,
        django_assert_num_queries: DjangoAssertNumQueries,
        departement: str,
    ) -> None:
        nuxt = self._retrieve_nuxt(
            f"/api/urba/exports/perimetres?departement={departement}"
        )
        # assert len(nuxt) == 1324

        # limit = 200
        limit = 1000000
        nuxt = nuxt.limit(limit)
        with django_assert_num_queries(2):
            before = datetime.now()
            response = client.get(
                "/api/perimetres",
                query_params={"departement": departement, "limit": limit},
            )
            logging.warning(response.resolver_match)
            logging.warning((datetime.now() - before) / timedelta(milliseconds=1))

        django = pl.read_csv(
            response.content,
            try_parse_dates=True,
            schema_overrides={
                "departement": pl.String(),
                "collectivite_code": pl.String(),
            },
        ).sort("collectivite_code", "collectivite_type", "procedure_id")
        # logging.warning(nuxt)
        # logging.warning(django)
        # logging.warning(nuxt["procedure_id"].to_list())
        # # logging.warning(django["procedure_id"].to_list())
        # logging.warning(nuxt[-1].to_dict())
        # logging.warning(django[-1].to_dict())
        # logging.warning(nuxt[-1]["procedure_id"].to_list())
        # logging.warning(django[-1]["procedure_id"].to_list())

        for nuxt_row, django_row in zip(
            nuxt.iter_rows(named=True), django.iter_rows(named=True), strict=True
        ):
            if nuxt_row["collectivite_type"] == "COMD":
                continue
            if (
                f"{nuxt_row['collectivite_code']}_COMD" in communes
                and f"{nuxt_row['collectivite_code']}_COM" not in communes
            ):
                # assert nuxt_row == "lol"
                continue
            if (
                nuxt_row["collectivite_code"],
                nuxt_row["procedure_id"],
            ) in LEGITIMATE_DIFFERENCES:
                logging.warning(f"Ignoring {nuxt_row['procedure_id']}")  # noqa: G004
                assert nuxt_row != django_row
            else:
                assert nuxt_row == django_row
        # polars.testing.assert_frame_equal(nuxt, django)
