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
from django.urls import reverse
from environ import Env
from pytest_django import DjangoAssertNumQueries


# https://pytest-django.readthedocs.io/en/latest/database.html#using-an-existing-external-database-for-tests
# https://github.com/pytest-dev/pytest-django/issues/643
@pytest.fixture(scope="module")
def django_db_setup(django_db_modify_db_settings: None) -> None:  # noqa: ARG001
    # remove cached_property of connections.settings from the cache
    del connections.__dict__["settings"]

    settings.DATABASES["default"] = Env().db("PRODUCTION_DATABASE_URL")

    # re-configure the settings given the changed database config
    connections._settings = connections.configure_settings(settings.DATABASES)  # noqa: SLF001
    # open a connection to the database with the new database config
    connections["default"] = connections.create_connection("default")


DATE_DAPPROBATION_MAL_DETECTEE = [
    ("09106", "COM", "93de19ac-d609-4b26-8651-6c43ed5a2a8a"),
    ("09106", "COM", "51ded599-7b22-44ca-b740-bf8b7475f266"),
    ("09168", "COM", "93de19ac-d609-4b26-8651-6c43ed5a2a8a"),
    ("09168", "COM", "5f8cf12b-4d7a-4ad6-a30e-5c10c2421ba5"),
    ("09249", "COM", "93de19ac-d609-4b26-8651-6c43ed5a2a8a"),
    ("09249", "COM", "da8a2cca-e609-41ee-948d-5b492793dead"),
    ("09305", "COM", "93de19ac-d609-4b26-8651-6c43ed5a2a8a"),
    ("09305", "COM", "8724af17-193f-44a7-80c4-ce7469866b86"),
    ("14365", "COM", "2f9b15b9-81fd-4634-8be9-119d41e0c45f"),
    ("14365", "COM", "f58c3625-b5b3-45a5-aff1-c47c99822518"),
    ("26179", "COM", "53f8aa39-2557-4eb7-8238-07cb923e60fc"),
    ("26179", "COM", "e830835b-cfa8-47d5-a50d-78e4b818edf6"),
    ("30216", "COM", "51979ada-b38f-4bc4-a565-9619312341c4"),
    ("30216", "COM", "3c098394-743e-4764-8f38-4e369d0bbbbd"),
    ("30321", "COM", "895d1152-4774-4ab8-bd03-2bc3bfb9e204"),
    ("30321", "COM", "434e0c84-7a46-40c4-bfd5-9d0403bf0438"),
    ("32016", "COM", "5df9e6ef-4505-4c8e-a658-6f005768356f"),
    ("32016", "COM", "3b34eb61-cb0e-46e2-a36c-76b9232c21af"),
    ("32090", "COM", "5df9e6ef-4505-4c8e-a658-6f005768356f"),
    ("32090", "COM", "4ae5c3bd-8c87-4c6d-a318-fb292bc64364"),
    ("32105", "COM", "5df9e6ef-4505-4c8e-a658-6f005768356f"),
    ("32105", "COM", "37ccdd2b-5533-46dd-9fef-1ea9a5316b6e"),
    ("32121", "COM", "5df9e6ef-4505-4c8e-a658-6f005768356f"),
    ("32121", "COM", "d7a6e51a-24d5-4b60-a9a0-779b5839ae5d"),
    ("32134", "COM", "5df9e6ef-4505-4c8e-a658-6f005768356f"),
    ("32134", "COM", "d2a1b936-8fdd-4280-913f-37deab1c3c31"),
    ("32160", "COM", "5df9e6ef-4505-4c8e-a658-6f005768356f"),
    ("32160", "COM", "641c0d0e-fd6f-4e97-ae26-19165edd9d5b"),
    ("32210", "COM", "5df9e6ef-4505-4c8e-a658-6f005768356f"),
    ("32210", "COM", "402f7daf-6779-4a1f-9f5e-a11d48ae5b25"),
    ("32268", "COM", "5df9e6ef-4505-4c8e-a658-6f005768356f"),
    ("32268", "COM", "ae660b77-250d-4371-b76a-d1cbbea9dc66"),
    ("32334", "COM", "5df9e6ef-4505-4c8e-a658-6f005768356f"),
    ("32334", "COM", "5eec6001-d363-4faa-9dea-4e44a49c1310"),
    ("32339", "COM", "5df9e6ef-4505-4c8e-a658-6f005768356f"),
    ("32339", "COM", "ea28808c-6c64-48b7-86b8-8117396b0893"),
    ("32425", "COM", "5df9e6ef-4505-4c8e-a658-6f005768356f"),
    ("32425", "COM", "869403a5-5ecd-4bc7-b88d-8183e013546a"),
    ("35126", "COM", "679e1833-f117-45e7-8e99-b513a533d54f"),
    ("35126", "COM", "fff7609e-cbe4-44fd-9caa-4a071eed376d"),
    ("35284", "COM", "d0d7b3da-2943-4a26-968f-4441effa047d"),
    ("35284", "COM", "b7220fec-f119-4738-bfe9-38c018229933"),
    ("35358", "COM", "1c8c32ef-f5de-4a2b-a22d-af41ddd2a0fa"),
    ("35358", "COM", "dc9dad09-faf1-4772-916f-f4ebb0d20dc1"),
    ("37150", "COM", "92ee19b3-2d22-4551-a797-8f552656a132"),
    ("37150", "COM", "fd5912a2-3b04-4b84-9b78-3d82f8e24fd8"),
    ("42178", "COM", "4bc62080-7d7d-44dd-8d73-e40e64dfca99"),
    ("42178", "COM", "c4074a28-443f-4884-8523-5891b3db3187"),
    ("51076", "COM", "370ec285-deed-4faa-bf02-dffc66be8081"),
    ("51076", "COM", "bcaf8a9d-0dc5-4558-a880-8908108ed31c"),
    ("58278", "COM", "dc4dc271-3f1a-4681-8229-96ff8df77611"),
    ("58278", "COM", "fbb92c4c-eb0d-4e8f-8892-d6b0f7a045f1"),
    ("60024", "COM", "df50a1b2-6e4c-49dd-bfb0-15f3fdbc83d2"),
    ("60024", "COM", "342551f1-21ba-4d40-97c4-14a278497452"),
    ("60036", "COM", "df50a1b2-6e4c-49dd-bfb0-15f3fdbc83d2"),
    ("60036", "COM", "0318c9ed-ad53-4ed1-b0f5-d83ad14675aa"),
    ("60040", "COM", "df50a1b2-6e4c-49dd-bfb0-15f3fdbc83d2"),
    ("60040", "COM", "c8987d05-dee2-4840-abf6-aea1822c5004"),
    ("60078", "COM", "df50a1b2-6e4c-49dd-bfb0-15f3fdbc83d2"),
    ("60078", "COM", "477175c0-1455-460a-9a51-e76142d29f5d"),
    ("60125", "COM", "df50a1b2-6e4c-49dd-bfb0-15f3fdbc83d2"),
    ("60125", "COM", "03674860-ea56-4b3e-984f-8e0706c99558"),
    ("60149", "COM", "df50a1b2-6e4c-49dd-bfb0-15f3fdbc83d2"),
    ("60149", "COM", "f6146ac5-825d-48ca-b04c-366b12dd9c6b"),
    ("60152", "COM", "df50a1b2-6e4c-49dd-bfb0-15f3fdbc83d2"),
    ("60152", "COM", "8ba9ca78-0acf-48a7-aff3-0333ca23dba8"),
    ("60223", "COM", "df50a1b2-6e4c-49dd-bfb0-15f3fdbc83d2"),
    ("60223", "COM", "8c318483-4cb5-49cc-9050-5753e44fb456"),
    ("60224", "COM", "8cc9bd59-b650-4832-bfb7-fc17ca635062"),
    ("60224", "COM", "dfc3ed1a-40f6-48c4-bd62-e55723228014"),
    ("60229", "COM", "df50a1b2-6e4c-49dd-bfb0-15f3fdbc83d2"),
    ("60229", "COM", "6ba5de70-c5ef-46c5-8c8f-d8fe9a6d50cc"),
    ("60254", "COM", "df50a1b2-6e4c-49dd-bfb0-15f3fdbc83d2"),
    ("60254", "COM", "3ec391ac-1dd7-43e0-a9d0-2970dc78dc42"),
    ("60284", "COM", "df50a1b2-6e4c-49dd-bfb0-15f3fdbc83d2"),
    ("60284", "COM", "a0547363-c597-4a3f-8a57-61e27de3e795"),
    ("60308", "COM", "df50a1b2-6e4c-49dd-bfb0-15f3fdbc83d2"),
    ("60308", "COM", "3b1296ce-8d2a-4ac7-ab51-938d1f4a529c"),
    ("60318", "COM", "df50a1b2-6e4c-49dd-bfb0-15f3fdbc83d2"),
    ("60318", "COM", "d3fa01c3-7922-4e3f-b5bd-ffc99e67478b"),
    ("60369", "COM", "df50a1b2-6e4c-49dd-bfb0-15f3fdbc83d2"),
    ("60369", "COM", "d6b874ca-2a0a-4c11-9cd3-4610183978f0"),
    ("60424", "COM", "df50a1b2-6e4c-49dd-bfb0-15f3fdbc83d2"),
    ("60424", "COM", "db1c2d95-33f5-4ccf-b676-be5087b7ee9c"),
    ("60441", "COM", "df50a1b2-6e4c-49dd-bfb0-15f3fdbc83d2"),
    ("60441", "COM", "50dcc3f6-6a08-4592-9fc3-792957b55e1c"),
    ("60531", "COM", "df50a1b2-6e4c-49dd-bfb0-15f3fdbc83d2"),
    ("60531", "COM", "d1651ff9-aa6e-4ae6-b90b-d331c0170b63"),
    ("60540", "COM", "df50a1b2-6e4c-49dd-bfb0-15f3fdbc83d2"),
    ("60540", "COM", "e293c5a5-6fcb-408e-84fc-cb12521a3627"),
    ("68056", "COM", "2e2f5c1a-65b5-44e1-af45-bcb8ca5f8a0d"),
    ("68056", "COM", "b630d804-4aa7-42c9-a849-359d29e58e64"),
    ("68056", "COMD", "2e2f5c1a-65b5-44e1-af45-bcb8ca5f8a0d"),
    ("77349", "COM", "0ffda3fd-cefe-4200-986b-5dbce235ba12"),
    ("77349", "COM", "e452d44c-63ab-4971-a3c6-8c32fc2b9760"),
    ("78517", "COM", "38048e04-4f13-46f9-a308-501ae203f505"),
    ("78517", "COM", "3656ff56-7ff5-4384-9b43-41c487865768"),
    ("78616", "COM", "1763164c-e23d-412c-a416-7f16fa3afda2"),
    ("78616", "COM", "f49c481f-8022-40a8-b3dd-8446a4eb113e"),
]
SD_OPPOSABLE = [
    # Si SD en cours -> Abandon
    # Si SD opposable -> Caduc
    ("25132", "COM", "4c94b230-f79c-46df-aa96-9bb9307ffcf6"),
]
COM_DEVENUE_COMD = [
    ("08294", "COM", "c00c9a5e-03a1-4dae-b298-fa32d8a54c13"),  # PLU
    ("16355", "COM", "7e422814-a017-473a-aea6-02bb53525c2c"),  # PLU
    ("16355", "COM", "ba8a1589-6276-4ed7-a140-fea24999c925"),  # SCOT
    ("25282", "COM", "5f3efb46-7c15-4a4f-b569-197c5e2b2e55"),
    ("25282", "COM", "ee671943-2573-4827-b9c6-46a9713550d9"),
    ("25549", "COM", "f30ddee9-d76c-402f-af70-3f719ce024c7"),
    ("25549", "COM", "5f3efb46-7c15-4a4f-b569-197c5e2b2e55"),
    ("35112", "COM", "dc37f337-eeea-4ddd-9269-b808733bac60"),  # SCOT
    ("35112", "COM", "e0eb08f1-22f1-4b59-9458-67e2e273c11b"),  # PLU
    ("49321", "COM", "6f6ca667-11f2-4740-a812-cd8aca4ef871"),  # PLU
    ("49321", "COM", "899ea350-7b2d-4f79-b2c5-73d4d4db1016"),  # SCOT
    ("64541", "COM", "d7d3860e-6fef-4bab-a3fd-acb49faed47d"),  # PLU
    ("69152", "COM", "341b069f-86dd-4ef0-be31-27519331cb52"),  # SCOT
    ("69152", "COM", "561c93a4-1fd5-4d12-a57b-9ce07a392675"),  # PLU
    ("85041", "COM", "17beec5d-ed83-4ac9-9dbc-ed54d40763f8"),  # SCOT
    ("85041", "COM", "d94edd24-1b9d-4a6d-a32d-c163199f9e38"),  # PLU
    ("85271", "COM", "17beec5d-ed83-4ac9-9dbc-ed54d40763f8"),  # SCOT
    ("85271", "COM", "d94edd24-1b9d-4a6d-a32d-c163199f9e38"),  # PLU
    ("86231", "COM", "88239098-221e-4df9-b239-816e7f39adda"),  # SCOT
    ("86231", "COM", "ff68a91b-592c-40ca-8c88-0bc8bc6ce810"),  # PLU
]
PROCEDURE_DABROGATION = [
    # On est bons
    ("15006", "COM", "475f2868-afb8-4dc9-8ca4-06e5a6a49333"),
    ("15006", "COM", "506775b3-abdf-4e5b-b73b-0d882363ebd7"),
    # On est bons
    ("70296", "COM", "acb69d9e-f712-4d00-89f7-c01ff34d0940"),
    # Hermance : signaler une erreur
    ("73189", "COM", "94489998-162b-48ea-b29b-2a811b0ba599"),
    ("73189", "COM", "bfeac1ce-786d-4586-b669-5d42ff134cb9"),
]
PROCEDURES_SECTORIELLES = [
    ("24087", "COM", "03127305-b00f-49f5-9c4e-4bbd2f217c70"),
    ("24087", "COM", "f2052f81-7e87-426b-8ce1-e48eed9be2d4"),
    ("44213", "COM", "c8f11169-be55-4050-87b7-79ff621362dc"),
    ("44213", "COM", "fe45b18c-7db4-4447-b3d7-c3f6bbeefede"),
    ("72023", "COM", "2e2df2f5-d5d2-4bca-a30c-bd8c8f5821e7"),
    ("72023", "COM", "a9d14cd7-89e7-4000-950a-7aca3052906b"),
]
DEUX_EVENTS_LE_MEME_JOUR = [
    ("2B286", "COM", "dbca33bb-5d3f-43e6-89d4-f36796c436bb"),
]
DEUX_PROCEDURES_APPROUVEES_LE_MEME_JOUR = [
    ("63284", "COM", "c79781aa-32c6-4252-aa85-008b9e8f3ef0"),
    ("63284", "COM", "d8716395-9599-4b58-8abe-4cbf01539089"),
    ("63287", "COM", "4fab76e3-3ef4-4986-aca6-50dc366b17f5"),
    ("63287", "COM", "b323c6d1-e482-4f20-8a4f-2f6901380ac2"),
    ("67168", "COM", "1b7c8a98-2fd0-4a3b-a1fd-f1f1939bff50"),
    ("67168", "COM", "d3ea434e-4db0-46cd-9414-ce9bba6410bf"),
    ("90041", "COM", "8264005f-cfd7-4484-be5b-f859a50a59b0"),
    ("90041", "COM", "d5eeb3de-7406-40ca-8263-def8be6156df"),
]
NUXT_CONSIDERE_EVENEMENT_INVALIDE = [
    ("57251", "COM", "5a7cefde-0a81-493e-bb63-22b4827ffb65"),
    ("57403", "COM", "8fe6bc24-faf3-4613-9cbf-66748980a13b"),
    ("57532", "COM", "ea9ccb62-58fc-4cb8-bb9f-f38e6b8942d1"),
    ("57653", "COM", "8eb47633-5b19-4d88-b1e2-0aafd85ff9ce"),
    ("57715", "COM", "e5479169-36a4-4b2f-a31b-e4084e214d27"),
]
COMMUNES_DISPARUES = [
    ("19092", "UNKWN", "68907c42-1712-4508-a01e-4ffa26b5156c"),
    ("19092", "UNKWN", "bccb0d87-6059-49b2-930d-d0937743224f"),
    ("25134", "UNKWN", ""),
    ("25628", "UNKWN", "109fa690-994a-4398-9a1f-c404392f532e"),
    ("45287", "UNKWN", "78be3500-881a-487f-b40e-2d5706938136"),
    ("45287", "UNKWN", "b84585df-ffe5-4136-81e8-c53001d8ca18"),
    ("97123", "UNKWN", ""),
    ("97127", "UNKWN", "63ff9b83-9bac-4c5f-830c-31a901dfc05e"),
]
# Elaboration et révision le même jour ? c8bf0cc2-5ded-490b-8abb-7875c61091f0
DIFFERENCES = [
    # df2439d9-ba4f-4cba-9fcf-c8ed3a52b24c est un SCoT opposable mais pas pour 01155
    ("01155", "COM", "40e4f479-d0f1-4d2d-9f80-6760c44b22e5"),
    # Nuxt donne deux PLU opposables, on fait mieux
    ("05001", "COMD", "cf448ad5-193b-4c1f-a38b-d92a9b4472e6"),
    # Je pense que c'est date d'approbation mal détectée mais c'est bizarre d'avoir un POS avec un événement 29 ans plus tard
    ("77440", "COM", "c3297e3c-5628-4cc1-a236-412de6d7c256"),
    ("77440", "COM", "c3f618f7-b792-4654-b216-b66362a6dc74"),
    # Gouzangrez fusionne avec Commeny mais ne devient pas une commune déléguée
    ("95282", "COM", "ce37494f-1ff8-48a2-b766-51316fb67110"),
    *DATE_DAPPROBATION_MAL_DETECTEE,
    *PROCEDURE_DABROGATION,
    *SD_OPPOSABLE,
    *COM_DEVENUE_COMD,
    *PROCEDURES_SECTORIELLES,
    *DEUX_EVENTS_LE_MEME_JOUR,
    *NUXT_CONSIDERE_EVENEMENT_INVALIDE,
    *DEUX_PROCEDURES_APPROUVEES_LE_MEME_JOUR,
    *COMMUNES_DISPARUES,
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
        nuxt.drop_in_place("created_at")
        nuxt.drop_in_place("departement")
        nuxt.drop_in_place("added_at")
        nuxt.drop_in_place("procedures")
        return nuxt

    @pytest.mark.django_db
    def test_all(
        self,
        client: Client,
        django_assert_num_queries: DjangoAssertNumQueries,
    ) -> None:
        nuxt = self._retrieve_nuxt("/api/urba/exports/perimetres")

        with django_assert_num_queries(2):
            response = client.get("/api/perimetres")

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
            ) in DIFFERENCES:
                logging.warning(f"Ignoring {nuxt_row['procedure_id']}")  # noqa: G004
                assert nuxt_row != django_row
            else:
                assert nuxt_row == django_row

    @pytest.mark.parametrize(
        "departement",
        [
            f"{i:0>2}"
            for i in ["976", "974", "973", "972", "971", "2B", "2A", *range(95, 0, -1)]
        ],
    )
    @pytest.mark.django_db
    def test_departement(
        self,
        client: Client,
        django_assert_num_queries: DjangoAssertNumQueries,
        departement: str,
    ) -> None:
        if departement == "20":
            return
        nuxt = self._retrieve_nuxt(
            f"/api/urba/exports/perimetres?departement={departement}"
        )

        with django_assert_num_queries(2):
            response = client.get(
                "/api/perimetres",
                query_params={"departement": departement},
            )

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
            ) in DIFFERENCES:
                logging.warning(f"Ignoring {nuxt_row['procedure_id']}")  # noqa: G004
                assert nuxt_row != django_row
            else:
                assert nuxt_row == django_row


