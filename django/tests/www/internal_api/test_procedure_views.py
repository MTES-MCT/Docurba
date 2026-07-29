import datetime
import random
import uuid
from urllib.parse import urlencode

import pytest
from django.urls import reverse
from pytest_django import DjangoAssertNumQueries
from pytest_django.asserts import assertQuerySetEqual
from syrupy.assertion import SnapshotAssertion

from docurba.core import enums as core_enums
from docurba.core import models as core_models
from docurba.users import models as users_models
from tests.conftest import APIClient, SupabaseApiTestClient
from tests.core import factories as core_factories
from tests.users.factories import ProfileFactory

BASE_QUERIES = (
    1  # session
    + 1  # profiles for authentication check
    + 1  # count for pagination
    + 1  # procedures details
    + 1  # doc_frise_events for with_events()
    + 1  # topics
    + 1  # perimetre
)


@pytest.mark.django_db
class TestProcedureList:
    def _create_collectivite_perimetre_profile(
        self,
    ) -> tuple[core_models.Collectivite, core_models.Commune, users_models.Profile]:
        # This test assumes no one has the jurisdiction because
        # collectivite.competence_plan and collectivite.competence_schema
        # are False by default.
        # In this particular case, which should not happen in the reality,
        # the system chooses the collectivite to be the `collectivite porteuse``.
        # Jurisdiction are omitted in this test to avoid `collectivite porteuse` differences.
        # They are tested separately.
        # TODO: get collectivite from the logged in user depending on the user rights.  # noqa: FIX002
        collectivite = core_factories.CollectiviteFactory(
            for_snapshot=True,
            with_flat_members=True,
            with_flat_members__for_snapshot=True,
        )
        perimetre_insee_codes = collectivite.flat_members.filter(
            type=core_enums.CommuneType.COM
        ).values_list("code_insee", flat=True)
        communes = core_models.Commune.objects.filter(
            code_insee__in=perimetre_insee_codes
        )
        logged_in_profile = ProfileFactory(collectivite=collectivite)
        return (
            collectivite,
            sorted(communes, key=lambda c: c.code_insee),
            logged_in_profile,
        )

    @property
    def url(self) -> str:
        return reverse("internal_api:procedures-list")

    @pytest.mark.parametrize("status", core_enums.ProcedureStatusChoices)
    def test_filter_status(
        self,
        status: str,
        api_client_with_auth: SupabaseApiTestClient,
        django_assert_num_queries: DjangoAssertNumQueries,
    ) -> None:
        collectivite, communes, logged_in_profile = (
            self._create_collectivite_perimetre_profile()
        )
        expected_procedure = core_factories.ProcedureFactory(
            status=status,
            collectivite_porteuse=collectivite,
            with_perimetre=communes,
        )
        excluded_status = random.choice(  # noqa: S311
            [
                p_status
                for p_status in core_enums.ProcedureStatusChoices
                if p_status != status
            ]
        )
        core_factories.ProcedureFactory(
            status=excluded_status,
            collectivite_porteuse=collectivite,
            with_perimetre=communes,
        )
        with (
            api_client_with_auth(logged_in_profile) as api_client,
            django_assert_num_queries(BASE_QUERIES),
        ):
            response = api_client.get(f"{self.url}?status={status}")
        assert response.status_code == 200
        assert response.json()["count"] == 1
        assert response.json()["results"][0]["status"] == status.value
        assert response.json()["results"][0]["id"] == str(expected_procedure.id)

    def test_filter_many_statuses(
        self,
        api_client_with_auth: SupabaseApiTestClient,
        django_assert_num_queries: DjangoAssertNumQueries,
    ) -> None:
        collectivite, communes, logged_in_profile = (
            self._create_collectivite_perimetre_profile()
        )
        expected_procedure_one = core_factories.ProcedureFactory(
            status=core_enums.ProcedureStatusChoices.OPPOSABLE,
            collectivite_porteuse=collectivite,
            with_perimetre=communes,
        )
        expected_procedure_two = core_factories.ProcedureFactory(
            status=core_enums.ProcedureStatusChoices.EN_COURS,
            collectivite_porteuse=collectivite,
            with_perimetre=communes,
        )
        not_expected_procedure = core_factories.ProcedureFactory(
            status=core_enums.ProcedureStatusChoices.ABANDON,
            collectivite_porteuse=collectivite,
            with_perimetre=communes,
        )
        with (
            api_client_with_auth(logged_in_profile) as api_client,
            django_assert_num_queries(BASE_QUERIES),
        ):
            response = api_client.get(
                f"{self.url}?status={core_enums.ProcedureStatusChoices.OPPOSABLE}&status={core_enums.ProcedureStatusChoices.EN_COURS}"
            )
        assert response.status_code == 200
        assert response.json()["count"] == 2
        results_procedure_ids = [result["id"] for result in response.json()["results"]]
        assert sorted(
            [str(expected_procedure_one.id), str(expected_procedure_two.id)]
        ) == sorted(results_procedure_ids)
        assert not_expected_procedure not in results_procedure_ids

    @pytest.mark.parametrize(
        ("query_params"),
        [
            pytest.param(
                {"is_principale": "true"},
                id="is_principale",
            ),
            pytest.param(
                {"is_principale": "false"},
                id="is_principale",
            ),
            pytest.param(
                {},
                id="default_value",
            ),
        ],
    )
    def test_filter_is_principale(
        self,
        query_params: dict,
        api_client_with_auth: SupabaseApiTestClient,
        django_assert_num_queries: DjangoAssertNumQueries,
        snapshot: SnapshotAssertion,
    ) -> None:
        collectivite, communes, logged_in_profile = (
            self._create_collectivite_perimetre_profile()
        )
        core_factories.ProcedureFactory(
            is_principale=True,
            collectivite_porteuse=collectivite,
            with_perimetre=communes,
        )
        core_factories.ProcedureFactory(
            is_principale=False,
            collectivite_porteuse=collectivite,
            with_perimetre=communes,
        )
        with (
            api_client_with_auth(logged_in_profile) as api_client,
            django_assert_num_queries(BASE_QUERIES),
        ):
            response = api_client.get(f"{self.url}?{urlencode(query_params)}")
        assert response.status_code == 200
        assert response.json()["count"] == snapshot()

    @pytest.mark.parametrize(
        ("query_params"),
        [
            pytest.param(
                {"collectivites_porteuses": ["253000020", "30001"]},
                id="several_collectivites_porteuses",
            ),
            pytest.param(
                {"collectivites_porteuses": ["253000020"]},
                id="one_collectivite_porteuse_siren",
            ),
            pytest.param(
                {"collectivites_porteuses": ["30001"]},
                id="one_collectivite_porteuse_code_insee",
            ),
            # Don't raise an error for the moment.
            pytest.param(
                {"collectivites_porteuses": ["00000"]},
                id="not_found",
            ),
            pytest.param(
                {},
                id="default_value",
            ),
        ],
    )
    def test_filter_collectivites_porteuses(
        self,
        query_params: dict,
        snapshot: SnapshotAssertion,
        api_client_with_auth: SupabaseApiTestClient,
    ) -> None:
        collectivite, communes, logged_in_profile = (
            self._create_collectivite_perimetre_profile()
        )
        core_factories.ProcedureFactory(
            with_perimetre=[communes[0]],
            collectivite_porteuse=collectivite,
            numero="1",
            for_snapshot=True,
            status=core_enums.ProcedureStatusChoices.EN_COURS,
        )
        collectivite_with_code_insee = core_factories.CommuneFactory(
            departement__code_insee="30",
            code_insee="30001",
            type=core_enums.TypeCollectivite.COM,
            nom="Aigaliers",
        )
        core_factories.ProcedureFactory(
            pk=uuid.UUID("1cd65b57-7027-4aa5-8d19-222222222222"),
            name="Révision du PLU d'Aigaliers",
            status=core_enums.ProcedureStatusChoices.EN_COURS,
            collectivite_porteuse=collectivite_with_code_insee,
            with_perimetre=[collectivite_with_code_insee],
            numero="1",
            project=core_factories.ProjectFactory(
                id=uuid.UUID("1cd65b57-7027-4aa5-8d19-333333333333")
            ),
            doc_type=core_enums.TypeDocument.PLU,
        )
        aigremont = core_factories.CommuneFactory(code_insee="30002")
        core_factories.ProcedureFactory(
            pk=uuid.UUID("1cd65b57-7027-4aa5-8d19-444444444444"),
            name="Révision du PLU d'Aigremont",
            status=core_enums.ProcedureStatusChoices.EN_COURS,
            collectivite_porteuse=aigremont,
            with_perimetre=[aigremont],
            numero="1",
            project=core_factories.ProjectFactory(
                id=uuid.UUID("1cd65b57-7027-4aa5-8d19-555555555555")
            ),
            doc_type=core_models.core_enums.TypeDocument.PLU,
        )
        with api_client_with_auth(logged_in_profile) as api_client:
            response = api_client.get(
                f"{self.url}?{urlencode(query_params, doseq=True)}"
            )
        assert response.status_code == 200
        assert response.json()["results"] == snapshot()

    @pytest.mark.parametrize(
        ("query_params"),
        [
            pytest.param(
                {"communes_perimetre": ["30032", "30034"]},
                id="several_communes",
            ),
            pytest.param(
                {"communes_perimetre": ["30032"]},
                id="one_commune",
            ),
            # Don't raise an error for the moment.
            pytest.param(
                {"communes_perimetre": ["00000"]},
                id="not_found",
            ),
            pytest.param(
                {},
                id="default_value",
            ),
        ],
    )
    def test_filter_communes_perimetre(
        self,
        query_params: dict,
        snapshot: SnapshotAssertion,
        api_client_with_auth: SupabaseApiTestClient,
    ) -> None:
        collectivite, communes, logged_in_profile = (
            self._create_collectivite_perimetre_profile()
        )
        procedure = core_factories.ProcedureFactory(
            with_perimetre=[communes[0]],
            collectivite_porteuse=collectivite,
            numero="1",
            for_snapshot=True,
            status=core_enums.ProcedureStatusChoices.EN_COURS,
        )
        core_factories.ProcedureFactory(
            pk=uuid.UUID("1cd65b57-7027-4aa5-8d19-222222222222"),
            name="Seconde procédure",
            status=core_enums.ProcedureStatusChoices.EN_COURS,
            collectivite_porteuse=collectivite,
            with_perimetre=[communes[1]],
            numero="1",
            project=procedure.project,
            doc_type=core_models.core_enums.TypeDocument.PLU,
        )
        core_factories.ProcedureFactory(
            pk=uuid.UUID("1cd65b57-7027-4aa5-8d19-333333333333"),
            name="Troisième procédure",
            status=core_enums.ProcedureStatusChoices.EN_COURS,
            collectivite_porteuse=collectivite,
            with_perimetre=[communes[2]],
            numero="1",
            project=procedure.project,
            doc_type=core_models.core_enums.TypeDocument.PLU,
        )
        with api_client_with_auth(logged_in_profile) as api_client:
            response = api_client.get(
                f"{self.url}?{urlencode(query_params, doseq=True)}"
            )
        assert response.status_code == 200
        assert response.json()["results"] == snapshot()

    def test_serializer_with_topics(
        self,
        api_client_with_auth: SupabaseApiTestClient,
        django_assert_num_queries: DjangoAssertNumQueries,
    ) -> None:
        collectivite, communes, logged_in_profile = (
            self._create_collectivite_perimetre_profile()
        )
        expected_topic = core_models.Topic.objects.get(name="zan")
        core_factories.ProcedureFactory(
            collectivite_porteuse=collectivite,
            with_perimetre=communes,
            with_topics=True,
            with_topics__list=[expected_topic],
        )
        with (
            api_client_with_auth(logged_in_profile) as api_client,
            django_assert_num_queries(BASE_QUERIES),
        ):
            response = api_client.get(f"{self.url}")
        assert response.status_code == 200
        assert response.json()["results"][0]["topics"] == [{"name": "zan"}]

    def test_serializer_name(
        self,
        api_client_with_auth: SupabaseApiTestClient,
        django_assert_num_queries: DjangoAssertNumQueries,
    ) -> None:
        collectivite, communes, logged_in_profile = (
            self._create_collectivite_perimetre_profile()
        )
        core_factories.ProcedureFactory(
            name="",
            collectivite_porteuse=collectivite,
            with_perimetre=communes[:1],
            id=uuid.UUID("11111111-7027-4aa5-8d19-222222222222"),
            for_snapshot=True,
        )
        core_factories.ProcedureFactory(
            name="",
            id=uuid.UUID("22222222-7027-4aa5-8d19-222222222222"),
            with_perimetre=communes,
        )
        core_factories.ProcedureFactory(
            name="",
            id=uuid.UUID("33333333-7027-4aa5-8d19-333333333333"),
            with_perimetre=communes,
        )
        with (
            api_client_with_auth(logged_in_profile) as api_client,
            django_assert_num_queries(BASE_QUERIES),
        ):
            response = api_client.get(f"{self.url}")
        assert response.status_code == 200
        assert response.json()["results"][0]["name"] == "Élaboration PLU Beaucaire"

    def test_serializer_doc_type(
        self,
        api_client_with_auth: SupabaseApiTestClient,
        django_assert_num_queries: DjangoAssertNumQueries,
    ) -> None:
        """The exposed docType is computed in Procedure.type_document.

        We don't need to fully test it here because it's already tested in core models tests.
        """
        collectivite, communes, logged_in_profile = (
            self._create_collectivite_perimetre_profile()
        )
        # doc_type matches type_document
        core_factories.ProcedureFactory(
            collectivite_porteuse=collectivite,
            with_perimetre=communes,
            doc_type=core_enums.TypeDocument.PLUI,
        )
        with (
            api_client_with_auth(logged_in_profile) as api_client,
            django_assert_num_queries(BASE_QUERIES),
        ):
            response = api_client.get(f"{self.url}")
        assert response.status_code == 200
        assert response.json()["results"][0]["docType"] == "PLUi"

        # doc_type is PLU but area is composed of many towns
        core_factories.ProcedureFactory(
            collectivite_porteuse=collectivite,
            with_perimetre=communes,
            doc_type=core_enums.TypeDocument.PLU,
        )
        with (
            api_client_with_auth(logged_in_profile) as api_client,
            django_assert_num_queries(BASE_QUERIES),
        ):
            response = api_client.get(f"{self.url}")
        assert response.status_code == 200
        assert response.json()["results"][0]["docType"] == "PLUi"

    def test_serializer_nominal_principal_procedure(
        self,
        api_client_with_auth: SupabaseApiTestClient,
        snapshot: SnapshotAssertion,
        django_assert_num_queries: DjangoAssertNumQueries,
    ) -> None:
        collectivite, communes, logged_in_profile = (
            self._create_collectivite_perimetre_profile()
        )
        core_factories.ProcedureFactory(
            collectivite_porteuse=collectivite,
            with_perimetre=communes,
            numero="1",
            for_snapshot=True,
            status=core_enums.ProcedureStatusChoices.EN_COURS,
        )
        with (
            api_client_with_auth(logged_in_profile) as api_client,
            django_assert_num_queries(BASE_QUERIES),
        ):
            response = api_client.get(f"{self.url}")
        assert response.status_code == 200
        assert response.json() == snapshot()

    def test_serializer_nominal_secondary_procedure(
        self,
        api_client_with_auth: SupabaseApiTestClient,
        snapshot: SnapshotAssertion,
        django_assert_num_queries: DjangoAssertNumQueries,
    ) -> None:
        collectivite, communes, logged_in_profile = (
            self._create_collectivite_perimetre_profile()
        )
        principal_procedure = core_factories.ProcedureFactory(
            pk=uuid.UUID("1cd65b57-7027-4aa5-8d19-111111111111"),
            collectivite_porteuse=collectivite,
            with_perimetre=communes,
            numero="1",
            for_snapshot=True,
            status=core_enums.ProcedureStatusChoices.EN_COURS,
        )
        secondary_procedure = core_factories.ProcedureFactory(
            pk=uuid.UUID("1cd65b57-7027-4aa5-8d19-222222222222"),
            parente=principal_procedure,
            name="Révision du PLU de Nantes",
            collectivite_porteuse=collectivite,
            with_perimetre=communes,
            numero="1",
            project=principal_procedure.project,
            doc_type=core_enums.TypeDocument.PLU,
        )
        with (
            api_client_with_auth(logged_in_profile) as api_client,
            django_assert_num_queries(BASE_QUERIES),
        ):
            response = api_client.get(f"{self.url}")
        assert response.status_code == 200
        # Results are sorted by ID.
        assert response.json()["results"][1]["id"] == str(secondary_procedure.pk)
        assert response.json()["results"][1]["parentId"] == str(principal_procedure.pk)
        assert response.json()["results"][1] == snapshot()

    def test_serializer_with_approval_date(
        self,
        api_client_with_auth: SupabaseApiTestClient,
        django_assert_num_queries: DjangoAssertNumQueries,
    ) -> None:
        collectivite, communes, logged_in_profile = (
            self._create_collectivite_perimetre_profile()
        )
        core_factories.ProcedureFactory(
            collectivite_porteuse=collectivite,
            with_perimetre=communes,
            with_event=True,
            with_event__category=core_models.EventCategory.APPROUVE,
            with_event__date_evenement=datetime.date(2026, 10, 6),
        )
        with (
            api_client_with_auth(logged_in_profile) as api_client,
            django_assert_num_queries(BASE_QUERIES),
        ):
            response = api_client.get(f"{self.url}")
        assert response.status_code == 200
        assert response.json()["results"][0]["approval_date"] == "2026-10-06"

    def test_serializer_with_communes_is_opposable(
        self,
        api_client_with_auth: SupabaseApiTestClient,
        django_assert_num_queries: DjangoAssertNumQueries,
    ) -> None:
        collectivite, communes, logged_in_profile = (
            self._create_collectivite_perimetre_profile()
        )
        procedure = core_factories.ProcedureFactory(
            collectivite_porteuse=collectivite,
            with_perimetre=communes,
        )
        perimetre_through = procedure.perimetre_through.order_by(
            "commune__code_insee"
        ).first()
        perimetre_through.opposable = True
        perimetre_through.save()
        with (
            api_client_with_auth(logged_in_profile) as api_client,
            django_assert_num_queries(BASE_QUERIES),
        ):
            response = api_client.get(f"{self.url}")
        assert response.status_code == 200
        assert response.json()["results"][0]["perimetre"][0]["is_opposable"] == "True"
        for i in range(1, len(communes) - 1):
            assert (
                response.json()["results"][0]["perimetre"][i]["is_opposable"] == "False"
            )


