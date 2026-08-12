import random
import uuid
from urllib.parse import urlencode

import pytest
from django.urls import reverse
from pytest_django import DjangoAssertNumQueries
from syrupy.assertion import SnapshotAssertion

from docurba.core.enums import CommuneType, TypeCollectivite
from docurba.core.models import (
    Collectivite,
    Commune,
    ProcedureStatusChoices,
    Topic,
    TypeDocument,
)
from docurba.users.models import Profile
from tests.conftest import SupabaseApiClient
from tests.core.factories import (
    CollectiviteFactory,
    CommuneFactory,
    ProcedureFactory,
    ProjectFactory,
)
from tests.users.factories import ProfileFactory

BASE_QUERIES = (
    1  # session
    + 1  # count for pagination
    + 1  # procedures details
    + 1  # topics
    + 1  # perimetre
)


@pytest.mark.django_db
class TestProcedureList:
    def _create_collectivite_perimetre_profile(
        self,
    ) -> tuple[Collectivite, Commune, Profile]:
        #     # This test assumes no one has the jurisdiction because
        #     # collectivite.competence_plan and collectivite.competence_schema
        #     # are False by default.
        #     # In this particular case, which should not happen in the reality,
        #     # the system chooses the collectivite to be the `collectivite porteuse``.
        #     # Jurisdiction are omitted in this test to avoid `collectivite porteuse` differences.
        #     # They are tested separately.
        # TODO: get collectivite from the logged in user depending on the user rights.  # noqa: FIX002
        collectivite = CollectiviteFactory(
            for_snapshot=True,
            with_flat_members=True,
            with_flat_members__for_snapshot=True,
        )
        perimetre_insee_codes = collectivite.flat_members.filter(
            type=CommuneType.COM
        ).values_list("code_insee", flat=True)
        communes = Commune.objects.filter(code_insee__in=perimetre_insee_codes)
        logged_in_profile = ProfileFactory(
            with_collectivite=True, with_collectivite__collectivite=collectivite
        )
        return collectivite, communes, logged_in_profile

    @property
    def url(self) -> str:
        return reverse("internal_api:procedures-list")

    @pytest.mark.parametrize("status", ProcedureStatusChoices)
    def test_status_filter(
        self,
        status: str,
        api_client_with_auth: SupabaseApiClient,
        django_assert_num_queries: DjangoAssertNumQueries,
    ) -> None:
        collectivite, communes, logged_in_profile = (
            self._create_collectivite_perimetre_profile()
        )
        expected_procedure = ProcedureFactory(
            status=status,
            collectivite_porteuse=collectivite,
            with_perimetre=communes,
        )
        excluded_status = random.choice(  # noqa: S311
            [p_status for p_status in ProcedureStatusChoices if p_status != status]
        )
        ProcedureFactory(
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

    def test_many_statuses_filter(
        self,
        api_client_with_auth: SupabaseApiClient,
        django_assert_num_queries: DjangoAssertNumQueries,
    ) -> None:
        collectivite, communes, logged_in_profile = (
            self._create_collectivite_perimetre_profile()
        )
        expected_procedure_one = ProcedureFactory(
            status=ProcedureStatusChoices.OPPOSABLE,
            collectivite_porteuse=collectivite,
            with_perimetre=communes,
        )
        expected_procedure_two = ProcedureFactory(
            status=ProcedureStatusChoices.EN_COURS,
            collectivite_porteuse=collectivite,
            with_perimetre=communes,
        )
        not_expected_procedure = ProcedureFactory(
            status=ProcedureStatusChoices.ABANDON,
            collectivite_porteuse=collectivite,
            with_perimetre=communes,
        )
        with (
            api_client_with_auth(logged_in_profile) as api_client,
            django_assert_num_queries(BASE_QUERIES),
        ):
            response = api_client.get(
                f"{self.url}?status={ProcedureStatusChoices.OPPOSABLE}&status={ProcedureStatusChoices.EN_COURS}"
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
    def test_is_principale_filter(
        self,
        query_params: dict,
        api_client_with_auth: SupabaseApiClient,
        django_assert_num_queries: DjangoAssertNumQueries,
        snapshot: SnapshotAssertion,
    ) -> None:
        collectivite, communes, logged_in_profile = (
            self._create_collectivite_perimetre_profile()
        )
        ProcedureFactory(
            is_principale=True,
            collectivite_porteuse=collectivite,
            with_perimetre=communes,
        )
        ProcedureFactory(
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
            # # Don't raise an error for the moment.
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
    def test_collectivites_porteuses(
        self,
        query_params: dict,
        snapshot: SnapshotAssertion,
        api_client_with_auth: SupabaseApiClient,
    ) -> None:
        collectivite, communes, logged_in_profile = (
            self._create_collectivite_perimetre_profile()
        )
        ProcedureFactory(
            with_perimetre=[communes[0]],
            collectivite_porteuse=collectivite,
            numero="1",
            for_snapshot=True,
            status=ProcedureStatusChoices.EN_COURS,
        )
        collectivite_with_code_insee = CommuneFactory(
            departement__code_insee="30",
            code_insee="30001",
            type=TypeCollectivite.COM,
            nom="Aigaliers",
        )
        ProcedureFactory(
            pk=uuid.UUID("1cd65b57-7027-4aa5-8d19-222222222222"),
            name="Révision du PLU d'Aigaliers",
            status=ProcedureStatusChoices.EN_COURS,
            collectivite_porteuse=collectivite_with_code_insee,
            with_perimetre=[collectivite_with_code_insee],
            numero="1",
            project=ProjectFactory(
                id=uuid.UUID("1cd65b57-7027-4aa5-8d19-333333333333")
            ),
            doc_type=TypeDocument.PLU,
        )
        aigremont = CommuneFactory(code_insee="30002")
        ProcedureFactory(
            pk=uuid.UUID("1cd65b57-7027-4aa5-8d19-444444444444"),
            name="Révision du PLU d'Aigremont",
            status=ProcedureStatusChoices.EN_COURS,
            collectivite_porteuse=aigremont,
            with_perimetre=[aigremont],
            numero="1",
            project=ProjectFactory(
                id=uuid.UUID("1cd65b57-7027-4aa5-8d19-555555555555")
            ),
            doc_type=TypeDocument.PLU,
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
            # # Don't raise an error for the moment.
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
    def test_communes_perimetre(
        self,
        query_params: dict,
        snapshot: SnapshotAssertion,
        api_client_with_auth: SupabaseApiClient,
    ) -> None:
        collectivite, communes, logged_in_profile = (
            self._create_collectivite_perimetre_profile()
        )
        procedure = ProcedureFactory(
            with_perimetre=[communes[0]],
            collectivite_porteuse=collectivite,
            numero="1",
            for_snapshot=True,
            status=ProcedureStatusChoices.EN_COURS,
        )
        ProcedureFactory(
            pk=uuid.UUID("1cd65b57-7027-4aa5-8d19-222222222222"),
            name="Seconde procédure",
            status=ProcedureStatusChoices.EN_COURS,
            collectivite_porteuse=collectivite,
            with_perimetre=[communes[1]],
            numero="1",
            project=procedure.project,
            doc_type=TypeDocument.PLU,
        )
        ProcedureFactory(
            pk=uuid.UUID("1cd65b57-7027-4aa5-8d19-333333333333"),
            name="Troisième procédure",
            status=ProcedureStatusChoices.EN_COURS,
            collectivite_porteuse=collectivite,
            with_perimetre=[communes[2]],
            numero="1",
            project=procedure.project,
            doc_type=TypeDocument.PLU,
        )
        with api_client_with_auth(logged_in_profile) as api_client:
            response = api_client.get(
                f"{self.url}?{urlencode(query_params, doseq=True)}"
            )
        assert response.status_code == 200
        assert response.json()["results"] == snapshot()

    def test_serializer_with_topics(
        self,
        api_client_with_auth: SupabaseApiClient,
        django_assert_num_queries: DjangoAssertNumQueries,
    ) -> None:
        collectivite, communes, logged_in_profile = (
            self._create_collectivite_perimetre_profile()
        )
        expected_topic = Topic.objects.get(name="zan")
        ProcedureFactory(
            collectivite_porteuse=collectivite,
            with_perimetre=[communes[0]],
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

    def test_nominal_principal_procedure_serializer(
        self,
        api_client_with_auth: SupabaseApiClient,
        snapshot: SnapshotAssertion,
        django_assert_num_queries: DjangoAssertNumQueries,
    ) -> None:
        collectivite, communes, logged_in_profile = (
            self._create_collectivite_perimetre_profile()
        )
        ProcedureFactory(
            collectivite_porteuse=collectivite,
            with_perimetre=communes,
            numero="1",
            for_snapshot=True,
            status=ProcedureStatusChoices.EN_COURS,
        )
        with (
            api_client_with_auth(logged_in_profile) as api_client,
            django_assert_num_queries(BASE_QUERIES),
        ):
            response = api_client.get(f"{self.url}")
        assert response.status_code == 200
        assert response.json() == snapshot()

    def test_nominal_secondary_procedure_serializer(
        self,
        api_client_with_auth: SupabaseApiClient,
        snapshot: SnapshotAssertion,
        django_assert_num_queries: DjangoAssertNumQueries,
    ) -> None:
        collectivite, communes, logged_in_profile = (
            self._create_collectivite_perimetre_profile()
        )
        principal_procedure = ProcedureFactory(
            pk=uuid.UUID("1cd65b57-7027-4aa5-8d19-111111111111"),
            collectivite_porteuse=collectivite,
            with_perimetre=communes,
            numero="1",
            for_snapshot=True,
            status=ProcedureStatusChoices.EN_COURS,
        )
        secondary_procedure = ProcedureFactory(
            pk=uuid.UUID("1cd65b57-7027-4aa5-8d19-222222222222"),
            parente=principal_procedure,
            name="Révision du PLU de Nantes",
            status=ProcedureStatusChoices.EN_COURS,
            collectivite_porteuse=collectivite,
            with_perimetre=communes,
            numero="1",
            project=principal_procedure.project,
            doc_type=TypeDocument.PLU,
        )
        with (
            api_client_with_auth(logged_in_profile) as api_client,
            django_assert_num_queries(
                BASE_QUERIES
                + 1  # parente perimetre
                + 1  # parente topics
                + 1  # parente departement?
                + 1  # parente region?
            ),
        ):
            response = api_client.get(f"{self.url}")
        assert response.status_code == 200
        # Results are sorted by ID.
        assert response.json()["results"][1]["id"] == str(secondary_procedure.id)
        assert response.json()["results"][1] == snapshot()