class TestScots:
    PLUSIEURS_EN_COURS = [  # noqa: RUF012
        200035319,
    ]

    # Taille de périmètre fausse
    COMMUNE_FUSIONNEE_EN_2024 = [  # noqa: RUF012
        200041473,  # 86231
        200048858,  # 16355
        200052629,  # 49321
        200060259,  # 19092_UNKWN
        200061836,  # 25549 25282
        200068070,  # 25134_UNKWN 25628_UNKWN
        200086643,  # 45287_UNKWN
        200088730,  # 08294
        251802161,  # 18131
        253514632,  # 35112
    ]

    # https://github.com/betagouv/docurba-nuxt3/pull/17/
    FILTRE_SUDOCU_PRESCRIPTION_NON_IMPLEMENTE = [  # noqa: RUF012
        200069532,  # Lisieux https://docurba.beta.gouv.fr/collectivite/14366/
        200010700,
        200079903,
        200000099,
    ]

    NUXT_NE_REGARDE_PAS_EVENT_INVALIDE = [  # noqa: RUF012
        240500462,
    ]
    DIFFERENCES = (
        PLUSIEURS_EN_COURS
        + COMMUNE_FUSIONNEE_EN_2024
        + FILTRE_SUDOCU_PRESCRIPTION_NON_IMPLEMENTE
        + NUXT_NE_REGARDE_PAS_EVENT_INVALIDE
    )

    def _retrieve_nuxt(self, original: str) -> pl.DataFrame:
        cached_csv = (
            Path("core/tests/nuxt_snapshots")
            / hashlib.md5(original.encode(), usedforsecurity=False).hexdigest()
        )
        if not cached_csv.exists() or (
            datetime.now(UTC) - datetime.fromtimestamp(cached_csv.stat().st_mtime, UTC)
            > timedelta(seconds=1)  # hours=1)
        ):
            logging.warning("Refreshing CSV")
            urlretrieve(Env().str("UPSTREAM_NUXT") + original, cached_csv)  # noqa: S310
        return pl.read_csv(
            cached_csv,
            try_parse_dates=True,
            schema_overrides={
                "scot_code_departement": pl.String(),
                "collectivite_code": pl.String(),
            },
        )

    @pytest.mark.django_db
    def test_all(
        self,
        client: Client,
        django_assert_num_queries: DjangoAssertNumQueries,
    ) -> None:
        nuxt = self._retrieve_nuxt("/api/urba/exports/scots")

        with django_assert_num_queries(4):
            response = client.get(reverse("api_scots"))

        django = pl.read_csv(
            response.content,
            try_parse_dates=True,
            schema_overrides={
                "scot_code_departement": pl.String(),
                "collectivite_code": pl.String(),
            },
        )  # .sort("collectivite_code", "collectivite_type", "procedure_id")

        differences = pl.col("scot_codecollectivite").is_in(self.DIFFERENCES).not_()
        nuxt = nuxt.sort("scot_codecollectivite", "pa_id", "pc_id").filter(differences)
        django = django.sort("scot_codecollectivite", "pa_id", "pc_id").filter(
            differences
        )

        foo = 0
        for nuxt_row, django_row in zip(
            nuxt.iter_rows(named=True), django.iter_rows(named=True), strict=True
        ):
            colonnes_filtrees = (
                "annee_cog",
                "scot_code_region",
                "scot_libelle_region",
                "scot_code_departement",
                "scot_lib_departement",
                "scot_codecollectivite",
                "scot_code_type_collectivite",
                "scot_nom_collectivite",
                "pa_id",
                "pa_nom_schema",
                "pa_noserie_procedure",
                "pa_scot_interdepartement",
                "pa_date_publication_perimetre",
                # "pa_date_prescription",
                "pa_date_arret_projet",
                "pa_date_approbation",
                "pa_date_fin_echeance",
                # "pa_nombre_communes",
                "pc_id",
                "pc_nom_schema",
                "pc_noserie_procedure",
                "pc_proc_elaboration_revision",
                "pc_scot_interdepartement",
                "pc_date_publication_perimetre",
                # "pc_date_prescription",
                "pc_date_arret_projet",
                # "pc_nombre_communes",
            )

            nuxt_row = {  # noqa: PLW2901
                k: str(v or "").capitalize()
                for k, v in nuxt_row.items()
                if k in colonnes_filtrees
            }
            django_row = {  # noqa: PLW2901
                k: str(v).capitalize()
                for k, v in django_row.items()
                if k.startswith(colonnes_filtrees)
            }

            assert nuxt_row == django_row, foo

            foo += 1  # noqa: SIM113


