import datetime
import random
import uuid
from urllib.parse import urlencode

import pytest
from django.urls import reverse
from pytest_django import DjangoAssertNumQueries
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
            doc_type=core_enums.TypeDocument.PLU,
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
            doc_type=core_enums.TypeDocument.PLU,
        )
        core_factories.ProcedureFactory(
            pk=uuid.UUID("1cd65b57-7027-4aa5-8d19-333333333333"),
            name="Troisième procédure",
            status=core_enums.ProcedureStatusChoices.EN_COURS,
            collectivite_porteuse=collectivite,
            with_perimetre=[communes[2]],
            numero="1",
            project=procedure.project,
            doc_type=core_enums.TypeDocument.PLU,
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
class TestProcedureSynchronizeStatus:
    def _url(self, procedure: core_models.Procedure) -> str:
        return reverse(
            "internal_api:procedures-synchronize-status", kwargs={"pk": procedure.pk}
        )

    def _procedure_with_outdated_status(self) -> core_models.Procedure:
        procedure = core_factories.ProcedureFactory(
            status=core_enums.ProcedureStatusChoices.OPPOSABLE
        )
        event_type = core_factories.EventTypeFactory(
            name="Annulation synchronize status",
            impact=core_enums.ProcedureStatusChoices.ANNULE,
        )
        core_factories.EventFactory(
            procedure=procedure,
            event_type=event_type,
            date_evenement=datetime.date(2024, 6, 1),
        )
        return procedure

    def test_synchronize_status_updates_procedure(
        self, api_client_with_auth: SupabaseApiTestClient
    ) -> None:
        procedure = self._procedure_with_outdated_status()
        profile = ProfileFactory()

        with api_client_with_auth(profile) as api_client:
            response = api_client.post(self._url(procedure))

        assert response.status_code == 200
        assert response.json() == {"status": "annule"}
        procedure.refresh_from_db()
        assert procedure.status == core_enums.ProcedureStatusChoices.ANNULE

    def test_synchronize_status_already_up_to_date(
        self, api_client_with_auth: SupabaseApiTestClient
    ) -> None:
        procedure = core_factories.ProcedureFactory()
        profile = ProfileFactory()

        with api_client_with_auth(profile) as api_client:
            response = api_client.post(self._url(procedure))

        assert response.status_code == 200
        assert response.json() == {"status": "en projet"}
        procedure.refresh_from_db()
        assert procedure.status == core_enums.ProcedureStatusChoices.EN_PROJET

    def test_synchronize_status_takes_future_events_into_account(
        self, api_client_with_auth: SupabaseApiTestClient
    ) -> None:
        # The endpoint does not use a date pivot: even a future event impacts
        # the computed status.
        procedure = core_factories.ProcedureFactory(
            status=core_enums.ProcedureStatusChoices.EN_COURS
        )
        event_type = core_factories.EventTypeFactory(
            name="Future approbation synchronize status",
            impact=core_enums.ProcedureStatusChoices.OPPOSABLE,
        )
        core_factories.EventFactory(
            procedure=procedure,
            event_type=event_type,
            date_evenement=datetime.date(2999, 12, 1),
        )
        profile = ProfileFactory()

        with api_client_with_auth(profile) as api_client:
            response = api_client.post(self._url(procedure))

        assert response.status_code == 200
        assert response.json() == {"status": "opposable"}
        procedure.refresh_from_db()
        assert procedure.status == core_enums.ProcedureStatusChoices.OPPOSABLE

    def _create_impactful_event(
        self,
        procedure: core_models.Procedure,
        impact: core_enums.ProcedureStatusChoices,
        *,
        date_evenement: datetime.date,
    ) -> core_models.Event:
        # The uuid suffix prevents unique constraint violations when several
        # events share the same date and impact.
        event_type = core_factories.EventTypeFactory(
            name=f"Type {impact} {date_evenement} {uuid.uuid4().hex[:8]}",
            impact=impact,
        )
        return core_factories.EventFactory(
            procedure=procedure,
            event_type=event_type,
            date_evenement=date_evenement,
        )

    def test_synchronize_status_updates_perimetre_opposability(
        self, api_client_with_auth: SupabaseApiTestClient
    ) -> None:
        commune = core_factories.CommuneFactory()
        procedure = core_factories.ProcedureFactory(with_perimetre=[commune])
        self._create_impactful_event(
            procedure,
            core_enums.ProcedureStatusChoices.OPPOSABLE,
            date_evenement=datetime.date(2025, 1, 1),
        )

        with api_client_with_auth(ProfileFactory()) as api_client:
            response = api_client.post(self._url(procedure))
        assert response.status_code == 200

        assert procedure.perimetre_through.get().opposable is True

    def test_synchronize_status_resets_stale_opposable_flag(
        self, api_client_with_auth: SupabaseApiTestClient
    ) -> None:
        # Historically flagged as opposable by Nuxt, but the last impactful
        # event is no longer opposable.
        commune = core_factories.CommuneFactory()
        procedure = core_factories.ProcedureFactory(with_perimetre=[commune])
        self._create_impactful_event(
            procedure,
            core_enums.ProcedureStatusChoices.OPPOSABLE,
            date_evenement=datetime.date(2024, 6, 1),
        )
        self._create_impactful_event(
            procedure,
            core_enums.ProcedureStatusChoices.ANNULE,
            date_evenement=datetime.date(2025, 1, 1),
        )
        perimetre_line = procedure.perimetre_through.get()
        perimetre_line.opposable = True
        perimetre_line.save(update_fields=["opposable"])

        with api_client_with_auth(ProfileFactory()) as api_client:
            response = api_client.post(self._url(procedure))
        assert response.status_code == 200

        assert procedure.perimetre_through.get().opposable is False

    def test_synchronize_status_synchronizes_other_procedures_of_perimetre_communes(
        self, api_client_with_auth: SupabaseApiTestClient
    ) -> None:
        # Synchronizing a procedure also updates the flags of the other
        # procedures sharing its perimetre communes.
        commune = core_factories.CommuneFactory()
        procedure_avant = core_factories.ProcedureFactory(
            doc_type=core_enums.TypeDocument.PLU, with_perimetre=[commune]
        )
        self._create_impactful_event(
            procedure_avant,
            core_enums.ProcedureStatusChoices.OPPOSABLE,
            date_evenement=datetime.date(2024, 6, 1),
        )
        procedure_apres = core_factories.ProcedureFactory(
            doc_type=core_enums.TypeDocument.PLU, with_perimetre=[commune]
        )
        self._create_impactful_event(
            procedure_apres,
            core_enums.ProcedureStatusChoices.OPPOSABLE,
            date_evenement=datetime.date(2025, 1, 1),
        )
        stale_line = procedure_avant.perimetre_through.get()
        stale_line.opposable = True
        stale_line.save(update_fields=["opposable"])

        with api_client_with_auth(ProfileFactory()) as api_client:
            response = api_client.post(self._url(procedure_avant))
        assert response.status_code == 200

        assert procedure_apres.perimetre_through.get().opposable is True
        assert procedure_avant.perimetre_through.get().opposable is False

    def test_synchronize_status_leaves_communes_outside_perimetre_untouched(
        self, api_client_with_auth: SupabaseApiTestClient
    ) -> None:
        commune = core_factories.CommuneFactory()
        procedure = core_factories.ProcedureFactory(with_perimetre=[commune])
        self._create_impactful_event(
            procedure,
            core_enums.ProcedureStatusChoices.OPPOSABLE,
            date_evenement=datetime.date(2025, 1, 1),
        )
        autre_commune = core_factories.CommuneFactory()
        autre_procedure = core_factories.ProcedureFactory(
            with_perimetre=[autre_commune]
        )
        autre_line = autre_procedure.perimetre_through.get()
        autre_line.opposable = True
        autre_line.save(update_fields=["opposable"])

        with api_client_with_auth(ProfileFactory()) as api_client:
            response = api_client.post(self._url(procedure))
        assert response.status_code == 200

        assert procedure.perimetre_through.get().opposable is True
        # The stale flag outside the procedure perimetre is left untouched.
        assert autre_procedure.perimetre_through.get().opposable is True

    def test_synchronize_status_synchronizes_opposability_for_secondary_procedure(
        self, api_client_with_auth: SupabaseApiTestClient
    ) -> None:
        commune = core_factories.CommuneFactory()
        procedure_secondaire = core_factories.ProcedureFactory(
            with_perimetre=[commune],
            with_parente=True,
            parente__with_perimetre=[commune],
        )
        self._create_impactful_event(
            procedure_secondaire.parente,
            core_enums.ProcedureStatusChoices.OPPOSABLE,
            date_evenement=datetime.date(2024, 6, 1),
        )

        with api_client_with_auth(ProfileFactory()) as api_client:
            response = api_client.post(self._url(procedure_secondaire))
        assert response.status_code == 200

        assert procedure_secondaire.parente.perimetre_through.get().opposable is True
        assert procedure_secondaire.perimetre_through.get().opposable is False