@pytest.mark.django_db
class TestProcedureName:
    base_queries = 4

    @property
    def url(self) -> str:
        return reverse("internal_api:procedures-compute-name")

    def test_principal_procedure_name__one_town(
        self,
        api_client: APIClient,
        django_assert_num_queries: DjangoAssertNumQueries,
    ) -> None:
        commune = core_factories.CommuneFactory(for_snapshot=True)

        query_params = {
            "type": core_enums.ProcedureType.ELABORATION,
            "docType": core_enums.TypeDocument.PLU,
            "perimetreCodes": [
                commune.code_insee,
            ],  # procedure creation is on active communes only.
            "collectiviteCode": commune.code_insee,
        }
        with (
            django_assert_num_queries(self.base_queries),
        ):
            response = api_client.get(
                f"{self.url}?{urlencode(query_params, doseq=True)}"
            )
        assert response.status_code == 200
        assert response.json()["name"] == "Elaboration PLU Beaucaire"

    def test_principal_procedure_name__multiple_towns(
        self,
        api_client: APIClient,
        django_assert_num_queries: DjangoAssertNumQueries,
    ) -> None:
        communes = core_factories.CommuneFactory.create_batch(2)
        collectivite = core_factories.CollectiviteFactory(
            for_snapshot=True,
            with_members=True,
            with_members__list=[commune.collectivite_ptr for commune in communes],
        )

        query_params = {
            "type": core_enums.ProcedureType.ELABORATION,
            "docType": core_enums.TypeDocument.PLU,
            "perimetreCodes": [
                commune.code_insee for commune in communes
            ],  # procedure creation is on active communes only.
            "collectiviteCode": collectivite.siren,
        }
        with (
            django_assert_num_queries(self.base_queries),
        ):
            response = api_client.get(
                f"{self.url}?{urlencode(query_params, doseq=True)}"
            )
        assert response.status_code == 200
        assert (
            response.json()["name"]
            == "Elaboration PLUi Syndicat mixte d'équipement de la commune de Beaucaire"
        )

    def test_secondary_procedure_name(
        self,
        api_client: APIClient,
        django_assert_num_queries: DjangoAssertNumQueries,
    ) -> None:
        communes = core_factories.CommuneFactory.create_batch(2)
        collectivite_porteuse = core_factories.CollectiviteFactory(
            for_snapshot=True,
            with_members=True,
            with_members__list=[commune.collectivite_ptr for commune in communes],
        )
        principal_procedure = core_factories.ProcedureFactory(
            for_snapshot=True,
            collectivite_porteuse=collectivite_porteuse,
            with_perimetre=communes,
        )

        query_params = {
            "type": core_enums.ProcedureType.MODIFICATION,
            "parentId": str(principal_procedure.pk),
            "number": "1",
        }
        with django_assert_num_queries(self.base_queries):
            response = api_client.get(
                f"{self.url}?{urlencode(query_params, doseq=True)}"
            )
        assert response.status_code == 200
        assert (
            response.json()["name"]
            == "Modification PLUi Syndicat mixte d'équipement de la commune de Beaucaire"
        )

    @pytest.mark.parametrize(
        "query_params",
        [
            pytest.param(
                {
                    "parentId": "",
                    "collectiviteCode": "253000020",
                    "docType": core_enums.TypeDocument.PLU,
                    "type": core_enums.ProcedureType.ELABORATION,
                },
                id="missing perimetreCodes",
            ),
            pytest.param(
                {
                    "parentId": "",
                    "perimetreCodes": "30032",
                    "docType": core_enums.TypeDocument.PLU,
                    "type": core_enums.ProcedureType.ELABORATION,
                },
                id="missing collectiviteCode",
            ),
            pytest.param(
                {
                    "parentId": "",
                    "collectiviteCode": "253000020",
                    "perimetreCodes": "30032",
                    "type": core_enums.ProcedureType.ELABORATION,
                },
                id="missing docType",
            ),
        ],
    )
    def test_validation_error(
        self,
        api_client: APIClient,
        query_params: dict,
    ) -> None:
        commune = core_factories.CommuneFactory(for_snapshot=True)
        core_factories.CollectiviteFactory(
            for_snapshot=True,
            with_members=True,
            with_members__list=[commune],
        )

        response = api_client.get(f"{self.url}?{urlencode(query_params, doseq=True)}")
        assert response.status_code == 400
        assert (
            response.json()["non_field_errors"][0]
            == "Missing principal procedure required field. Mandatory fields are: ['collectiviteCode', 'perimetreCodes', 'doc_type']"
        )

    def test_parente_procedure_not_found(
        self,
        api_client: APIClient,
    ) -> None:
        commune = core_factories.CommuneFactory(for_snapshot=True)
        core_factories.CollectiviteFactory(
            for_snapshot=True,
            with_members=True,
            with_members__list=[commune],
        )
        query_params = {
            "parentId": "fb48c069-33c6-4ed2-9db3-054e99ea7981",
            "type": core_enums.ProcedureType.ELABORATION,
        }

        response = api_client.get(f"{self.url}?{urlencode(query_params, doseq=True)}")
        assert response.status_code == 400
        assert (
            response.json()["parentId"][0]
            == "The principal procedure has not been found."
        )

    def test_collectivite_porteuse_not_found(
        self,
        api_client: APIClient,
    ) -> None:
        core_factories.CommuneFactory(for_snapshot=True)
        query_params = {
            "parentId": "",
            "collectiviteCode": "000000000",
            "perimetreCodes": "30032",
            "type": core_enums.ProcedureType.ELABORATION,
            "docType": core_enums.TypeDocument.PLU,
        }

        response = api_client.get(f"{self.url}?{urlencode(query_params, doseq=True)}")
        assert response.status_code == 400
        assert (
            response.json()["collectiviteCode"][0]
            == 'The "collectivité porteuse" has not been found.'
        )

    def test_perimetre_not_found(
        self,
        api_client: APIClient,
    ) -> None:
        commune = core_factories.CommuneFactory(for_snapshot=True)
        collectivite = core_factories.CollectiviteFactory(
            for_snapshot=True,
            with_members=True,
            with_members__list=[commune],
        )
        query_params = {
            "parentId": "",
            "collectiviteCode": collectivite.siren,
            "perimetreCodes": ["30032", "00000"],
            "type": core_enums.ProcedureType.ELABORATION,
            "docType": core_enums.TypeDocument.PLU,
        }

        response = api_client.get(f"{self.url}?{urlencode(query_params, doseq=True)}")
        assert response.status_code == 400
        assert (
            response.json()["perimetreCodes"][0]
            == "Following communes have not been found: ['00000']."
        )