class TestCommunes:
    COMD_PAS_PRIS_EN_COMPTE = (
        1130,  # COMD avec même code que COM
        2018,  # COMD avec même code que COM
        2053,  # COMD avec même code que COM
        3168,
        11251,
        12224,
        14098,
        14666,
        15141,
        16192,
        16286,
        19010,
        19098,
        19123,
        21178,
        24087,
        24117,
        24142,
        24316,
        24376,
        25575,
        26001,
        26086,
        27107,
        27448,
        29076,
        29227,
        31471,
        33008,
        33380,
        34246,
        35163,
        38292,
        38297,
        38439,
        39137,
        39331,
        39339,
        39491,
        39577,
        45051,
        45129,
        48009,
        48027,
        48099,
        49029,
        49067,
        50142,
        50260,
        50388,
        50591,
        51171,
        52140,
        52405,
        54099,
        55537,
        56144,  # COM avec des COMD
        56173,  # COM avec COMD disparues,
        57578,
        60088,
        60245,
        60256,
        60694,
        61168,
        61211,
        61486,
        65399,
        68006,
        68143,
        70285,
        70489,
        70491,
        73187,
        73227,
        73236,
        73257,
        76164,
        76258,
        77109,
        77504,
        78551,
        79061,
        79083,
        80442,
        85162,
        85177,
        86123,
        88465,
        89130,
        91228,
    )

    NUXT_TROUVE_PAS_EN_COURS = (
        7342,
        9125,
        9160,
        12012,
        12018,
        26243,
        26373,
        28330,
        31539,
        35134,  # Nuxt ne voit pas bien l'abandon invalide
        39188,
        39396,
        46053,
        46223,
        46249,
        46270,
        46338,
        54364,
        57107,
        77315,
        77341,
        77413,
        77522,
        86112,
        86191,
    )

    EN_COURS_SANS_EVENEMENTS = (
        26117,
        26364,
        31113,
        34303,
        35359,
        37003,
        74056,
        83034,
        83047,
        83069,
        83098,
        83126,
        83129,
        83137,
        83144,
        84006,
        84050,
    )

    NUXT_DONNE_ABROGATION_OPPOSABLE = (15006, 70296, 73189)

    DEUX_OPPOSABLES_MEME_JOUR = (
        9336,
        26179,
        14365,
        44213,
        63284,
        68298,
        89264,
    )

    ABANDON_MEME_JOUR_PRESCRIPTION = (
        6003,  # https://docurba.beta.gouv.fr/frise/55bccdeb-e1ae-4c3e-9cc2-9cb713ecde25
        11221,  # Cas compliqué
        21054,
        25113,
        25511,
        27056,
        30032,
        30152,
        33310,
        33402,
        77260,
        78520,
    )

    PROCEDURES_DOUBLONS = (
        # 31005,
        # 31023,
        # 31028,
        # 31039,
        # 31063,
        # 31083,
        # 31086,
        # 31109,
        # 35012,
        # 35030,
        # 35054,
        # 35098,
        # 35124,
        # 35212,
        # 35218,
        # 35231,
        # 35249,
        # 35316,
        # 35332,
        # 35322,
        # 35343,
        84129,
    )

    POS_BIZARRE = (
        42127,
        54261,
        60006,
        69027,
        78152,
        80261,
    )

    PLUSIEURS_EN_COURS = (
        45191,
        58172,  # PLU devrait avoir priorité
        68188,
    )

    NUXT_SE_TROMPE_APPROBATION = (77207,)

    def _retrieve_nuxt(self, original: str) -> pl.DataFrame:
        cached_csv = (
            Path("core/tests/nuxt_snapshots")
            / hashlib.md5(original.encode(), usedforsecurity=False).hexdigest()
        )
        if not cached_csv.exists() or (
            datetime.now(UTC) - datetime.fromtimestamp(cached_csv.stat().st_mtime, UTC)
            > timedelta(hours=1)
            # > timedelta(seconds=1)
        ):
            logging.warning("Refreshing CSV")
            urlretrieve(Env().str("UPSTREAM_NUXT") + original, cached_csv)  # noqa: S310
        return pl.read_csv(
            cached_csv,
            try_parse_dates=True,
            schema_overrides={
                "cp_siren": pl.String(),
                "pa_plui_valant_scot": pl.String(),
                "pa_pdu_obligatoire": pl.String(),
                "pa_annee_prescription": pl.String(),
                "pa_annee_approbation": pl.String(),
                "pa_date_prescription": pl.String(),
                "pa_date_approbation": pl.String(),
                "pa_delai_approbation": pl.String(),
                "pa_num_procedure_sudocuh": pl.String(),
            },
        )

    @pytest.mark.parametrize(
        "departement",
        [
            f"{i:0>2}"
            for i in ["976", "974", "973", "972", "971", "2B", "2A", *range(95, 0, -1)]
        ],
    )
    @pytest.mark.django_db
    def test_departement(
        self,
        client: Client,
        departement: str,
    ) -> None:
        nuxt = self._retrieve_nuxt(
            f"/api/urba/exports/communes?departementCode={departement}"
        ).sort("code_insee")

        # with django_assert_num_queries(4):
        response = client.get(
            "/api/communes", query_params={"departement": departement}
        )

        django = pl.read_csv(
            response.content,
            try_parse_dates=True,
            schema_overrides={
                "cp_siren": pl.String(),
                "pa_plui_valant_scot": pl.String(),
                "pa_pdu_obligatoire": pl.String(),
                "pa_annee_prescription": pl.String(),
                "pa_annee_approbation": pl.String(),
                "pa_date_prescription": pl.String(),
                "pa_date_approbation": pl.String(),
                "pa_delai_approbation": pl.String(),
                "pa_num_procedure_sudocuh": pl.String(),
            },
        ).sort("code_insee")

        differences = (
            pl.col("code_insee")
            .is_in(
                self.COMD_PAS_PRIS_EN_COMPTE
                + self.NUXT_TROUVE_PAS_EN_COURS
                + self.PROCEDURES_DOUBLONS
                + self.NUXT_DONNE_ABROGATION_OPPOSABLE
                + self.EN_COURS_SANS_EVENEMENTS
                + self.DEUX_OPPOSABLES_MEME_JOUR
                + self.POS_BIZARRE
                + self.PLUSIEURS_EN_COURS
                + self.NUXT_SE_TROMPE_APPROBATION
                + self.ABANDON_MEME_JOUR_PRESCRIPTION
            )
            .not_()
        )
        nuxt = nuxt.filter(differences)
        django = django.filter(differences)

        foo = 0
        for nuxt_row, django_row in zip(
            nuxt.iter_rows(named=True), django.iter_rows(named=True), strict=True
        ):
            colonnes_filtrees = (
                "annee_cog",
                "code_insee",
                "com_nom",
                "com_code_departement",
                "com_nom_departement",
                "com_code_region",
                "com_nom_region",
                # "com_nouvelle",  # On ignore car Nuxt retourne toujours False en comparant des strings et des int
                "epci_reg",
                "epci_region",
                "epci_dept",
                "epci_departement",
                "epci_type",
                "epci_nom",
                "epci_siren",
                # Collectivité Porteuse
                "collectivite_porteuse",
                "cp_type",
                "cp_code_region",
                "cp_lib_region",
                "cp_code_departement",
                "cp_nom_departement",
                "cp_nom",
                "cp_siren",
                "cp_code_insee",
                "plan_code_etat_simplifie",
                "plan_libelle_code_etat_simplifie",
                "plan_code_etat_complet",
                "plan_libelle_code_etat_complet",
                # En cours
                "pc_docurba_id",
                "pc_num_procedure_sudocuh",
                "pc_type_procedure",
                "pc_date_prescription",
                "pc_date_arret_projet",
                "pc_date_pac",
                "pc_date_pac_comp",
                "pc_plui_valant_scot",
                "pc_sectoriel",
                "pc_pdu_obligatoire",
                "pc_nom_sst",
                "pc_cout_sst_ht",
                "pc_cout_sst_ttc",
                # Approuvé
                "pa_docurba_id",
                "pa_num_procedure_sudocuh",
                "pa_type_procedure",
                "pa_sectoriel",
                "pa_date_prescription",
                "pa_date_arret_projet",
                "pa_date_pac",
                "pa_date_pac_comp",
                "pa_date_approbation",
                "pa_annee_prescription",
                "pa_annee_approbation",
                "pa_delai_approbation",
                "pa_plui_valant_scot",
                "pa_pdu_obligatoire",
                "pa_nom_sst",
                "pa_cout_sst_ht",
                "pa_cout_sst_ttc",
            )

            if django_row["pc_date_prescription"] == "0000-00-00":
                django_row["pc_date_prescription"] = ""
            nuxt_row = {  # noqa: PLW2901
                k: str(v or "").capitalize().strip()
                for k, v in nuxt_row.items()
                if k in colonnes_filtrees
            }
            django_row = {  # noqa: PLW2901
                k: str(v or "").capitalize().strip()
                for k, v in django_row.items()
                if k in colonnes_filtrees
            }

            assert nuxt_row == django_row, foo

            foo += 1  # noqa: SIM113
