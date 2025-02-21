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


LEGITIMATE_DIFFERENCES = [
    # df2439d9-ba4f-4cba-9fcf-c8ed3a52b24c est un SCoT opposable mais pas pour 01155
    ("01155", "40e4f479-d0f1-4d2d-9f80-6760c44b22e5"),
    (),
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

    @pytest.mark.parametrize("departement", [f"{i:0>2}" for i in range(24, 25)])
    @pytest.mark.django_db
    def test_departement(
        self,
        client: Client,
        django_assert_num_queries: DjangoAssertNumQueries,
        departement,
    ) -> None:
        nuxt = self._retrieve_nuxt(
            f"/api/urba/exports/perimetres?departement={departement}"
        )
        # assert len(nuxt) == 1324

        # limit = 200
        limit = 1000000
        nuxt = nuxt.limit(limit)
        with django_assert_num_queries(2):
            response = client.get(
                "/api/perimetres",
                query_params={"departement": departement, "limit": limit},
            )

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
                continue

            assert nuxt_row == django_row
        # polars.testing.assert_frame_equal(nuxt, django)
