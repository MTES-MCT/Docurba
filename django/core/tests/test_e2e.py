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


# https://pytest-django.readthedocs.io/en/latest/database.html#using-an-existing-external-database-for-tests
@pytest.fixture(scope="module")
def django_db_setup(django_db_modify_db_settings) -> None:
    # remove cached_property of connections.settings from the cache
    del connections.__dict__["settings"]

    settings.DATABASES["default"] = Env().db("PRODUCTION_DATABASE_URL")

    # re-configure the settings given the changed database config
    connections._settings = connections.configure_settings(settings.DATABASES)
    # open a connection to the database with the new database config
    connections["default"] = connections.create_connection("default")


class TestPerimetres:
    def _retrieve_fresh_csv(self, cached_csv: Path, original: str) -> None:
        if not cached_csv.exists() or (
            datetime.now(UTC) - datetime.fromtimestamp(cached_csv.stat().st_mtime, UTC)
            > timedelta(hours=1)
        ):
            logging.warning("Refreshing CSV")
            urlretrieve(original, cached_csv)  # noqa: S310

    @pytest.mark.django_db
    def Ztest_all(self, client: Client, django_assert_num_queries) -> None:
        cached_csv = Path("core/tests/perimetres.csv")
        self._retrieve_fresh_csv(
            cached_csv,
            "http://localhost:3000/api/urba/exports/perimetres",
        )
        nuxt = pl.read_csv(cached_csv, try_parse_dates=True)
        assert len(nuxt) == 336727

        with django_assert_num_queries(1):
            response = client.get("/api/perimetres")

        django = pl.read_csv(response.content, try_parse_dates=True)

        polars.testing.assert_frame_equal(nuxt, django)

    @pytest.mark.django_db
    def test_56(self, client: Client, django_assert_num_queries) -> None:
        cached_csv = Path("core/tests/perimetres_56.csv")
        self._retrieve_fresh_csv(
            cached_csv,
            "http://localhost:3000/api/urba/exports/perimetres?departement=56",
        )
        nuxt = pl.read_csv(cached_csv, try_parse_dates=True)
        assert len(nuxt) == 2671

        with django_assert_num_queries(1):
            response = client.get("/api/perimetres?departement=56")

        django = pl.read_csv(response.content, try_parse_dates=True)

        polars.testing.assert_frame_equal(nuxt, django)