@pytest.mark.django_db
class TestPrincipalProcedureCreation:
    # There is at least one N+1 hiding somewhere.
    # We decided to ignore it for the following weeks because:
    # - the procedure.type_document will be removed when procedure.doc_type will be cleaned
    # - the procedure sectoriality should be stored in a column
    # - procedure.current_perimetre and procedure.departements will be deleted soon.
    PP_BASE_QUERIES = (
        3  # for validating params. => OK
        + 1  # for saving the procedure.
        + 1  # to get the perimetre # 7
        + 1  # to save the perimetre # 8
        + 1  # to create the project # 9
        + 1  # to list topics # 10
        + 1  # to create procedure topics # 11
        + 1  # to save it again # 12
        + 7  # to serialize # 19
    )
    PS_BASE_QUERIES = (
        3  # for validating params. => OK
        + 1  # to fetch the principal procedure => OK
        + 1  # for creating => OK # 5
        + 3  # for saving the perimeter # 8
        + 1  # for getting the topics # 9
        + 1  # for saving ProcedureTopic # 10
        + 1  # for computing procedure.doc_type for procedure.type_document # 11
        + 1  # to save the instance again # 12
        + 8  # to serialize the result # 20
    )

    @property
    def url(self) -> str:
        return reverse("internal_api:procedures-list")

    def _default_post_data(
        self,
        perimetre: list[core_models.Commune] | None = None,
        collectivite: core_models.Collectivite | None = None,
    ) -> dict:
        return {
            "type": core_enums.ProcedureType.ABROGATION,
            "collectiviteCode": collectivite.siren if collectivite else "",
            "perimetreCodes": perimetre or "",
            "docType": core_enums.TypeDocument.PLUI,
            "number": "",
            "startedBeforeHuwartLaw": True,
            "topicsList": ["zan", "coastline", "other"],
            "otherTopicComment": "I love coastlines.",
        }

    def _assert_default_procedure_creation(
        self,
        procedure: core_models.Procedure,
        logged_in_profile: users_models.Profile,
        post_data: dict,
    ) -> None:
        assert procedure.started_before_huwart_law is True
        assert procedure.type == core_enums.ProcedureType.ABROGATION
        assert procedure.doc_type == post_data["docType"]
        assert procedure.numero == "1"
        assert procedure.name_complement == post_data.get("nameComplement", "")
        assert procedure.shareable
        assert procedure.parente is None
        assert procedure.is_principale is True
        assert procedure.status == "en cours"
        assert procedure.is_sectoriel is None
        assert procedure.vaut_PDM is False
        assert procedure.vaut_PLH is False
        assert procedure.testing is True
        assert procedure.owner_id == uuid.UUID(logged_in_profile.user_id)

    def _assert_default_commune_procedure_creation(
        self, procedure: core_models.Procedure
    ) -> None:
        for commune_procedure in procedure.perimetre_through.select_related(
            "commune__departement"
        ).all():
            assert (
                commune_procedure.collectivite_code
                == commune_procedure.commune.code_insee
            )
            assert commune_procedure.collectivite_type == commune_procedure.commune.type
            assert (
                commune_procedure.departement
                == commune_procedure.commune.departement.code_insee
            )
            assert commune_procedure.opposable is False

    def _assert_default_topics_creation(
        self, procedure: core_models.Procedure, post_data: dict
    ) -> None:
        assertQuerySetEqual(
            procedure.topics.all(),
            core_models.Topic.objects.filter(name__in=post_data["topicsList"]),
        )
        assert (
            procedure.topics_through.get(topic__name="other").comment
            == post_data["otherTopicComment"]
        )
        assert all(
            comment == ""
            for comment in procedure.topics_through.exclude(
                topic__name="other"
            ).values_list("comment", flat=True)
        )

    def _assert_default_project_creation(
        self, procedure: core_models.Procedure, project: core_models.Project
    ) -> None:
        assert project.name == f"{procedure.type} {procedure.doc_type}"
        assert project.doc_type == procedure.doc_type
        assert project.current_perimetre == procedure.current_perimetre
        assert project.test is True
        assert project.region == "76"  # Occitanie

    def test_collectivite_is_intermunicipality__nominal(
        self,
        api_client_with_auth: SupabaseApiTestClient,
        django_assert_num_queries: DjangoAssertNumQueries,
    ) -> None:
        # This test assumes no one has the jurisdiction because
        # collectivite.competence_plan and collectivite.competence_schema
        # are False by default.
        # In this particular case, which should not happen in the reality,
        # the system chooses the collectivite to be the `collectivite porteuse``.
        # Jurisdiction are omitted in this test to avoid `collectivite porteuse` differences.
        # They are tested separately.
        collectivite = core_factories.CollectiviteFactory(
            for_snapshot=True,
            with_flat_members=True,
            with_flat_members__for_snapshot=True,
        )
        perimetre_insee_codes = collectivite.flat_members.filter(
            type=core_enums.CommuneType.COM
        ).values_list("code_insee", flat=True)
        data = self._default_post_data(
            collectivite=collectivite, perimetre=perimetre_insee_codes
        )
        logged_in_profile = ProfileFactory(collectivite=collectivite)
        with (
            api_client_with_auth(logged_in_profile) as api_client,
            django_assert_num_queries(self.PP_BASE_QUERIES + 8),
        ):
            response = api_client.post(self.url, data=data)
        assert response.status_code == 201

        assert core_models.Procedure.objects.count() == 1
        procedure = core_models.Procedure.objects.first()
        assert response.json()["id"] == str(procedure.pk)
        assert response.json()["projectId"] == str(procedure.project.pk)

        self._assert_default_procedure_creation(
            procedure=procedure, logged_in_profile=logged_in_profile, post_data=data
        )
        assert procedure.vaut_SCoT is False

        assert procedure.departements == ["30"]
        assert procedure.collectivite_porteuse_id == collectivite.siren
        assert sorted(
            procedure.perimetre.values_list("code_insee", flat=True)
        ) == sorted(perimetre_insee_codes)
        assert sorted(procedure.current_perimetre, key=lambda c: c["inseeCode"]) == [
            {"name": "Beaucaire", "inseeCode": "30032"},
            {"name": "Bellegarde", "inseeCode": "30034"},
            {"name": "Fourques", "inseeCode": "30117"},
            {"name": "Jonquières-Saint-Vincent", "inseeCode": "30135"},
            {"name": "Vallabrègues", "inseeCode": "30336"},
        ]

        self._assert_default_commune_procedure_creation(procedure=procedure)
        assert procedure.vaut_SCoT is False
        self._assert_default_topics_creation(procedure=procedure, post_data=data)

        ## PROJECT
        # Only for principal procedures.
        project = procedure.project
        self._assert_default_project_creation(procedure=procedure, project=project)
        assert project.collectivite_id == collectivite.siren
        assert project.collectivite_porteuse_id == collectivite.siren

    def test_collectivite_is_municipality__nominal(
        self,
        api_client_with_auth: SupabaseApiTestClient,
        django_assert_num_queries: DjangoAssertNumQueries,
    ) -> None:
        collectivite = core_factories.CommuneFactory(for_snapshot=True)
        logged_in_profile = ProfileFactory(collectivite=collectivite)
        perimetre_codes_insee = [collectivite.code_insee]
        post_data = self._default_post_data(
            collectivite=collectivite, perimetre=perimetre_codes_insee
        ) | {
            "collectiviteCode": collectivite.code_insee,
            "docType": core_enums.TypeDocument.PLU,
        }
        with (
            api_client_with_auth(profile=logged_in_profile) as api_client,
            django_assert_num_queries(self.PP_BASE_QUERIES - 1),
        ):
            response = api_client.post(self.url, data=post_data)
        assert response.status_code == 201
        assert core_models.Procedure.objects.count() == 1

        ## PROCEDURE
        procedure = core_models.Procedure.objects.first()
        self._assert_default_procedure_creation(
            procedure=procedure,
            logged_in_profile=logged_in_profile,
            post_data=post_data,
        )
        assert procedure.vaut_SCoT is False
        assert procedure.collectivite_porteuse_id == collectivite.code_insee
        assert sorted(
            procedure.perimetre.values_list("code_insee", flat=True)
        ) == sorted(perimetre_codes_insee)
        assert procedure.current_perimetre == [
            {"name": "Beaucaire", "inseeCode": "30032"}
        ]
        assert procedure.perimetre.count() == 1

        commune_procedure = procedure.perimetre_through.first()
        assert commune_procedure.collectivite_code == "30032"
        assert commune_procedure.collectivite_type == core_enums.CommuneType.COM
        assert commune_procedure.departement == "30"
        assert commune_procedure.opposable is False

        self._assert_default_topics_creation(procedure=procedure, post_data=post_data)

        ## PROJECT
        project = procedure.project
        self._assert_default_project_creation(procedure=procedure, project=project)
        assert project.collectivite_id == collectivite.code_insee
        assert project.collectivite_porteuse_id == collectivite.code_insee

    #############################################################
    ################ Test collectivite porteuse #################
    #############################################################
    def test_collectivite_porteuse__is_municipality_with_intermunicipality_and_jurisdiction(
        self,
        api_client_with_auth: SupabaseApiTestClient,
        django_assert_num_queries: DjangoAssertNumQueries,
    ) -> None:
        """The municipality has the jurisdiction, intermunicipality not.
        The selected collectivite is the municipality.
        """  # noqa: D205
        commune = core_factories.CommuneFactory(
            code_insee="30032",
            competence_plan=True,
            competence_schema=True,
        )
        intercommunalite = core_factories.CollectiviteFactory(
            for_snapshot=True,
            type=core_enums.TypeCollectivite.CC,
            with_members=True,
            with_members__list=[commune],
            competence_plan=False,
            competence_schema=False,
        )
        commune.intercommunalite = intercommunalite
        commune.save()

        assert core_models.Procedure.objects.count() == 0
        post_data = self._default_post_data(
            collectivite=commune, perimetre=[commune.code_insee]
        ) | {
            "collectiviteCode": commune.code_insee,
            "docType": core_enums.TypeDocument.PLU,
        }
        logged_in_profile = ProfileFactory(collectivite=commune)
        with (
            api_client_with_auth(logged_in_profile) as api_client,
            django_assert_num_queries(self.PP_BASE_QUERIES),
        ):
            response = api_client.post(self.url, data=post_data)
        assert response.status_code == 201
        assert core_models.Procedure.objects.count() == 1

        procedure = core_models.Procedure.objects.first()
        self._assert_default_procedure_creation(
            procedure=procedure,
            logged_in_profile=logged_in_profile,
            post_data=post_data,
        )
        assert procedure.vaut_SCoT is False
        assert procedure.collectivite_porteuse_id == commune.code_insee

        self._assert_default_commune_procedure_creation(procedure=procedure)
        self._assert_default_topics_creation(procedure=procedure, post_data=post_data)

        ## PROJECT
        project = procedure.project
        self._assert_default_project_creation(procedure=procedure, project=project)
        assert project.collectivite_id == intercommunalite.siren
        assert project.collectivite_porteuse_id == commune.code_insee

    def test_collectivite_porteuse__is_municipality_with_intermunicipality_and_jurisdiction_for_both(
        self,
        api_client_with_auth: SupabaseApiTestClient,
        django_assert_num_queries: DjangoAssertNumQueries,
    ) -> None:
        """The municipality has the jurisdiction, intermunicipality too.
        The municipality stays the collectivite porteuse.
        The selected collectivite is the municipality.
        """  # noqa: D205
        commune = core_factories.CommuneFactory(
            code_insee="30032",
            competence_plan=True,
            competence_schema=True,
        )
        intercommunalite = core_factories.CollectiviteFactory(
            for_snapshot=True,
            type=core_enums.TypeCollectivite.CC,
            with_members=True,
            with_members__list=[commune],
            competence_plan=True,
            competence_schema=True,
        )
        commune.intercommunalite = intercommunalite
        commune.save()

        assert core_models.Procedure.objects.count() == 0
        post_data = self._default_post_data(
            collectivite=commune, perimetre=[commune.code_insee]
        ) | {
            "collectiviteCode": commune.code_insee,
            "docType": core_enums.TypeDocument.PLU,
        }
        logged_in_profile = ProfileFactory(collectivite=commune)
        with (
            api_client_with_auth(logged_in_profile) as api_client,
            django_assert_num_queries(self.PP_BASE_QUERIES),
        ):
            response = api_client.post(self.url, data=post_data)
        assert response.status_code == 201
        assert core_models.Procedure.objects.count() == 1

        procedure = core_models.Procedure.objects.first()
        self._assert_default_procedure_creation(
            procedure=procedure,
            logged_in_profile=logged_in_profile,
            post_data=post_data,
        )
        assert procedure.vaut_SCoT is False
        assert procedure.collectivite_porteuse_id == commune.code_insee

        self._assert_default_commune_procedure_creation(procedure=procedure)
        self._assert_default_topics_creation(procedure=procedure, post_data=post_data)

        ## PROJECT
        project = procedure.project
        self._assert_default_project_creation(procedure=procedure, project=project)
        assert project.collectivite_id == intercommunalite.siren
        assert project.collectivite_porteuse_id == commune.code_insee

    def test_collectivite_porteuse__is_municipality_with_intermunicipality_and_no_jurisdiction(
        self,
        api_client_with_auth: SupabaseApiTestClient,
        django_assert_num_queries: DjangoAssertNumQueries,
    ) -> None:
        """The municipality does not have the jurisdiction.
        # It has been transfered to the intermunicipality.
        The intermunicipality is the collectivite porteuse.
        The selected collectivite is the municipality.
        """  # noqa: D205
        commune = core_factories.CommuneFactory(
            code_insee="30032",
            competence_plan=False,
            competence_schema=False,
        )
        intercommunalite = core_factories.CollectiviteFactory(
            for_snapshot=True,
            type=core_enums.TypeCollectivite.CC,
            with_members=True,
            with_members__list=[commune],
            competence_plan=True,
            competence_schema=True,
        )
        commune.intercommunalite = intercommunalite
        commune.save()

        assert core_models.Procedure.objects.count() == 0
        post_data = self._default_post_data(
            collectivite=commune, perimetre=[commune.code_insee]
        ) | {
            "collectiviteCode": commune.code_insee,
            "docType": core_enums.TypeDocument.PLU,
        }
        logged_in_profile = ProfileFactory(collectivite=commune)
        with (
            api_client_with_auth(logged_in_profile) as api_client,
            django_assert_num_queries(self.PP_BASE_QUERIES),
        ):
            response = api_client.post(self.url, data=post_data)
        assert response.status_code == 201
        assert core_models.Procedure.objects.count() == 1

        procedure = core_models.Procedure.objects.first()
        self._assert_default_procedure_creation(
            procedure=procedure,
            logged_in_profile=logged_in_profile,
            post_data=post_data,
        )
        assert procedure.vaut_SCoT is False
        assert procedure.collectivite_porteuse_id == intercommunalite.siren

        self._assert_default_commune_procedure_creation(procedure=procedure)
        self._assert_default_topics_creation(procedure=procedure, post_data=post_data)

        ## PROJECT
        project = procedure.project
        self._assert_default_project_creation(procedure=procedure, project=project)
        assert project.collectivite_id == intercommunalite.siren
        assert project.collectivite_porteuse_id == intercommunalite.siren

    def test_collectivite_porteuse__is_intermunicipality_without_jurisdiction(
        self,
        api_client_with_auth: SupabaseApiTestClient,
        django_assert_num_queries: DjangoAssertNumQueries,
    ) -> None:
        """The municipalities has the jurisdiction, intermunicipality not.
        The collectivite porteuse is the intermunicipality.
        The selected collectivite is the intermunicipality.
        """  # noqa: D205
        # Selected only one commune will be blocked soon to encourage
        # user to select the commune as the communalite.
        # That's why there are two communes here.
        communes = [
            core_factories.CommuneFactory(
                code_insee="30032",
                competence_plan=True,
                competence_schema=True,
            ),
            core_factories.CommuneFactory(
                code_insee="30034",
                competence_plan=True,
                competence_schema=True,
            ),
        ]
        intercommunalite = core_factories.CollectiviteFactory(
            for_snapshot=True,
            type=core_enums.TypeCollectivite.CC,
            with_members=True,
            with_members__list=communes,
            competence_plan=False,
            competence_schema=False,
        )
        for commune in communes:
            commune.intercommunalite = intercommunalite
            commune.save()

        assert core_models.Procedure.objects.count() == 0
        # This should create a PLUIS and will be blocked soon.
        post_data = self._default_post_data(
            collectivite=intercommunalite, perimetre=["30032", "30034"]
        ) | {
            "collectiviteCode": intercommunalite.siren,
            "docType": core_enums.TypeDocument.PLUI,
        }
        logged_in_profile = ProfileFactory(collectivite=intercommunalite)
        with (
            api_client_with_auth(logged_in_profile) as api_client,
            django_assert_num_queries(self.PP_BASE_QUERIES + 4),
        ):
            response = api_client.post(self.url, data=post_data)
        assert response.status_code == 201
        assert core_models.Procedure.objects.count() == 1

        procedure = core_models.Procedure.objects.first()
        self._assert_default_procedure_creation(
            procedure=procedure,
            logged_in_profile=logged_in_profile,
            post_data=post_data,
        )
        assert procedure.vaut_SCoT is False
        assert procedure.collectivite_porteuse_id == intercommunalite.siren

        self._assert_default_commune_procedure_creation(procedure=procedure)
        self._assert_default_topics_creation(procedure=procedure, post_data=post_data)

        ## PROJECT
        project = procedure.project
        self._assert_default_project_creation(procedure=procedure, project=project)
        assert project.collectivite_id == intercommunalite.siren
        assert project.collectivite_porteuse_id == intercommunalite.siren

    def test_collectivite_porteuse__is_intermunicipality_with_jurisdiction(
        self,
        api_client_with_auth: SupabaseApiTestClient,
        django_assert_num_queries: DjangoAssertNumQueries,
    ) -> None:
        """The intermunicipality has the jurisdiction.
        The selected collectivite is the intermunicipality.
        The intermunicipality is the collectivite porteuse.
        """  # noqa: D205
        # Selected only one commune will be blocked soon to encourage
        # user to select the commune as the communalite.
        # That's why there are two communes here.
        communes = [
            core_factories.CommuneFactory(
                code_insee="30032",
                competence_plan=True,
                competence_schema=True,
            ),
            core_factories.CommuneFactory(
                code_insee="30034",
                competence_plan=True,
                competence_schema=True,
            ),
        ]
        intercommunalite = core_factories.CollectiviteFactory(
            for_snapshot=True,
            type=core_enums.TypeCollectivite.CC,
            with_members=True,
            with_members__list=communes,
            competence_plan=False,
            competence_schema=False,
        )
        for commune in communes:
            commune.intercommunalite = intercommunalite
            commune.save()

        assert core_models.Procedure.objects.count() == 0
        post_data = self._default_post_data(
            collectivite=commune, perimetre=[commune.code_insee]
        ) | {
            "collectiviteCode": intercommunalite.siren,
            "docType": core_enums.TypeDocument.PLU,
        }
        logged_in_profile = ProfileFactory(collectivite=intercommunalite)
        with (
            api_client_with_auth(logged_in_profile) as api_client,
            django_assert_num_queries(self.PP_BASE_QUERIES),
        ):
            response = api_client.post(self.url, data=post_data)
        assert response.status_code == 201
        assert core_models.Procedure.objects.count() == 1

        procedure = core_models.Procedure.objects.first()
        self._assert_default_procedure_creation(
            procedure=procedure,
            logged_in_profile=logged_in_profile,
            post_data=post_data,
        )
        assert procedure.vaut_SCoT is False
        assert procedure.collectivite_porteuse_id == intercommunalite.siren

        self._assert_default_commune_procedure_creation(procedure=procedure)
        self._assert_default_topics_creation(procedure=procedure, post_data=post_data)

        ## PROJECT
        project = procedure.project
        self._assert_default_project_creation(procedure=procedure, project=project)
        assert project.collectivite_id == intercommunalite.siren
        assert project.collectivite_porteuse_id == intercommunalite.siren

    def test_no_other_topic_but_topic_comment(
        self,
        api_client_with_auth: SupabaseApiTestClient,
    ) -> None:
        collectivite = core_factories.CollectiviteFactory(
            for_snapshot=True,
            with_flat_members=True,
            with_flat_members__for_snapshot=True,
        )
        logged_in_profile = ProfileFactory(collectivite=collectivite)
        perimetre_insee_codes = collectivite.flat_members.filter(
            type=core_enums.CommuneType.COM
        ).values_list("code_insee", flat=True)

        data = self._default_post_data(
            collectivite=collectivite, perimetre=perimetre_insee_codes
        ) | {
            "topicsList": ["zan", "coastline"],
            "otherTopicComment": "I love coastlines.",
        }
        with (
            api_client_with_auth(logged_in_profile) as api_client,
        ):
            response = api_client.post(self.url, data=data)
        assert response.status_code == 400

    def test_other_topic_no_comment(
        self, api_client_with_auth: SupabaseApiTestClient
    ) -> None:
        collectivite = core_factories.CollectiviteFactory(
            for_snapshot=True,
            with_flat_members=True,
            with_flat_members__for_snapshot=True,
        )
        perimetre_insee_codes = collectivite.flat_members.filter(
            type=core_enums.CommuneType.COM
        ).values_list("code_insee", flat=True)
        data = self._default_post_data(
            collectivite=collectivite, perimetre=perimetre_insee_codes
        ) | {
            "topicsList": ["zan", "coastline", "other"],
            "otherTopicComment": "",
        }
        logged_in_profile = ProfileFactory(collectivite=collectivite)
        with api_client_with_auth(logged_in_profile) as api_client:
            response = api_client.post(self.url, data=data)

        assert response.status_code == 400
        assert (
            response.json()["non_field_errors"][0]
            == "Un commentaire est obligatoire car l'objet Autre a été sélectionné."
        )
        assert core_models.Procedure.objects.count() == 0

    def test_other_topic_comment_no_other_topic(
        self, api_client_with_auth: SupabaseApiTestClient
    ) -> None:
        collectivite = core_factories.CollectiviteFactory(
            for_snapshot=True,
            with_flat_members=True,
            with_flat_members__for_snapshot=True,
        )
        perimetre_insee_codes = collectivite.flat_members.filter(
            type=core_enums.CommuneType.COM
        ).values_list("code_insee", flat=True)
        data = self._default_post_data(
            collectivite=collectivite, perimetre=perimetre_insee_codes
        ) | {
            "topicsList": ["zan", "coastline"],
            "otherTopicComment": "I love coastlines",
        }
        logged_in_profile = ProfileFactory(collectivite=collectivite)
        with api_client_with_auth(logged_in_profile) as api_client:
            response = api_client.post(self.url, data=data)

        assert response.status_code == 400
        assert (
            response.json()["non_field_errors"][0]
            == "Un commentaire Autre ne peut être enregistré que pour l'objet Autre."
        )
        assert core_models.Procedure.objects.count() == 0

    @pytest.mark.parametrize(
        ("doc_types", "nb_communes_in_perimetre", "expected_error_message"),
        [
            pytest.param(
                ["PLUi", "PLUiH", "PLUiM", "PLUiHM", "SCOT"],
                1,
                "is an intermunicipality document but only one town has been selected.",
                id="forbidden_intercommunal_types",
            ),
            pytest.param(
                ["CC", "PLU"],
                2,
                "is a municipality document but many towns have been selected.",
                id="forbidden_communal_types",
            ),
        ],
    )
    def test_doc_type_len_perimetre__validation_error(
        self,
        api_client_with_auth: SupabaseApiTestClient,
        subtests: pytest.Subtests,
        doc_types: list,
        nb_communes_in_perimetre: int,
        expected_error_message: str,
    ) -> None:
        communes = core_factories.CommuneFactory.create_batch(nb_communes_in_perimetre)
        collectivite = core_factories.CollectiviteFactory(
            for_snapshot=True,
            with_members=True,
            with_members__list=communes,
        )
        perimetre_insee_codes = collectivite.flat_members.filter(
            type=core_enums.CommuneType.COM
        ).values_list("code_insee", flat=True)
        for doc_type in doc_types:
            with subtests.test(doc_type, doc_type=doc_type):
                data = self._default_post_data(
                    collectivite=collectivite, perimetre=perimetre_insee_codes
                ) | {
                    "docType": doc_type,
                }
                logged_in_profile = ProfileFactory(collectivite=collectivite)
                with api_client_with_auth(logged_in_profile) as api_client:
                    response = api_client.post(self.url, data=data)

                assert response.status_code == 400
                assert (
                    response.json()["non_field_errors"][0]
                    == f"{doc_type} {expected_error_message}"
                )
                assert core_models.Procedure.objects.count() == 0

    def test_procedure_interdepartment(
        self,
        api_client_with_auth: SupabaseApiTestClient,
        django_assert_num_queries: DjangoAssertNumQueries,
    ) -> None:
        communes = [
            core_factories.CommuneFactory(code_insee="30032"),
            core_factories.CommuneFactory(code_insee="13001"),
        ]
        collectivite = core_factories.CollectiviteFactory(
            for_snapshot=True,
            with_members=True,
            with_members__list=communes,
        )
        perimetre_insee_codes = collectivite.flat_members.filter(
            type=core_enums.CommuneType.COM
        ).values_list("code_insee", flat=True)
        data = self._default_post_data(
            collectivite=collectivite, perimetre=perimetre_insee_codes
        )
        logged_in_profile = ProfileFactory(collectivite=collectivite)
        with (
            api_client_with_auth(logged_in_profile) as api_client,
            django_assert_num_queries(self.PP_BASE_QUERIES + 2),
        ):
            response = api_client.post(self.url, data=data)
        assert response.status_code == 201

        assert core_models.Procedure.objects.count() == 1
        procedure = core_models.Procedure.objects.first()
        assert response.json()["id"] == str(procedure.id)

        self._assert_default_procedure_creation(
            procedure=procedure, logged_in_profile=logged_in_profile, post_data=data
        )
        assert procedure.vaut_SCoT is False
        assert sorted(procedure.departements) == ["13", "30"]
        self._assert_default_commune_procedure_creation(procedure=procedure)
        self._assert_default_project_creation(
            procedure=procedure, project=procedure.project
        )

    def test_name_complement(self, api_client_with_auth: SupabaseApiTestClient) -> None:
        collectivite = core_factories.CommuneFactory()
        logged_in_profile = ProfileFactory(collectivite=collectivite)
        perimetre_codes_insee = [collectivite.code_insee]
        expected_name_complement = "de zone urbaine"
        post_data = self._default_post_data(
            collectivite=collectivite, perimetre=perimetre_codes_insee
        ) | {
            "nameComplement": expected_name_complement,
            "collectiviteCode": str(collectivite.code_insee),
            "docType": core_enums.TypeDocument.PLU,
        }
        with api_client_with_auth(profile=logged_in_profile) as api_client:
            response = api_client.post(self.url, data=post_data)
        assert response.status_code == 201
        assert core_models.Procedure.objects.count() == 1
        procedure = core_models.Procedure.objects.first()
        assert procedure.name_complement == expected_name_complement
        assert procedure.computed_name == response.json()["name"]

    def test_sectoriel(
        self,
        api_client_with_auth: SupabaseApiTestClient,
        django_assert_num_queries: DjangoAssertNumQueries,
    ) -> None:
        communes = [
            core_factories.CommuneFactory(code_insee="30032"),
            core_factories.CommuneFactory(code_insee="30034"),
            core_factories.CommuneFactory(code_insee="13001"),
        ]
        collectivite = core_factories.CollectiviteFactory(
            for_snapshot=True,
            with_members=True,
            with_members__list=communes,
        )
        logged_in_profile = ProfileFactory(collectivite=collectivite)
        post_data = self._default_post_data(
            collectivite=collectivite, perimetre=["30032", "30034"]
        ) | {
            "docType": core_enums.TypeDocument.PLUI,
        }
        with (
            api_client_with_auth(logged_in_profile) as api_client,
            django_assert_num_queries(self.PP_BASE_QUERIES + 2),
        ):
            response = api_client.post(self.url, data=post_data)
        assert response.status_code == 201
        assert core_models.Procedure.objects.count() == 1
        procedure = core_models.Procedure.objects.first()
        assert procedure.doc_type == core_enums.TypeDocument.PLUIS

    def test_collectiviteCode__validation_error(  # noqa: N802
        self, api_client_with_auth: SupabaseApiTestClient
    ) -> None:
        communes = core_factories.CommuneFactory.create_batch(2)
        collectivite = core_factories.CollectiviteFactory(
            for_snapshot=True,
            with_members=True,
            with_members__list=communes,
        )
        perimetre_insee_codes = collectivite.flat_members.filter(
            type=core_enums.CommuneType.COM
        ).values_list("code_insee", flat=True)
        data = self._default_post_data(perimetre=perimetre_insee_codes) | {
            "collectiviteCode": "0000000000"
        }
        logged_in_profile = ProfileFactory(collectivite=collectivite)
        with api_client_with_auth(logged_in_profile) as api_client:
            response = api_client.post(self.url, data=data)

        assert response.status_code == 400
        assert response.json()["collectiviteCode"][0] == "Collectivité not found"
        assert core_models.Procedure.objects.count() == 0

    def test_perimetreCommunesCodes__validation_error(  # noqa: N802
        self, api_client_with_auth: SupabaseApiTestClient
    ) -> None:
        collectivite = core_factories.CollectiviteFactory(
            for_snapshot=True,
        )
        data = self._default_post_data(collectivite=collectivite) | {
            "perimetreCodes": ["00000"]
        }
        logged_in_profile = ProfileFactory(collectivite=collectivite)
        with api_client_with_auth(logged_in_profile) as api_client:
            response = api_client.post(self.url, data=data)

        assert response.status_code == 400
        assert (
            response.json()["perimetreCodes"][0]
            == "Following communes have not been found: ['00000']."
        )
        assert core_models.Procedure.objects.count() == 0

    def test_parentId__validation_error(  # noqa: N802
        self, api_client_with_auth: SupabaseApiTestClient
    ) -> None:
        collectivite = core_factories.CollectiviteFactory(
            for_snapshot=True,
        )
        post_data = {
            "collectiviteCode": "",
            "perimetreCodes": "",
            "docType": "",
            "number": "",
            "type": core_enums.ProcedureType.MISE_A_JOUR,
            "startedBeforeHuwartLaw": True,
            "topicsList": ["zan", "coastline", "other"],
            "otherTopicComment": "I love coastlines.",
            "nameComplement": "complément du nom",
            "parentId": "00000000-0000-0000-0000-000000000000",
        }
        logged_in_profile = ProfileFactory(collectivite=collectivite)
        with api_client_with_auth(logged_in_profile) as api_client:
            response = api_client.post(self.url, data=post_data)

        assert response.status_code == 400
        assert response.json()["parentId"][0] == "Principal procedure not found."
        assert core_models.Procedure.objects.count() == 0

    def test_nominal_secondary_procedure_creation(
        self,
        api_client_with_auth: SupabaseApiTestClient,
        django_assert_num_queries: DjangoAssertNumQueries,
    ) -> None:
        communes = core_factories.CommuneFactory.create_batch(2)
        collectivite = core_factories.CollectiviteFactory(
            for_snapshot=True,
            with_flat_members=True,
            with_flat_members__list=communes,
        )
        principal_procedure = core_factories.ProcedureFactory(
            pk=uuid.UUID("1cd65b57-7027-4aa5-8d19-111111111111"),
            doc_type=core_enums.TypeDocument.PLUI,
            collectivite_porteuse=collectivite,
            with_perimetre=communes,
            numero="1",
            for_snapshot=True,
            status=core_enums.ProcedureStatusChoices.EN_COURS,
        )

        post_data = {
            "collectiviteCode": "",
            "perimetreCodes": "",
            "docType": "",
            "number": "3",
            "type": core_enums.ProcedureType.MISE_A_JOUR,
            "startedBeforeHuwartLaw": True,
            "topicsList": ["zan", "coastline", "other"],
            "otherTopicComment": "I love coastlines.",
            "parentId": str(principal_procedure.pk),
            "nameComplement": "complément du nom",
        }

        logged_in_profile = ProfileFactory(collectivite=collectivite)
        with (
            api_client_with_auth(logged_in_profile) as api_client,
            django_assert_num_queries(self.PS_BASE_QUERIES),
        ):
            response = api_client.post(self.url, data=post_data)
        assert response.status_code == 201

        procedure = core_models.Procedure.objects.get(parente=principal_procedure.pk)

        assert procedure.started_before_huwart_law is True
        assert procedure.type == core_enums.ProcedureType.MISE_A_JOUR
        assert procedure.doc_type == principal_procedure.doc_type
        assert procedure.numero == "3"
        assert procedure.name_complement == "complément du nom"
        assert procedure.shareable
        assert procedure.is_principale is False
        assert procedure.status is None
        assert procedure.is_sectoriel is None
        assert procedure.vaut_PDM is False
        assert procedure.vaut_PLH is False
        assert procedure.testing is True
        assert procedure.owner_id == uuid.UUID(logged_in_profile.user_id)
        assert procedure.project_id == principal_procedure.project_id

        assertQuerySetEqual(
            procedure.perimetre.order_by("pk").all(),
            principal_procedure.perimetre.order_by("pk").all(),
        )

        self._assert_default_commune_procedure_creation(procedure=procedure)
        self._assert_default_topics_creation(procedure=procedure, post_data=post_data)
