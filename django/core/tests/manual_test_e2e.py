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
    ("09106", "COM", "93de19ac-d609-4b26-8651-6c43ed5a2a8a"),
    ("09106", "COM", "51ded599-7b22-44ca-b740-bf8b7475f266"),
    ("09168", "COM", "93de19ac-d609-4b26-8651-6c43ed5a2a8a"),
    ("09168", "COM", "5f8cf12b-4d7a-4ad6-a30e-5c10c2421ba5"),
    ("09249", "COM", "93de19ac-d609-4b26-8651-6c43ed5a2a8a"),
    ("09249", "COM", "da8a2cca-e609-41ee-948d-5b492793dead"),
    ("09305", "COM", "93de19ac-d609-4b26-8651-6c43ed5a2a8a"),
    ("09305", "COM", "8724af17-193f-44a7-80c4-ce7469866b86"),
    ("12066", "COM", "2940c934-d3f2-43d4-8678-21a9c3a5e3db"),
    ("12066", "COM", "5bdf7888-9b63-4a32-983f-7fe55a3c5ab0"),
    ("12076", "COM", "2940c934-d3f2-43d4-8678-21a9c3a5e3db"),
    ("12076", "COM", "027741b2-9d93-4606-94fb-43dca8655ba5"),
    ("12138", "COM", "2940c934-d3f2-43d4-8678-21a9c3a5e3db"),
    ("12138", "COM", "76d95ba8-510c-4bfc-b7d8-f49d3e4bc822"),
    ("12161", "COM", "2940c934-d3f2-43d4-8678-21a9c3a5e3db"),
    ("12161", "COM", "761923eb-ef9a-4836-809a-8fef427aba9c"),
    ("12165", "COM", "2940c934-d3f2-43d4-8678-21a9c3a5e3db"),
    ("12165", "COM", "da0a633d-2570-4ceb-9090-699f6eaf3d40"),
    ("12215", "COM", "2940c934-d3f2-43d4-8678-21a9c3a5e3db"),
    ("12215", "COM", "c0d393f7-bae3-4a6f-b83c-3d4f6c0d5769"),
    ("12221", "COM", "2940c934-d3f2-43d4-8678-21a9c3a5e3db"),
    ("12221", "COM", "d6bda473-bbb4-4dae-9fac-14fe9bcbd60f"),
    ("12254", "COM", "2940c934-d3f2-43d4-8678-21a9c3a5e3db"),
    ("12254", "COM", "9b13518b-8b4d-469c-b0b2-32b5af930342"),
    ("12288", "COM", "2940c934-d3f2-43d4-8678-21a9c3a5e3db"),
    ("12288", "COM", "e28018e0-6306-4c0d-a74c-ebdc7c2386e8"),
    ("14365", "COM", "2f9b15b9-81fd-4634-8be9-119d41e0c45f"),
    ("14365", "COM", "f58c3625-b5b3-45a5-aff1-c47c99822518"),
    ("26179", "COM", "53f8aa39-2557-4eb7-8238-07cb923e60fc"),
    ("26179", "COM", "e830835b-cfa8-47d5-a50d-78e4b818edf6"),
]
SD_OPPOSABLE = [
    ("25132", "COM", "4c94b230-f79c-46df-aa96-9bb9307ffcf6"),
]
COM_DEVENUE_COMD = [
    ("25282", "COM", "5f3efb46-7c15-4a4f-b569-197c5e2b2e55"),
    ("25549", "COM", "5f3efb46-7c15-4a4f-b569-197c5e2b2e55"),
    ("16355", "COM", "7e422814-a017-473a-aea6-02bb53525c2c"),  # PLU
    ("16355", "COM", "ba8a1589-6276-4ed7-a140-fea24999c925"),  # SCOT
    ("08294", "COM", "c00c9a5e-03a1-4dae-b298-fa32d8a54c13"),  # PLU
]
PROCEDURE_DABROGATION = [
    ("15006", "COM", "475f2868-afb8-4dc9-8ca4-06e5a6a49333"),
    ("15006", "COM", "506775b3-abdf-4e5b-b73b-0d882363ebd7"),
]
PROCEDURES_SECTORIELLES = [
    ("24087", "COM", "03127305-b00f-49f5-9c4e-4bbd2f217c70"),
    ("24087", "COM", "f2052f81-7e87-426b-8ce1-e48eed9be2d4"),
]
LEGITIMATE_DIFFERENCES = [
    # df2439d9-ba4f-4cba-9fcf-c8ed3a52b24c est un SCoT opposable mais pas pour 01155
    ("01155", "COM", "40e4f479-d0f1-4d2d-9f80-6760c44b22e5"),
    # Nuxt donne deux PLU opposables, on fait mieux
    ("05001", "COMD", "cf448ad5-193b-4c1f-a38b-d92a9b4472e6"),
    *DATE_DAPPROBATION_MAL_DETECTEE,
    *PROCEDURE_DABROGATION,
    *SD_OPPOSABLE,
    *COM_DEVENUE_COMD,
    *PROCEDURES_SECTORIELLES,
]
# 25282 COM/COMD 31a80d85-f75e-4177-8493-e47b38b4cab4 Supprimée le 16/03 (avec COM) pour être recréée le 17/03
# 25549 COM/COMD 3f547284-d110-48cc-874d-a87cc17c8505 Supprimée le 16/03 (avec COM) pour être recréée le 17/03


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
    @pytest.mark.parametrize("departement", [f"{i:0>2}" for i in range(1, 35)])
    @pytest.mark.django_db
    def test_departement(
        self,
        client: Client,
        django_assert_num_queries: DjangoAssertNumQueries,
        departement: str,
    ) -> None:
        if departement == "20":
            departement = "2A"
        nuxt = self._retrieve_nuxt(
            f"/api/urba/exports/perimetres?departement={departement}"
        )

        with django_assert_num_queries(2):
            before = datetime.now()
            response = client.get(
                "/api/perimetres",
                query_params={"departement": departement},
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

        for nuxt_row, django_row in zip(
            nuxt.iter_rows(named=True), django.iter_rows(named=True), strict=True
        ):
            if (
                nuxt_row["collectivite_code"],
                nuxt_row["collectivite_type"],
                nuxt_row["procedure_id"],
            ) in LEGITIMATE_DIFFERENCES:
                logging.warning(f"Ignoring {nuxt_row['procedure_id']}")  # noqa: G004
                assert nuxt_row != django_row
            else:
                assert nuxt_row == django_row
