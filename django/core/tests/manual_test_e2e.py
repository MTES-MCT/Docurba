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
        return pl.read_csv(cached_csv, try_parse_dates=True)

    @pytest.mark.django_db
    def Ztest_all(
        self, client: Client, django_assert_num_queries: DjangoAssertNumQueries
    ) -> None:
        nuxt = self._retrieve_nuxt("/api/urba/exports/perimetres")
        assert len(nuxt) == 336727

        with django_assert_num_queries(1):
            response = client.get("/api/perimetres")

        django = pl.read_csv(response.content, try_parse_dates=True)
        polars.testing.assert_frame_equal(nuxt, django)

    @pytest.mark.django_db
    def test_56(
        self, client: Client, django_assert_num_queries: DjangoAssertNumQueries
    ) -> None:
        nuxt = self._retrieve_nuxt("/api/urba/exports/perimetres?departement=56")
        nuxt.drop_in_place("id")
        nuxt.drop_in_place("added_at")
        assert len(nuxt) == 2671

        with django_assert_num_queries(1):
            response = client.get("/api/perimetres?departement=56")

        django = pl.read_csv(response.content, try_parse_dates=True)
        polars.testing.assert_frame_equal(nuxt, django)
