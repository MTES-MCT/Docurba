import uuid

import pytest
from django.urls import reverse
from pytest_django.asserts import assertQuerySetEqual

from docurba.core.enums import CommuneType, ProcedureType, TypeCollectivite
from docurba.core.models import (
    Collectivite,
    Commune,
    Procedure,
    Project,
    Topic,
    TypeDocument,
)
from docurba.users.models import Profile
from tests.conftest import SupabaseApiClient
from tests.core.factories import (
    CollectiviteFactory,
    CommuneFactory,
)
from tests.users.factories import ProfileFactory


@pytest.mark.django_db
class TestPrincipalProcedureCreation:
    @property
    def url(self) -> str:
        return reverse("internal_api:procedures-list")

    def _default_post_data(
        self,
        collectivite: Collectivite,
        perimetre: list[Commune],
    ) -> dict:
        return {
            "type": ProcedureType.ABROGATION,
            "collectiviteCode": collectivite.siren,
            "perimetreCommunesCodes": perimetre,
            "docType": TypeDocument.PLUI,
            "numero": "",
            "name": "Computed name",
            "startedBeforeHuwartLaw": True,
            "topics": ["zan", "coastline", "other"],
            "otherTopicComment": "I love coastlines.",
        }

    def _assert_default_procedure_creation(
        self, procedure: Procedure, logged_in_profile: Profile, post_data: dict
    ) -> None:
        assert procedure.started_before_huwart_law is True
        assert procedure.type == ProcedureType.ABROGATION
        assert procedure.doc_type == post_data["docType"]
        assert procedure.numero == "1"
        assert procedure.name == post_data["name"]
        # assert procedure.shareable
        assert procedure.parente is None
        assert procedure.is_principale is True
        assert procedure.status == "en cours"
        assert procedure.is_sectoriel is None
        assert procedure.vaut_PDM is False
        assert procedure.vaut_PLH is False
        assert procedure.testing is True
        assert procedure.owner_id == uuid.UUID(logged_in_profile.user_id)

    def _assert_default_commune_procedure_creation(self, procedure: Procedure) -> None:
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
        self, procedure: Procedure, post_data: dict
    ) -> None:
        assertQuerySetEqual(
            procedure.topics.all(), Topic.objects.filter(name__in=post_data["topics"])
        )
        assert (
            procedure.topics_through.get(topic__name="other").comment
            == post_data["otherTopicComment"]
        )

    def _assert_default_project_creation(
        self, procedure: Procedure, project: Project
    ) -> None:
        assert project.name == f"{procedure.type} {procedure.doc_type}"
        assert project.doc_type == procedure.doc_type
        assert project.current_perimetre == procedure.current_perimetre
        assert project.test is True
        assert project.region == "76"  # Occitanie

    def test_collectivite_is_intermunicipality__nominal(
        self,
        api_client_with_auth: SupabaseApiClient,
    ) -> None:
        # This test assumes no one has the jurisdiction because
        # collectivite.competence_plan and collectivite.competence_schema
        # are False by default.
        # In this particular case, which should not happen in the reality,
        # the system chooses the collectivite to be the `collectivite porteuse``.
        # Jurisdiction are omitted in this test to avoid `collectivite porteuse` differences.
        # They are tested separately.
        collectivite = CollectiviteFactory(
            for_snapshot=True,
            with_flat_members=True,
            with_flat_members__for_snapshot=True,
        )
        perimetre_insee_codes = collectivite.flat_members.filter(
            type=CommuneType.COM
        ).values_list("code_insee", flat=True)
        data = self._default_post_data(
            collectivite=collectivite, perimetre=perimetre_insee_codes
        )
        logged_in_profile = ProfileFactory(
            with_collectivite=True, with_collectivite__collectivite=collectivite
        )
        with api_client_with_auth(logged_in_profile) as api_client:
            response = api_client.post(self.url, data=data)
        assert response.status_code == 201

        assert Procedure.objects.count() == 1
        procedure = Procedure.objects.first()
        assert response.json()["id"] == str(procedure.id)
        assert response.json()["project_id"] == str(procedure.project.id)

        self._assert_default_procedure_creation(
            procedure=procedure, logged_in_profile=logged_in_profile, post_data=data
        )
        assert procedure.vaut_SCoT is False

        assert procedure.departements == ["30"]
        assert procedure.collectivite_porteuse_id == collectivite.code_insee_unique
        assert sorted(
            procedure.perimetre.values_list("code_insee", flat=True)
        ) == sorted(perimetre_insee_codes)
        assert procedure.current_perimetre == [
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
        assert project.collectivite_id == collectivite.code_insee_unique
        assert project.collectivite_porteuse_id == collectivite.code_insee_unique

    def test_collectivite_is_municipality__nominal(
        self, api_client_with_auth: SupabaseApiClient
    ) -> None:
        collectivite = CommuneFactory(for_snapshot=True)
        logged_in_profile = ProfileFactory(
            with_collectivite=True, with_collectivite__collectivite=collectivite
        )
        perimetre_codes_insee = [collectivite.code_insee]
        post_data = self._default_post_data(
            collectivite=collectivite, perimetre=perimetre_codes_insee
        ) | {
            "collectiviteCode": collectivite.code_insee,
            "docType": TypeDocument.PLU,
        }
        with api_client_with_auth(profile=logged_in_profile) as api_client:
            response = api_client.post(self.url, data=post_data)
        assert response.status_code == 201
        assert Procedure.objects.count() == 1

        ## PROCEDURE
        procedure = Procedure.objects.first()
        self._assert_default_procedure_creation(
            procedure=procedure,
            logged_in_profile=logged_in_profile,
            post_data=post_data,
        )
        assert procedure.vaut_SCoT is False
        assert procedure.collectivite_porteuse_id == collectivite.code_insee_unique
        assert sorted(
            procedure.perimetre.values_list("code_insee", flat=True)
        ) == sorted(perimetre_codes_insee)
        assert procedure.current_perimetre == [
            {"name": "Beaucaire", "inseeCode": "30032"}
        ]
        assert procedure.perimetre.count() == 1

        commune_procedure = procedure.perimetre_through.first()
        assert commune_procedure.collectivite_code == "30032"
        assert commune_procedure.collectivite_type == CommuneType.COM
        assert commune_procedure.departement == "30"
        assert commune_procedure.opposable is False

        self._assert_default_topics_creation(procedure=procedure, post_data=post_data)

        ## PROJECT
        project = procedure.project
        self._assert_default_project_creation(procedure=procedure, project=project)
        assert project.collectivite_id == collectivite.code_insee_unique
        assert project.collectivite_porteuse_id == collectivite.code_insee_unique

    #############################################################
    ################ Test collectivite porteuse #################
    #############################################################
    def test_collectivite_porteuse__is_municipality_with_intermunicipality_and_jurisdiction(
        self,
        api_client_with_auth: SupabaseApiClient,
    ) -> None:
        """The municipality has the jurisdiction, intermunicipality not.
        The selected collectivite is the municipality.
        """  # noqa: D205
        commune = CommuneFactory(
            code_insee="30032",
            competence_plan=True,
            competence_schema=True,
        )
        intercommunalite = CollectiviteFactory(
            for_snapshot=True,
            type=TypeCollectivite.CC,
            with_members=True,
            with_members__list=[commune],
            competence_plan=False,
            competence_schema=False,
        )
        commune.intercommunalite = intercommunalite
        commune.save()

        assert Procedure.objects.count() == 0
        post_data = self._default_post_data(
            collectivite=commune, perimetre=[commune.code_insee]
        ) | {"collectiviteCode": commune.code_insee, "docType": TypeDocument.PLU}
        logged_in_profile = ProfileFactory(
            with_collectivite=True, with_collectivite__collectivite=commune
        )
        with api_client_with_auth(logged_in_profile) as api_client:
            response = api_client.post(self.url, data=post_data)
        assert response.status_code == 201
        assert Procedure.objects.count() == 1

        procedure = Procedure.objects.first()
        self._assert_default_procedure_creation(
            procedure=procedure,
            logged_in_profile=logged_in_profile,
            post_data=post_data,
        )
        assert procedure.vaut_SCoT is False
        assert procedure.collectivite_porteuse_id == commune.code_insee_unique

        self._assert_default_commune_procedure_creation(procedure=procedure)
        self._assert_default_topics_creation(procedure=procedure, post_data=post_data)

        ## PROJECT
        project = procedure.project
        self._assert_default_project_creation(procedure=procedure, project=project)
        assert project.collectivite_id == intercommunalite.code_insee_unique
        assert project.collectivite_porteuse_id == commune.code_insee_unique

    def test_collectivite_porteuse__is_municipality_with_intermunicipality_and_jurisdiction_for_both(
        self,
        api_client_with_auth: SupabaseApiClient,
    ) -> None:
        """The municipality has the jurisdiction, intermunicipality too.
        The municipality stays the collectivite porteuse.
        The selected collectivite is the municipality.
        """  # noqa: D205
        commune = CommuneFactory(
            code_insee="30032",
            competence_plan=True,
            competence_schema=True,
        )
        intercommunalite = CollectiviteFactory(
            for_snapshot=True,
            type=TypeCollectivite.CC,
            with_members=True,
            with_members__list=[commune],
            competence_plan=True,
            competence_schema=True,
        )
        commune.intercommunalite = intercommunalite
        commune.save()

        assert Procedure.objects.count() == 0
        post_data = self._default_post_data(
            collectivite=commune, perimetre=[commune.code_insee]
        ) | {"collectiviteCode": commune.code_insee, "docType": TypeDocument.PLU}
        logged_in_profile = ProfileFactory(
            with_collectivite=True, with_collectivite__collectivite=commune
        )
        with api_client_with_auth(logged_in_profile) as api_client:
            response = api_client.post(self.url, data=post_data)
        assert response.status_code == 201
        assert Procedure.objects.count() == 1

        procedure = Procedure.objects.first()
        self._assert_default_procedure_creation(
            procedure=procedure,
            logged_in_profile=logged_in_profile,
            post_data=post_data,
        )
        assert procedure.vaut_SCoT is False
        assert procedure.collectivite_porteuse_id == commune.code_insee_unique

        self._assert_default_commune_procedure_creation(procedure=procedure)
        self._assert_default_topics_creation(procedure=procedure, post_data=post_data)

        ## PROJECT
        project = procedure.project
        self._assert_default_project_creation(procedure=procedure, project=project)
        assert project.collectivite_id == intercommunalite.code_insee_unique
        assert project.collectivite_porteuse_id == commune.code_insee_unique

    def test_collectivite_porteuse__is_municipality_with_intermunicipality_and_no_jurisdiction(
        self,
        api_client_with_auth: SupabaseApiClient,
    ) -> None:
        """The municipality does not have the jurisdiction.
        # It has been transfered to the intermunicipality.
        The intermunicipality is the collectivite porteuse.
        The selected collectivite is the municipality.
        """  # noqa: D205
        commune = CommuneFactory(
            code_insee="30032",
            competence_plan=False,
            competence_schema=False,
        )
        intercommunalite = CollectiviteFactory(
            for_snapshot=True,
            type=TypeCollectivite.CC,
            with_members=True,
            with_members__list=[commune],
            competence_plan=True,
            competence_schema=True,
        )
        commune.intercommunalite = intercommunalite
        commune.save()

        assert Procedure.objects.count() == 0
        post_data = self._default_post_data(
            collectivite=commune, perimetre=[commune.code_insee]
        ) | {"collectiviteCode": commune.code_insee, "docType": TypeDocument.PLU}
        logged_in_profile = ProfileFactory(
            with_collectivite=True, with_collectivite__collectivite=commune
        )
        with api_client_with_auth(logged_in_profile) as api_client:
            response = api_client.post(self.url, data=post_data)
        assert response.status_code == 201
        assert Procedure.objects.count() == 1

        procedure = Procedure.objects.first()
        self._assert_default_procedure_creation(
            procedure=procedure,
            logged_in_profile=logged_in_profile,
            post_data=post_data,
        )
        assert procedure.vaut_SCoT is False
        assert procedure.collectivite_porteuse_id == intercommunalite.code_insee_unique

        self._assert_default_commune_procedure_creation(procedure=procedure)
        self._assert_default_topics_creation(procedure=procedure, post_data=post_data)

        ## PROJECT
        project = procedure.project
        self._assert_default_project_creation(procedure=procedure, project=project)
        assert project.collectivite_id == intercommunalite.code_insee_unique
        assert project.collectivite_porteuse_id == intercommunalite.code_insee_unique

    def test_collectivite_porteuse__is_intermunicipality_without_jurisdiction(
        self,
        api_client_with_auth: SupabaseApiClient,
    ) -> None:
        """The municipalities has the jurisdiction, intermunicipality not.
        The collectivite porteuse is the intermunicipality.
        The selected collectivite is the intermunicipality.
        """  # noqa: D205
        # Selected only one commune will be blocked soon to encourage
        # user to select the commune as the communalite.
        # That's why there are two communes here.
        communes = [
            CommuneFactory(
                code_insee="30032",
                competence_plan=True,
                competence_schema=True,
            ),
            CommuneFactory(
                code_insee="30034",
                competence_plan=True,
                competence_schema=True,
            ),
        ]
        intercommunalite = CollectiviteFactory(
            for_snapshot=True,
            type=TypeCollectivite.CC,
            with_members=True,
            with_members__list=communes,
            competence_plan=False,
            competence_schema=False,
        )
        for commune in communes:
            commune.intercommunalite = intercommunalite
            commune.save()

        assert Procedure.objects.count() == 0
        # This should create a PLUIS and will be blocked soon.
        post_data = self._default_post_data(
            collectivite=intercommunalite, perimetre=["30032", "30034"]
        ) | {
            "collectiviteCode": intercommunalite.siren,
            "docType": TypeDocument.PLUIS,
        }
        logged_in_profile = ProfileFactory(
            with_collectivite=True, with_collectivite__collectivite=intercommunalite
        )
        with api_client_with_auth(logged_in_profile) as api_client:
            response = api_client.post(self.url, data=post_data)
        assert response.status_code == 201
        assert Procedure.objects.count() == 1

        procedure = Procedure.objects.first()
        self._assert_default_procedure_creation(
            procedure=procedure,
            logged_in_profile=logged_in_profile,
            post_data=post_data,
        )
        assert procedure.vaut_SCoT is False
        assert procedure.collectivite_porteuse_id == intercommunalite.code_insee_unique

        self._assert_default_commune_procedure_creation(procedure=procedure)
        self._assert_default_topics_creation(procedure=procedure, post_data=post_data)

        ## PROJECT
        project = procedure.project
        self._assert_default_project_creation(procedure=procedure, project=project)
        assert project.collectivite_id == intercommunalite.code_insee_unique
        assert project.collectivite_porteuse_id == intercommunalite.code_insee_unique

    def test_collectivite_porteuse__is_intermunicipality_with_jurisdiction(
        self,
        api_client_with_auth: SupabaseApiClient,
    ) -> None:
        """The intermunicipality has the jurisdiction.
        The selected collectivite is the intermunicipality.
        The intermunicipality is the collectivite porteuse.
        """  # noqa: D205
        # Selected only one commune will be blocked soon to encourage
        # user to select the commune as the communalite.
        # That's why there are two communes here.
        communes = [
            CommuneFactory(
                code_insee="30032",
                competence_plan=True,
                competence_schema=True,
            ),
            CommuneFactory(
                code_insee="30034",
                competence_plan=True,
                competence_schema=True,
            ),
        ]
        intercommunalite = CollectiviteFactory(
            for_snapshot=True,
            type=TypeCollectivite.CC,
            with_members=True,
            with_members__list=communes,
            competence_plan=False,
            competence_schema=False,
        )
        for commune in communes:
            commune.intercommunalite = intercommunalite
            commune.save()

        assert Procedure.objects.count() == 0
        post_data = self._default_post_data(
            collectivite=commune, perimetre=[commune.code_insee]
        ) | {"collectiviteCode": intercommunalite.siren, "docType": TypeDocument.PLUIS}
        logged_in_profile = ProfileFactory(
            with_collectivite=True, with_collectivite__collectivite=intercommunalite
        )
        with api_client_with_auth(logged_in_profile) as api_client:
            response = api_client.post(self.url, data=post_data)
        assert response.status_code == 201
        assert Procedure.objects.count() == 1

        procedure = Procedure.objects.first()
        self._assert_default_procedure_creation(
            procedure=procedure,
            logged_in_profile=logged_in_profile,
            post_data=post_data,
        )
        assert procedure.vaut_SCoT is False
        assert procedure.collectivite_porteuse_id == intercommunalite.code_insee_unique

        self._assert_default_commune_procedure_creation(procedure=procedure)
        self._assert_default_topics_creation(procedure=procedure, post_data=post_data)

        ## PROJECT
        project = procedure.project
        self._assert_default_project_creation(procedure=procedure, project=project)
        assert project.collectivite_id == intercommunalite.code_insee_unique
        assert project.collectivite_porteuse_id == intercommunalite.code_insee_unique

    def test_no_other_topic_but_topic_comment(
        self, api_client_with_auth: SupabaseApiClient
    ) -> None:
        collectivite = CollectiviteFactory(
            for_snapshot=True,
            with_flat_members=True,
            with_flat_members__for_snapshot=True,
        )
        logged_in_profile = ProfileFactory(
            with_collectivite=True, with_collectivite__collectivite=collectivite
        )

        perimetre_insee_codes = collectivite.flat_members.filter(
            type=CommuneType.COM
        ).values_list("code_insee", flat=True)

        data = self._default_post_data(
            collectivite=collectivite, perimetre=perimetre_insee_codes
        ) | {"topics": ["zan", "coastline"], "otherTopicComment": "I love coastlines."}
        with api_client_with_auth(logged_in_profile) as api_client:
            response = api_client.post(self.url, data=data)
        assert response.status_code == 400

    def test_other_topic_no_comment(
        self, api_client_with_auth: SupabaseApiClient
    ) -> None:
        collectivite = CollectiviteFactory(
            for_snapshot=True,
            with_flat_members=True,
            with_flat_members__for_snapshot=True,
        )
        perimetre_insee_codes = collectivite.flat_members.filter(
            type=CommuneType.COM
        ).values_list("code_insee", flat=True)
        data = self._default_post_data(
            collectivite=collectivite, perimetre=perimetre_insee_codes
        ) | {
            "topics": ["zan", "coastline", "other"],
            "otherTopicComment": "",
        }
        logged_in_profile = ProfileFactory(
            with_collectivite=True, with_collectivite__collectivite=collectivite
        )
        with api_client_with_auth(logged_in_profile) as api_client:
            response = api_client.post(self.url, data=data)

        assert response.status_code == 400
        assert (
            response.json()["non_field_errors"][0]
            == "Un commentaire est obligatoire car l'objet Autre a été sélectionné."
        )
        assert Procedure.objects.count() == 0

    def test_other_topic_comment_no_other_topic(
        self, api_client_with_auth: SupabaseApiClient
    ) -> None:
        collectivite = CollectiviteFactory(
            for_snapshot=True,
            with_flat_members=True,
            with_flat_members__for_snapshot=True,
        )
        perimetre_insee_codes = collectivite.flat_members.filter(
            type=CommuneType.COM
        ).values_list("code_insee", flat=True)
        data = self._default_post_data(
            collectivite=collectivite, perimetre=perimetre_insee_codes
        ) | {
            "topics": ["zan", "coastline"],
            "otherTopicComment": "I love coastlines",
        }
        logged_in_profile = ProfileFactory(
            with_collectivite=True, with_collectivite__collectivite=collectivite
        )
        with api_client_with_auth(logged_in_profile) as api_client:
            response = api_client.post(self.url, data=data)

        assert response.status_code == 400
        assert (
            response.json()["non_field_errors"][0]
            == "Un commentaire Autre ne peut être enregistré que pour l'objet Autre."
        )
        assert Procedure.objects.count() == 0

    @pytest.mark.parametrize(
        ("doc_types", "nb_communes_in_perimetre", "expected_error_message"),
        [
            pytest.param(
                ["PLUi", "PLUiH", "PLUiM", "PLUiHM", "SCOT"],
                1,
                "est un document intercommunal mais une seule commune fait partie du périmètre de la procédure.",
                id="forbidden_intercommunal_types",
            ),
            pytest.param(
                ["CC", "PLU"],
                2,
                "est un document communal mais plusieurs communes font partie du périmètre de la procédure.",
                id="forbidden_communal_types",
            ),
        ],
    )
    def test_doc_type_len_perimetre__validation_error(
        self,
        api_client_with_auth: SupabaseApiClient,
        subtests: pytest.Subtests,
        doc_types: list,
        nb_communes_in_perimetre: int,
        expected_error_message: str,
    ) -> None:
        communes = CommuneFactory.create_batch(nb_communes_in_perimetre)
        collectivite = CollectiviteFactory(
            for_snapshot=True,
            with_members=True,
            with_members__list=communes,
        )
        perimetre_insee_codes = collectivite.flat_members.filter(
            type=CommuneType.COM
        ).values_list("code_insee", flat=True)
        for doc_type in doc_types:
            with subtests.test(doc_type, doc_type=doc_type):
                data = self._default_post_data(
                    collectivite=collectivite, perimetre=perimetre_insee_codes
                ) | {
                    "docType": doc_type,
                }
                logged_in_profile = ProfileFactory(
                    with_collectivite=True, with_collectivite__collectivite=collectivite
                )
                with api_client_with_auth(logged_in_profile) as api_client:
                    response = api_client.post(self.url, data=data)

                assert response.status_code == 400
                assert (
                    response.json()["non_field_errors"][0]
                    == f"{doc_type} {expected_error_message}"
                )
                assert Procedure.objects.count() == 0

    def test_procedure_interdepartment(
        self,
        api_client_with_auth: SupabaseApiClient,
    ) -> None:
        communes = [
            CommuneFactory(code_insee="30032"),
            CommuneFactory(code_insee="13001"),
        ]
        collectivite = CollectiviteFactory(
            for_snapshot=True,
            with_members=True,
            with_members__list=communes,
        )
        perimetre_insee_codes = collectivite.flat_members.filter(
            type=CommuneType.COM
        ).values_list("code_insee", flat=True)
        data = self._default_post_data(
            collectivite=collectivite, perimetre=perimetre_insee_codes
        )
        logged_in_profile = ProfileFactory(
            with_collectivite=True, with_collectivite__collectivite=collectivite
        )
        with api_client_with_auth(logged_in_profile) as api_client:
            response = api_client.post(self.url, data=data)
        assert response.status_code == 201

        assert Procedure.objects.count() == 1
        procedure = Procedure.objects.first()
        assert response.json()["id"] == str(procedure.id)
        assert response.json()["project_id"] == str(procedure.project.id)

        self._assert_default_procedure_creation(
            procedure=procedure, logged_in_profile=logged_in_profile, post_data=data
        )
        assert procedure.vaut_SCoT is False
        assert sorted(procedure.departements) == ["13", "30"]
        self._assert_default_commune_procedure_creation(procedure=procedure)
        self._assert_default_project_creation(
            procedure=procedure, project=procedure.project
        )
