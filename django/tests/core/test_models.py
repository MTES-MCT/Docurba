# ruff: noqa: FBT001, N803
from collections.abc import Callable
from contextlib import nullcontext as does_not_raise
from datetime import UTC, date, datetime, timedelta
from functools import partial
from uuid import uuid4

import pytest
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import models
from django.utils import timezone
from freezegun import freeze_time
from pytest_django import DjangoAssertNumQueries

from docurba.core import enums as core_enums
from docurba.core import models as core_models
from tests.core.factories import (
    CollectiviteFactory,
    CommuneFactory,
    DepartementFactory,
    EventFactory,
    EventTypeFactory,
    ProcedureFactory,
    ProjectSharingFactory,
)
from tests.users.factories import ProfileFactory


@pytest.mark.django_db
class TestMaterializedViewFlatMembership:
    def test_through_memberships(
        self,
    ) -> None:
        grand_parent = CollectiviteFactory(
            with_flat_members=True,
        )
        parent = grand_parent.collectivites_adherentes.first()
        node = parent.collectivites_adherentes.first()

        CollectiviteFactory(
            with_flat_members=True,
        )
        assert core_models.Adhesion.objects.count() == 4
        assert core_models.MaterializedViewFlatMembership.objects.count() == 6

        assert hasattr(grand_parent, "flat_members")
        assert sorted(grand_parent.flat_members.values_list("id", flat=True)) == sorted(
            [
                parent.pk,
                node.pk,
            ]
        )

        assert hasattr(node, "flat_groups")
        assert sorted(node.flat_groups.values_list("id", flat=True)) == sorted(
            [
                grand_parent.pk,
                parent.pk,
            ]
        )

    def test_denormalized_data(
        self,
    ) -> None:
        collectivite = CollectiviteFactory(with_members=True)
        members = collectivite.adhesions.all()
        for member in members:
            assert core_models.MaterializedViewFlatMembership.objects.filter(
                member_id=member.id,
                member_type=member.type,
                group_id=collectivite.id,
                group_type=collectivite.type,
            ).exists()

    @pytest.mark.django_db
    def test_different_path_same_flat_membership(self) -> None:
        # Two path should lead to only one flat membership.
        # grand_child --> child 1 --> collectivite
        # grand_child --> child 2 --> collectivite
        collectivite = CollectiviteFactory()
        collectivite_children = CollectiviteFactory.create_batch(2)
        collectivite.collectivites_adherentes.add(*collectivite_children)
        grand_child = CollectiviteFactory()
        for child in collectivite_children:
            grand_child.adhesions.add(*[child])

        core_models.MaterializedViewFlatMembership().refresh()

        assert core_models.Adhesion.objects.count() == 4
        assert core_models.MaterializedViewFlatMembership.objects.count() == 5

        assert sorted(collectivite.flat_members.values_list("id", flat=True)) == sorted(
            [
                collectivite_children[0].pk,
                collectivite_children[1].pk,
                grand_child.pk,
            ]
        )

        assert sorted(
            collectivite_children[0].flat_members.values_list("id", flat=True)
        ) == sorted([grand_child.pk])

    def test_read_only(self) -> None:
        collectivite = CollectiviteFactory(with_members=True)
        flat_membership = collectivite.flat_members_through.first()
        flat_membership.group_id = CollectiviteFactory().pk
        with pytest.raises(PermissionDenied):
            flat_membership.save()

        with pytest.raises(PermissionDenied):
            flat_membership.delete()

        with pytest.raises(PermissionDenied):
            core_models.MaterializedViewFlatMembership.objects.create(
                member_id=CollectiviteFactory().pk, group_id=CollectiviteFactory().pk
            )

        with pytest.raises(PermissionDenied):
            core_models.MaterializedViewFlatMembership.objects.bulk_create()

        memberships = core_models.MaterializedViewFlatMembership.objects.all()
        for membership in memberships:
            membership.group_id = CollectiviteFactory().pk

        with pytest.raises(PermissionDenied):
            memberships.bulk_update(memberships, fields=["group_id"])

        with pytest.raises(PermissionDenied):
            memberships.delete()


@pytest.mark.django_db
class TestProcedureQuerySet:
    def test_with_concatenated_topics_as_string(
        self, django_assert_num_queries: DjangoAssertNumQueries
    ) -> None:
        topics = core_models.Topic.objects.filter(name__in=["zan", "forest_fire"])
        procedure = ProcedureFactory()
        procedure.topics.add(*topics)
        with django_assert_num_queries(1):
            procedure = (
                core_models.Procedure.objects.with_concatenated_topics_as_string().get(
                    pk=procedure.pk
                )
            )
        assert hasattr(procedure, "concatenated_topics_as_string")
        assert procedure.concatenated_topics_as_string == "Feu de forêt,Trajectoire ZAN"

    def test_with_events_archived(
        self, django_assert_num_queries: DjangoAssertNumQueries
    ) -> None:
        procedure = ProcedureFactory()
        event_not_archived = EventFactory(procedure=procedure)
        EventFactory(procedure=procedure, archived=True)

        with django_assert_num_queries(2):
            procedure = core_models.Procedure.objects.with_events().get(pk=procedure.pk)

        assert len(procedure.events_prefetched) == 1
        assert procedure.events_prefetched[0].id == event_not_archived.id

    def test_most_recently_shared_to_profile_email(self) -> None:
        guest = ProfileFactory()
        # Old sharing
        ProjectSharingFactory(
            user_email=guest.email,
            project__with_procedure=True,
            project__with_procedure__is_principale=True,
            role=core_enums.ProjectSharingRoleType.WRITE_FRISE,
            created_at=timezone.now() - timedelta(days=2),
        )
        sharing = ProjectSharingFactory(
            user_email=guest.email,
            project__with_procedure=True,
            project__with_procedure__is_principale=True,
            role=core_enums.ProjectSharingRoleType.WRITE_FRISE,
            created_at=timezone.now(),
        )
        expected_procedure = sharing.project.procedures.order_by("created_at").last()
        # Procedure is not principal.
        ProjectSharingFactory(
            user_email=guest.email,
            project__with_procedure=True,
            project__with_procedure__is_principale=False,
            role="write_frise",
        )
        # Project without procedure.
        ProjectSharingFactory(
            user_email=guest.email,
            role="write_frise",
        )
        # Wrong role
        ProjectSharingFactory(
            user_email=guest.email,
            project__with_procedure=True,
            project__with_procedure__is_principale=False,
            role="read",
        )

        # Other user
        ProjectSharingFactory(
            user_email="marthe@tarascon.com",
            project__with_procedure=True,
            project__with_procedure__is_principale=False,
            role="write_frise",
        )
        result = core_models.Procedure.objects.most_recently_shared_to_profile_email(
            email=guest.email
        )
        assert isinstance(result, core_models.Procedure) is True
        assert result == expected_procedure


class TestProcedureCommunesCounts:
    @pytest.mark.django_db
    def test_procedure_sectorielle_perimetre_inferieur_adhesions(
        self, django_assert_num_queries: DjangoAssertNumQueries
    ) -> None:
        collectivite = CollectiviteFactory()

        collectivite_enfant = CollectiviteFactory()
        collectivite_enfant.adhesions.add(collectivite)

        commune_enfant = CommuneFactory()
        commune_enfant.adhesions.add(collectivite)

        collectivite_grand_enfant = CollectiviteFactory()
        collectivite_grand_enfant.adhesions.add(collectivite_enfant)
        commune_grand_enfant = CommuneFactory()
        commune_grand_enfant.adhesions.add(collectivite_enfant)

        commune_grand_grand_enfant = CommuneFactory()
        commune_grand_grand_enfant.adhesions.add(collectivite_grand_enfant)
        core_models.MaterializedViewFlatMembership.refresh()

        procedure_sectorielle = ProcedureFactory(
            collectivite_porteuse=collectivite,
            doc_type=core_enums.TypeDocument.PLU,
            with_perimetre=[commune_enfant],
        )
        with django_assert_num_queries(1):
            procedure_sectorielle_with_counts = core_models.Procedure.objects.get(
                id=procedure_sectorielle.id
            )
            assert (
                procedure_sectorielle_with_counts.perimetre_without_deleguees_count == 1
            )
            assert (
                procedure_sectorielle_with_counts.collectivite_porteuse_communes_adherentes_count
                == 3
            )
            assert procedure_sectorielle_with_counts.is_sectoriel_consolide

    @pytest.mark.django_db
    def test_procedure_non_sectorielle(
        self, django_assert_num_queries: DjangoAssertNumQueries
    ) -> None:
        collectivite = CollectiviteFactory()

        collectivite_enfant = CollectiviteFactory()
        collectivite_enfant.adhesions.add(collectivite)

        commune_enfant = CommuneFactory()
        commune_enfant.adhesions.add(collectivite)

        collectivite_grand_enfant = CollectiviteFactory()
        collectivite_grand_enfant.adhesions.add(collectivite_enfant)
        commune_grand_enfant = CommuneFactory()
        commune_grand_enfant.adhesions.add(collectivite_enfant)

        commune_grand_grand_enfant = CommuneFactory()
        commune_grand_grand_enfant.adhesions.add(collectivite_grand_enfant)

        core_models.MaterializedViewFlatMembership.refresh()

        procedure_non_sectorielle = ProcedureFactory(
            collectivite_porteuse=collectivite,
            doc_type=core_enums.TypeDocument.PLU,
            with_perimetre=[
                commune_enfant,
                commune_grand_enfant,
                commune_grand_grand_enfant,
            ],
        )

        with django_assert_num_queries(1):
            procedure_non_sectorielle_with_counts = core_models.Procedure.objects.get(
                id=procedure_non_sectorielle.id
            )
            assert (
                procedure_non_sectorielle_with_counts.perimetre_without_deleguees_count
                == 3
            )
            assert (
                procedure_non_sectorielle_with_counts.collectivite_porteuse_communes_adherentes_count
                == 3
            )
            assert not procedure_non_sectorielle_with_counts.is_sectoriel_consolide

    @pytest.mark.django_db
    def test_exclut_commune_deleguee_du_perimetre_count(
        self, django_assert_num_queries: DjangoAssertNumQueries
    ) -> None:
        collectivite = CollectiviteFactory()

        commune_enfant = CommuneFactory()
        commune_enfant.adhesions.add(collectivite)

        commune_deleguee = CommuneFactory(nouvelle=commune_enfant)

        core_models.MaterializedViewFlatMembership.refresh()

        procedure = ProcedureFactory(
            collectivite_porteuse=collectivite,
            doc_type=core_enums.TypeDocument.PLU,
            with_perimetre=[commune_enfant, commune_deleguee],
        )

        with django_assert_num_queries(1):
            procedure_with_counts = core_models.Procedure.objects.get(id=procedure.id)
            assert procedure_with_counts.perimetre_without_deleguees_count == 1
            assert (
                procedure_with_counts.collectivite_porteuse_communes_adherentes_count
                == 1
            )

    @pytest.mark.django_db
    def test_retourne_zero_quand_pas_de_commune(
        self, django_assert_num_queries: DjangoAssertNumQueries
    ) -> None:
        collectivite = CollectiviteFactory()

        core_models.MaterializedViewFlatMembership.refresh()

        procedure = ProcedureFactory(
            collectivite_porteuse=collectivite, doc_type=core_enums.TypeDocument.PLU
        )

        with django_assert_num_queries(1):
            procedure_with_counts = core_models.Procedure.objects.get(id=procedure.id)
            assert procedure_with_counts.perimetre_without_deleguees_count == 0
            assert (
                procedure_with_counts.collectivite_porteuse_communes_adherentes_count
                == 0
            )


def test_tous_document_types_ont_event_category() -> None:
    assert list(core_enums.TypeDocument) == list(
        core_models.EVENT_CATEGORY_BY_DOC_TYPE.keys()
    )


@pytest.mark.django_db
class TestCollectivite:
    def test_code_insee_integrity(self) -> None:
        departement = DepartementFactory(code_insee="30")
        collectivite = CollectiviteFactory.build(
            type=core_enums.TypeCollectivite.CC,
            code_insee="12345",
            departement=departement,
        )
        with pytest.raises(
            ValidationError, match=r"Seules les communes peuvent avoir un code INSEE."
        ):
            collectivite.save()

        collectivite = CollectiviteFactory.build(
            type=core_enums.TypeCollectivite.COM,
            code_insee="12345",
            departement=departement,
        )
        with does_not_raise():
            collectivite.save()

    def test_filter_by_code(self) -> None:
        collectivite_with_siren = CollectiviteFactory(siren="123456789", code_insee="")
        collectivite_with_code_insee = CollectiviteFactory(
            siren="", code_insee="12345", type=core_enums.CommuneType.COM
        )
        siren_results = core_models.Collectivite.objects.filter_by_code(
            collectivite_with_siren.siren
        )
        code_insee_results = core_models.Collectivite.objects.filter_by_code(
            collectivite_with_code_insee.code_insee
        )
        assert collectivite_with_siren in siren_results
        assert collectivite_with_code_insee not in siren_results
        assert collectivite_with_siren not in code_insee_results
        assert collectivite_with_code_insee in code_insee_results


class TestCollectivitePortantScot:
    @pytest.mark.django_db
    def test_retourne_que_collectivite_avec_scot(
        self, django_assert_num_queries: DjangoAssertNumQueries
    ) -> None:
        collectivite_avec_scot = CollectiviteFactory()

        scot_en_cours = ProcedureFactory(
            collectivite_porteuse=collectivite_avec_scot,
            doc_type=core_enums.TypeDocument.SCOT,
        )
        scot_en_cours.event_set.create(
            type="Délibération de l'établissement public qui prescrit",
            date_evenement="2024-12-01",
        )

        _collectivite_sans_procedure = CollectiviteFactory()

        collectivite_avec_plan = CollectiviteFactory()

        ProcedureFactory(
            collectivite_porteuse=collectivite_avec_plan,
            doc_type=core_enums.TypeDocument.PLU,
        )

        with django_assert_num_queries(4):
            collectivites = list(core_models.Collectivite.objects.portant_scot())
            assert collectivites == [collectivite_avec_scot]

            assert collectivites[0].scots_pour_csv == [(None, scot_en_cours)]

    @pytest.mark.django_db
    def test_ignore_procedures_archivees(
        self, django_assert_num_queries: DjangoAssertNumQueries
    ) -> None:
        collectivite = CollectiviteFactory()

        scot_supprime = ProcedureFactory(
            collectivite_porteuse=collectivite,
            doc_type=core_enums.TypeDocument.SCOT,
            soft_delete=True,
        )

        _scot_doublon = ProcedureFactory(
            collectivite_porteuse=collectivite,
            doc_type=core_enums.TypeDocument.SCOT,
            doublon_cache_de=scot_supprime,
        )

        with django_assert_num_queries(1):
            assert list(core_models.Collectivite.objects.portant_scot()) == []

    @pytest.mark.django_db
    def test_ignore_procedures_secondaires(
        self, django_assert_num_queries: DjangoAssertNumQueries
    ) -> None:
        collectivite = CollectiviteFactory()
        parent_procedure = ProcedureFactory(
            collectivite_porteuse=collectivite,
            doc_type=core_enums.TypeDocument.SCOT,
            soft_delete=True,
        )

        ProcedureFactory(
            collectivite_porteuse=collectivite,
            doc_type=core_enums.TypeDocument.SCOT,
            parente=parent_procedure,
            archived=False,
        )

        with django_assert_num_queries(1):
            assert list(core_models.Collectivite.objects.portant_scot()) == []

    @pytest.mark.django_db
    def test_retourne_collectivites_distinctes(
        self,
        django_assert_num_queries: DjangoAssertNumQueries,
    ) -> None:
        collectivite_avec_scot = CollectiviteFactory()
        commune = CommuneFactory()

        scots_opposables = []
        for date_string in ("2024-02-01", "2024-02-02"):
            scot_opposable = ProcedureFactory(
                collectivite_porteuse=collectivite_avec_scot,
                doc_type=core_enums.TypeDocument.SCOT,
                with_perimetre=[commune],
            )
            scot_opposable.event_set.create(
                type="Délibération d'approbation", date_evenement=date_string
            )
            scots_opposables.append(scot_opposable)

        with django_assert_num_queries(6):
            collectivites = list(core_models.Collectivite.objects.portant_scot())
            assert collectivites == [collectivite_avec_scot]

            assert collectivites[0].scots_pour_csv == [(scots_opposables[1], None)]

    @pytest.mark.django_db
    def test_fonctionne_et_log_erreur_quand_plusieurs_scots_en_cours(
        self,
        django_assert_num_queries: DjangoAssertNumQueries,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        collectivite_avec_scot = CollectiviteFactory()

        scots_en_cours = []
        for _ in range(2):
            scot_en_cours = ProcedureFactory(
                collectivite_porteuse=collectivite_avec_scot,
                doc_type=core_enums.TypeDocument.SCOT,
            )
            scot_en_cours.event_set.create(
                type="Délibération de l'établissement public qui prescrit",
                date_evenement="2024-12-01",
            )
            scots_en_cours.append(scot_en_cours)

        with django_assert_num_queries(4):
            collectivites = list(core_models.Collectivite.objects.portant_scot())
            assert collectivites == [collectivite_avec_scot]

            assert len(collectivites[0].scots_pour_csv) == 1
            actual_opposable, actual_en_cours = collectivites[0].scots_pour_csv[0]
            assert actual_opposable is None
            assert actual_en_cours

            assert (
                f"Plusieurs SCoT en cours pour la collectivité {collectivite_avec_scot.code_insee}"
                in caplog.messages
            )

    @pytest.mark.django_db
    def test_retourne_scot_opposables_des_qu_une_commune_considere_opposable(
        self, django_assert_num_queries: DjangoAssertNumQueries
    ) -> None:
        collectivite = CollectiviteFactory()
        commune_a = CommuneFactory()
        commune_b = CommuneFactory()

        scot_opposable_a = ProcedureFactory(
            collectivite_porteuse=collectivite,
            doc_type=core_enums.TypeDocument.SCOT,
            type="A",
            with_perimetre=[commune_a],
        )
        scot_opposable_a.event_set.create(
            type="Délibération d'approbation", date_evenement="2024-01-01"
        )

        scot_precedent_a = ProcedureFactory(
            collectivite_porteuse=collectivite,
            doc_type=core_enums.TypeDocument.SCOT,
            type="B",
            with_perimetre=[commune_a],
        )
        scot_precedent_a.event_set.create(
            type="Délibération d'approbation", date_evenement="1999-01-01"
        )

        scot_opposable_a_et_b = ProcedureFactory(
            collectivite_porteuse=collectivite,
            doc_type=core_enums.TypeDocument.SCOT,
            type="C",
            with_perimetre=[commune_a, commune_b],
        )
        scot_opposable_a_et_b.event_set.create(
            type="Délibération d'approbation", date_evenement="2023-01-01"
        )

        with django_assert_num_queries(6):
            collectivites = list(core_models.Collectivite.objects.portant_scot())
            assert collectivites == [collectivite]

            assert set(collectivites[0].scots_pour_csv) == {
                (scot_opposable_a, None),
                (scot_opposable_a_et_b, None),
            }

    @pytest.mark.django_db
    def test_retourne_le_meme_scot_en_cours_pour_chaque_opposable(
        self,
        django_assert_num_queries: DjangoAssertNumQueries,
    ) -> None:
        collectivite_avec_scot = CollectiviteFactory()
        commune_a = CommuneFactory()
        commune_b = CommuneFactory()

        scot_en_cours = ProcedureFactory(
            collectivite_porteuse=collectivite_avec_scot,
            doc_type=core_enums.TypeDocument.SCOT,
        )
        scot_en_cours.event_set.create(
            type="Délibération de l'établissement public qui prescrit",
            date_evenement="2024-12-01",
        )

        scots_opposables = []
        for commune in [commune_a, commune_b]:
            scot_opposable = ProcedureFactory(
                collectivite_porteuse=collectivite_avec_scot,
                doc_type=core_enums.TypeDocument.SCOT,
                with_perimetre=[commune],
            )
            scot_opposable.event_set.create(
                type="Délibération d'approbation", date_evenement="2024-12-01"
            )
            scots_opposables.append(scot_opposable)

        with django_assert_num_queries(6):
            collectivites = list(core_models.Collectivite.objects.portant_scot())
            assert collectivites == [collectivite_avec_scot]

            assert set(collectivites[0].scots_pour_csv) == {
                (scots_opposables[0], scot_en_cours),
                (scots_opposables[1], scot_en_cours),
            }

    @pytest.mark.django_db
    @pytest.mark.parametrize(
        ("avant", "has_scot_opposable"),
        [
            ("", False),
            ("2025-12-13", True),
            ("2025-12-10", False),
        ],
    )
    def test_scot_caduc_est_opposable_si_interroge_avant_fin_d_echeance(
        self,
        avant: str,
        has_scot_opposable: bool,
        django_assert_num_queries: DjangoAssertNumQueries,
    ) -> None:
        collectivite_avec_scot = CollectiviteFactory()
        commune = CommuneFactory()

        scot_opposable = ProcedureFactory(
            collectivite_porteuse=collectivite_avec_scot,
            doc_type=core_enums.TypeDocument.SCOT,
            with_perimetre=[commune],
        )
        scot_opposable.event_set.create(
            type="Délibération d'approbation", date_evenement="2025-12-11"
        )
        scot_opposable.event_set.create(
            type="Fin d'échéance", date_evenement="2025-12-14"
        )

        with django_assert_num_queries(6):
            collectivites = list(
                core_models.Collectivite.objects.portant_scot(avant=avant)
            )
        assert collectivites == [collectivite_avec_scot]

        if has_scot_opposable:
            assert collectivites[0].scots_pour_csv == [(scot_opposable, None)]
        else:
            assert collectivites[0].scots_pour_csv == []


class TestScotInterdepartemental:
    @pytest.mark.django_db
    def test_un_departement(
        self,
        django_assert_num_queries: DjangoAssertNumQueries,
    ) -> None:
        collectivite_avec_scot = CollectiviteFactory()
        commune_a = CommuneFactory()
        commune_b = CommuneFactory(departement=commune_a.departement)

        scot_en_cours = ProcedureFactory(
            collectivite_porteuse=collectivite_avec_scot,
            doc_type=core_enums.TypeDocument.SCOT,
            with_perimetre=[commune_a, commune_b],
        )
        scot_en_cours.event_set.create(type="Prescription", date_evenement="2024-12-01")

        with django_assert_num_queries(6):
            collectivites = list(core_models.Collectivite.objects.portant_scot())
            assert collectivites == [collectivite_avec_scot]

            assert not collectivites[0].scots[0].is_interdepartemental

    @pytest.mark.django_db
    def test_plusieurs_departements(
        self,
        django_assert_num_queries: DjangoAssertNumQueries,
    ) -> None:
        collectivite_avec_scot = CollectiviteFactory()
        commune_a = CommuneFactory(departement__code_insee="13")
        commune_b = CommuneFactory(departement__code_insee="84")

        scot_en_cours = ProcedureFactory(
            collectivite_porteuse=collectivite_avec_scot,
            doc_type=core_enums.TypeDocument.SCOT,
            with_perimetre=[commune_a, commune_b],
        )
        scot_en_cours.event_set.create(type="Prescription", date_evenement="2024-12-01")

        with django_assert_num_queries(6):
            collectivites = list(core_models.Collectivite.objects.portant_scot())
            assert collectivites == [collectivite_avec_scot]

            assert collectivites[0].scots[0].is_interdepartemental


class TestProcedure:
    def test_is_schema(self) -> None:
        assert not core_models.Procedure(doc_type=core_enums.TypeDocument.CC).is_schema
        assert not core_models.Procedure(doc_type=core_enums.TypeDocument.PLU).is_schema
        assert not core_models.Procedure(
            doc_type=core_enums.TypeDocument.PLUI
        ).is_schema
        assert not core_models.Procedure(
            doc_type=core_enums.TypeDocument.PLUIM
        ).is_schema
        assert not core_models.Procedure(
            doc_type=core_enums.TypeDocument.PLUIH
        ).is_schema
        assert not core_models.Procedure(
            doc_type=core_enums.TypeDocument.PLUIHM
        ).is_schema

        assert core_models.Procedure(doc_type=core_enums.TypeDocument.SCOT).is_schema
        assert core_models.Procedure(doc_type=core_enums.TypeDocument.SD).is_schema

    @pytest.mark.django_db
    def test_liable_a_collectivite_porteuse_inexistante(self) -> None:
        """Tant que l'on ne gère pas bien les communes des anciens COG."""
        ProcedureFactory(collectivite_porteuse_id=12)

        assert core_models.Procedure.objects.count() == 1

    @pytest.mark.django_db
    def test_liable_a_commune_inexistante(self) -> None:
        """Tant que l'on ne gère pas bien les communes des anciens COG."""
        procedure = ProcedureFactory()
        procedure.perimetre.through.objects.create(
            collectivite_code=12,
            collectivite_type="COM",
            procedure=procedure,
        )

        assert procedure.perimetre.through.objects.count() == 1

    @pytest.mark.parametrize(
        "procedure_type",
        [core_enums.ProcedureType.ABROGATION, core_enums.ProcedureType.ELABORATION],
    )
    def test_principal_type(self, procedure_type: core_enums.ProcedureType) -> None:
        assert (
            core_models.Procedure(type=procedure_type).type
            in core_enums.ProcedureType.principal()
        )

    @pytest.mark.parametrize(
        "procedure_type",
        [
            core_enums.ProcedureType.MISE_A_JOUR,
            core_enums.ProcedureType.MISE_EN_COMPATIBILITE,
            core_enums.ProcedureType.MODIFICATION,
            core_enums.ProcedureType.MODIFICATION_SIMPLIFIEE,
            core_enums.ProcedureType.REVISION_MS_RA,
            core_enums.ProcedureType.REVISION_ALLEGEE,
            core_enums.ProcedureType.REVISION_SIMPLIFIEE,
        ],
    )
    def test_secondary_type(self, procedure_type: core_enums.ProcedureType) -> None:
        assert (
            core_models.Procedure(type=procedure_type).type
            in core_enums.ProcedureType.secondary()
        )

    @pytest.mark.django_db
    def test_computed_name(self) -> None:
        expected_name = "Procedure name"
        procedure = ProcedureFactory(name=expected_name)
        assert procedure.computed_name == expected_name

        expected_name = "Procedure name - with complement"
        procedure = ProcedureFactory(
            name="Procedure name", name_complement="with complement"
        )
        assert procedure.computed_name == expected_name

        expected_name = "Procedure name with complement"
        procedure = ProcedureFactory(
            name=expected_name, name_complement="with complement"
        )
        assert procedure.computed_name == expected_name

        # With zone name
        expected_name = (
            "Élaboration PLU Syndicat mixte d'équipement de la commune de Beaucaire"
        )
        procedure = ProcedureFactory(
            name="",
            collectivite_porteuse__for_snapshot=True,
            doc_type=core_enums.TypeDocument.PLU,
        )
        assert procedure.computed_name == expected_name

        # With zone name and numero
        expected_name = (
            "Élaboration 1 PLU Syndicat mixte d'équipement de la commune de Beaucaire"
        )
        procedure = ProcedureFactory(
            name="",
            numero="1",
            collectivite_porteuse__for_snapshot=True,
            doc_type=core_enums.TypeDocument.PLU,
        )
        assert procedure.computed_name == expected_name

        # With zone name, numero and name complement
        expected_name = "Élaboration 1 PLU Syndicat mixte d'équipement de la commune de Beaucaire - en cours"
        procedure = ProcedureFactory(
            name="",
            numero="1",
            name_complement="en cours",
            collectivite_porteuse__for_snapshot=True,
            doc_type=core_enums.TypeDocument.PLU,
        )
        assert procedure.computed_name == expected_name

    @pytest.mark.django_db
    def test_zone_name(self, django_assert_num_queries: DjangoAssertNumQueries) -> None:
        collectivite_porteuse = CollectiviteFactory(
            nom="CC de la Terre d'Argence", type=core_enums.TypeCollectivite.CC
        )

        # Zone composed of one town.
        procedure = ProcedureFactory(
            with_perimetre=[CommuneFactory(nom="Beaucaire")],
            collectivite_porteuse=collectivite_porteuse,
        )
        assert procedure.zone_name == "Beaucaire"

        # Zone composed of two towns.
        procedure = ProcedureFactory(
            with_perimetre=[
                CommuneFactory(nom="Beaucaire"),
                CommuneFactory(nom="Argilliers"),
            ],
            collectivite_porteuse=collectivite_porteuse,
        )
        assert procedure.zone_name == "CC de la Terre d'Argence"

        # Zone composed of two towns but only one is active.
        procedure = ProcedureFactory(
            with_perimetre=[
                CommuneFactory(nom="Beaucaire"),
                CommuneFactory(nom="Argilliers", type=core_enums.CommuneType.COMD),
            ],
            collectivite_porteuse=collectivite_porteuse,
        )
        assert procedure.zone_name == "CC de la Terre d'Argence"

        # Zone has a delegated town.
        procedure = ProcedureFactory(
            with_perimetre=[
                CommuneFactory(nom="Beaucaire"),
                CommuneFactory(nom="Nîmes"),
                CommuneFactory(nom="Argilliers", type=core_enums.CommuneType.COMD),
            ],
            collectivite_porteuse=collectivite_porteuse,
        )
        assert procedure.zone_name == "CC de la Terre d'Argence"

        # Zone has a delegated town. The procedure has effect only on this delegated town.
        delegated_town = CommuneFactory(
            nom="Argilliers", type=core_enums.CommuneType.COMD
        )
        procedure = ProcedureFactory(
            with_perimetre=[
                CommuneFactory(nom="Beaucaire"),
                CommuneFactory(nom="Nîmes"),
                delegated_town,
            ],
            collectivite_porteuse=collectivite_porteuse,
        )
        delegated_town_through = procedure.perimetre_through.get(
            commune_id=delegated_town.id
        )
        delegated_town_through.opposable = True
        delegated_town_through.save()

        # Assert num queries when the method is called with a prefetch or without.
        # - Without prefetch.
        with (
            django_assert_num_queries(2),
        ):
            assert procedure.zone_name == "Argilliers"
        # - With a prefetch.
        with (
            django_assert_num_queries(2),
        ):
            procedure = core_models.Procedure.objects.prefetch_related(
                models.Prefetch(
                    "perimetre", queryset=core_models.Commune.objects.with_opposable()
                )
            ).get(pk=procedure.pk)

        with (
            django_assert_num_queries(0),
        ):
            assert procedure.zone_name == "Argilliers"


class TestProcedureDates:
    @pytest.mark.django_db
    def test_none_quand_inexistantes(
        self, django_assert_num_queries: DjangoAssertNumQueries
    ) -> None:
        commune = CommuneFactory()
        ProcedureFactory(
            doc_type=core_enums.TypeDocument.SCOT, collectivite_porteuse=commune
        )

        with django_assert_num_queries(2):
            procedure = core_models.Procedure.objects.with_events().first()

            assert procedure.date_approbation is None
            assert procedure.date_prescription is None
            assert procedure.date_publication_perimetre is None
            assert procedure.date_arret_projet is None
            assert procedure.date_fin_echeance is None

    @pytest.mark.django_db
    @pytest.mark.parametrize(
        ("event_type", "date_attribute"),
        [
            ("Délibération d'approbation", "date_approbation"),
            ("Prescription", "date_prescription"),
            ("Publication périmètre", "date_publication_perimetre"),
            ("Arrêt de projet", "date_arret_projet"),
            ("Fin d'échéance", "date_fin_echeance"),
        ],
    )
    def test_retourne_plus_recent(
        self,
        event_type: str,
        date_attribute: str,
        django_assert_num_queries: DjangoAssertNumQueries,
    ) -> None:
        commune = CommuneFactory()
        procedure = ProcedureFactory(
            doc_type=core_enums.TypeDocument.SCOT,
            collectivite_porteuse=commune,
        )
        for date_string in ("2022-12-01", "2024-12-01", "2023-12-01"):
            procedure.event_set.create(type=event_type, date_evenement=date_string)

        with django_assert_num_queries(2):
            procedure_with_events = core_models.Procedure.objects.with_events().first()

            assert getattr(procedure_with_events, date_attribute) == date(2024, 12, 1)

    @pytest.mark.django_db
    @pytest.mark.parametrize(
        ("event_type", "date_attribute"),
        [
            ("Délibération d'approbation", "date_approbation"),
            ("Prescription", "date_prescription"),
            ("Publication périmètre", "date_publication_perimetre"),
            ("Arrêt de projet", "date_arret_projet"),
            ("Fin d'échéance", "date_fin_echeance"),
        ],
    )
    def test_ignore_event_pas_valid(
        self,
        event_type: str,
        date_attribute: str,
        django_assert_num_queries: DjangoAssertNumQueries,
    ) -> None:
        commune = CommuneFactory()
        procedure = ProcedureFactory(
            doc_type=core_enums.TypeDocument.SCOT, collectivite_porteuse=commune
        )
        procedure.event_set.create(
            type=event_type, date_evenement="2024-12-01", is_valid=False
        )

        with django_assert_num_queries(2):
            procedure_with_events = core_models.Procedure.objects.with_events().first()

            assert getattr(procedure_with_events, date_attribute) is None

    @pytest.mark.django_db
    @pytest.mark.parametrize(
        ("event_type", "date_attribute"),
        [
            ("Délibération d'approbation", "date_approbation"),
            ("Prescription", "date_prescription"),
            ("Publication périmètre", "date_publication_perimetre"),
            ("Arrêt de projet", "date_arret_projet"),
        ],
    )
    def test_ignore_event_apres(
        self,
        event_type: str,
        date_attribute: str,
        django_assert_num_queries: DjangoAssertNumQueries,
    ) -> None:
        """Ignore les événements après la date fournie, sauf pour les dates de fin d'échéance qui doivent toujours être récupérées."""
        commune = CommuneFactory()
        procedure = ProcedureFactory(
            doc_type=core_enums.TypeDocument.SCOT, collectivite_porteuse=commune
        )
        procedure.event_set.create(type=event_type, date_evenement="2022-12-01")
        procedure.event_set.create(type="Fin d'échéance", date_evenement="2022-12-01")

        with django_assert_num_queries(2):
            procedure_with_events = core_models.Procedure.objects.with_events(
                avant="2022-11-29"
            ).first()
            assert getattr(procedure_with_events, date_attribute) is None
            assert procedure_with_events.date_fin_echeance == date(2022, 12, 1)

        with django_assert_num_queries(2):
            procedure_with_events = core_models.Procedure.objects.with_events(
                avant="2022-11-30"
            ).first()
            assert getattr(procedure_with_events, date_attribute) is None
            assert procedure_with_events.date_fin_echeance == date(2022, 12, 1)

        with django_assert_num_queries(2):
            procedure_with_events = core_models.Procedure.objects.with_events(
                avant="2022-12-01"
            ).first()
            assert getattr(procedure_with_events, date_attribute) == date(2022, 12, 1)
            assert procedure_with_events.date_fin_echeance == date(2022, 12, 1)


class TestProcedureDocTypeDocument:
    def test_non_plu_like(self) -> None:
        assert (
            core_models.Procedure(doc_type=core_enums.TypeDocument.CC).type_document
            == core_enums.TypeDocument.CC
        )
        assert (
            core_models.Procedure(doc_type=core_enums.TypeDocument.SCOT).type_document
            == core_enums.TypeDocument.SCOT
        )
        assert (
            core_models.Procedure(doc_type=core_enums.TypeDocument.SD).type_document
            == core_enums.TypeDocument.SD
        )

    @pytest.mark.django_db
    @pytest.mark.parametrize(
        "doc_type",
        [
            (core_enums.TypeDocument.PLU),
            (core_enums.TypeDocument.PLUI),
            (core_enums.TypeDocument.PLUIH),
            (core_enums.TypeDocument.PLUIM),
            (core_enums.TypeDocument.PLUIHM),
        ],
    )
    def test_plu(
        self,
        doc_type: core_enums.TypeDocument,
        django_assert_num_queries: DjangoAssertNumQueries,
    ) -> None:
        commune = CommuneFactory()
        procedure = ProcedureFactory(
            doc_type=doc_type, collectivite_porteuse=commune, with_perimetre=[commune]
        )

        with django_assert_num_queries(1):
            procedure = core_models.Procedure.objects.get(id=procedure.id)
            assert procedure.type_document == core_enums.TypeDocument.PLU
            assert not procedure.vaut_PLH_consolide
            assert not procedure.vaut_PDM_consolide

    @pytest.mark.django_db
    @pytest.mark.parametrize(
        "doc_type",
        [
            (core_enums.TypeDocument.PLU),
            (core_enums.TypeDocument.PLUI),
        ],
    )
    def test_plui(
        self,
        doc_type: core_enums.TypeDocument,
        django_assert_num_queries: DjangoAssertNumQueries,
    ) -> None:
        commune_a = CommuneFactory()
        commune_b = CommuneFactory()

        procedure = ProcedureFactory(
            collectivite_porteuse=commune_a,
            doc_type=doc_type,
            with_perimetre=[commune_a, commune_b],
        )

        with django_assert_num_queries(1):
            procedure = core_models.Procedure.objects.get(id=procedure.id)
            assert procedure.type_document == core_enums.TypeDocument.PLUI
            assert not procedure.vaut_PLH_consolide
            assert not procedure.vaut_PDM_consolide

    @pytest.mark.django_db
    @pytest.mark.parametrize(
        ("doc_type", "vaut_PLH"),
        [
            (core_enums.TypeDocument.PLU, True),
            (core_enums.TypeDocument.PLUI, True),
            (core_enums.TypeDocument.PLUIH, False),
            (core_enums.TypeDocument.PLUIH, True),
        ],
    )
    def test_pluih(
        self,
        doc_type: core_enums.TypeDocument,
        vaut_PLH: bool,
        django_assert_num_queries: DjangoAssertNumQueries,
    ) -> None:
        commune_a = CommuneFactory()
        commune_b = CommuneFactory()

        procedure = ProcedureFactory(
            collectivite_porteuse=commune_a,
            doc_type=doc_type,
            vaut_PLH=vaut_PLH,
            with_perimetre=[commune_a, commune_b],
        )

        with django_assert_num_queries(1):
            procedure = core_models.Procedure.objects.get(id=procedure.id)
            assert procedure.type_document == core_enums.TypeDocument.PLUIH
            assert procedure.vaut_PLH_consolide
            assert not procedure.vaut_PDM_consolide

    @pytest.mark.django_db
    @pytest.mark.parametrize(
        ("doc_type", "vaut_PDM"),
        [
            (core_enums.TypeDocument.PLU, True),
            (core_enums.TypeDocument.PLUI, True),
            (core_enums.TypeDocument.PLUIM, False),
            (core_enums.TypeDocument.PLUIM, True),
        ],
    )
    def test_pluim(
        self,
        doc_type: core_enums.TypeDocument,
        vaut_PDM: bool,
        django_assert_num_queries: DjangoAssertNumQueries,
    ) -> None:
        commune_a = CommuneFactory()
        commune_b = CommuneFactory()

        procedure = ProcedureFactory(
            collectivite_porteuse=commune_a,
            doc_type=doc_type,
            vaut_PDM=vaut_PDM,
            with_perimetre=[commune_a, commune_b],
        )

        with django_assert_num_queries(1):
            procedure = core_models.Procedure.objects.get(id=procedure.id)
            assert procedure.type_document == core_enums.TypeDocument.PLUIM
            assert not procedure.vaut_PLH_consolide
            assert procedure.vaut_PDM_consolide

    @pytest.mark.django_db
    @pytest.mark.parametrize(
        ("doc_type", "vaut_PLH", "vaut_PDM"),
        [
            (core_enums.TypeDocument.PLU, True, True),
            (core_enums.TypeDocument.PLUI, True, True),
            (core_enums.TypeDocument.PLUIH, True, True),
            (core_enums.TypeDocument.PLUIM, True, True),
            (core_enums.TypeDocument.PLUIHM, False, False),
            (core_enums.TypeDocument.PLUIHM, False, True),
            (core_enums.TypeDocument.PLUIHM, True, False),
            (core_enums.TypeDocument.PLUIHM, True, True),
        ],
    )
    def test_pluihm(
        self,
        doc_type: core_enums.TypeDocument,
        vaut_PLH: bool,
        vaut_PDM: bool,
        django_assert_num_queries: DjangoAssertNumQueries,
    ) -> None:
        commune_a = CommuneFactory()
        commune_b = CommuneFactory()

        procedure = ProcedureFactory(
            collectivite_porteuse=commune_a,
            doc_type=doc_type,
            vaut_PLH=vaut_PLH,
            vaut_PDM=vaut_PDM,
            with_perimetre=[commune_a, commune_b],
        )

        with django_assert_num_queries(1):
            procedure = core_models.Procedure.objects.get(id=procedure.id)
            assert procedure.type_document == core_enums.TypeDocument.PLUIHM
            assert procedure.vaut_PLH_consolide
            assert procedure.vaut_PDM_consolide

    @pytest.mark.django_db
    @pytest.mark.parametrize(
        ("src_doc_type", "expected_doc_type"),
        [
            (core_enums.TypeDocument.PLU, core_enums.TypeDocument.PLUIS),
            (core_enums.TypeDocument.PLUI, core_enums.TypeDocument.PLUIS),
            (core_enums.TypeDocument.PLUIH, core_enums.TypeDocument.PLUISH),
            (core_enums.TypeDocument.PLUIM, core_enums.TypeDocument.PLUISM),
            (core_enums.TypeDocument.PLUIHM, core_enums.TypeDocument.PLUISHM),
        ],
    )
    def test_type_document_pour_procedure_sectorielle(
        self,
        src_doc_type: core_enums.TypeDocument,
        expected_doc_type: core_enums.TypeDocument,
    ) -> None:
        commune_a = CommuneFactory()
        commune_b = CommuneFactory()
        collectivite = CollectiviteFactory(
            with_members=True,
            with_members__list=[
                commune_a,
                commune_b,
                CommuneFactory(),
            ],
        )
        procedure = ProcedureFactory(
            doc_type=src_doc_type,
            collectivite_porteuse=collectivite,
            with_perimetre=[commune_a, commune_b],
        )
        procedure = core_models.Procedure.objects.get(id=procedure.id)
        assert procedure.type_document == expected_doc_type


class TestProcedureDelaiApprobation:
    @pytest.mark.django_db
    @pytest.mark.parametrize(
        ("date_approbation", "date_prescription"),
        [
            (None, None),
            ("2024-12-01", None),
            (None, "2024-01-01"),
        ],
    )
    def test_none_si_au_moins_une_date_absente(
        self, date_approbation: str, date_prescription: str
    ) -> None:
        commune = CommuneFactory()
        procedure = ProcedureFactory(
            doc_type=core_enums.TypeDocument.PLUI, collectivite_porteuse=commune
        )
        if date_approbation:
            procedure.event_set.create(
                type="Délibération d'approbation",
                date_evenement=date_approbation,
            )
        if date_prescription:
            procedure.event_set.create(
                type="Prescription", date_evenement=date_prescription
            )

        procedure_with_events = core_models.Procedure.objects.with_events().get(
            id=procedure.id
        )
        assert procedure_with_events.delai_d_approbation is None

    @pytest.mark.django_db
    def test_delai_d_approbation_calcule(self) -> None:
        commune = CommuneFactory()
        procedure = ProcedureFactory(
            doc_type=core_enums.TypeDocument.PLUI, collectivite_porteuse=commune
        )
        procedure.event_set.create(type="Prescription", date_evenement="2024-01-01")
        procedure.event_set.create(
            type="Délibération d'approbation", date_evenement="2024-02-01"
        )

        procedure_with_events = core_models.Procedure.objects.with_events().get(
            id=procedure.id
        )
        assert procedure_with_events.delai_d_approbation == 31


class TestProcedureSort:
    @pytest.mark.django_db
    def test_approuvee_plus_recemment(self) -> None:
        commune = CommuneFactory()
        procedure_recente = ProcedureFactory(
            doc_type=core_enums.TypeDocument.PLUI, collectivite_porteuse=commune
        )
        procedure_recente.event_set.create(
            type="Délibération d'approbation", date_evenement="2024-12-01"
        )

        procedure_vieille = ProcedureFactory(
            doc_type=core_enums.TypeDocument.PLUI, collectivite_porteuse=commune
        )
        procedure_vieille.event_set.create(
            type="Délibération d'approbation", date_evenement="2023-12-01"
        )

        procedure_recent_with_events = core_models.Procedure.objects.with_events().get(
            id=procedure_recente.id
        )
        procedure_vieille_with_events = core_models.Procedure.objects.with_events().get(
            id=procedure_vieille.id
        )
        assert procedure_vieille_with_events < procedure_recent_with_events

    @pytest.mark.django_db
    def test_prescrite_plus_recemment(self) -> None:
        commune = CommuneFactory()
        procedure_recente = ProcedureFactory(
            doc_type=core_enums.TypeDocument.PLUI, collectivite_porteuse=commune
        )
        procedure_recente.event_set.create(
            type="Prescription", date_evenement="2024-12-01"
        )

        procedure_vieille = ProcedureFactory(
            doc_type=core_enums.TypeDocument.PLUI, collectivite_porteuse=commune
        )
        procedure_vieille.event_set.create(
            type="Prescription", date_evenement="2023-12-01"
        )

        procedure_recent_with_events = core_models.Procedure.objects.with_events().get(
            id=procedure_recente.id
        )
        procedure_vieille_with_events = core_models.Procedure.objects.with_events().get(
            id=procedure_vieille.id
        )
        assert procedure_vieille_with_events < procedure_recent_with_events

    @pytest.mark.django_db
    def test_date_approbation_priorite_quand_date_entremelees(self) -> None:
        commune = CommuneFactory()
        procedure_recente = ProcedureFactory(
            doc_type=core_enums.TypeDocument.PLUI, collectivite_porteuse=commune
        )
        procedure_recente.event_set.create(
            type="Prescription", date_evenement="1999-12-01"
        )
        procedure_recente.event_set.create(
            type="Délibération d'approbation", date_evenement="2024-12-01"
        )

        procedure_vieille = ProcedureFactory(
            doc_type=core_enums.TypeDocument.PLUI, collectivite_porteuse=commune
        )
        procedure_vieille.event_set.create(
            type="Prescription", date_evenement="2023-12-01"
        )
        procedure_vieille.event_set.create(
            type="Délibération d'approbation", date_evenement="2023-12-02"
        )

        procedure_recent_with_events = core_models.Procedure.objects.with_events().get(
            id=procedure_recente.id
        )
        procedure_vieille_with_events = core_models.Procedure.objects.with_events().get(
            id=procedure_vieille.id
        )
        assert procedure_vieille_with_events < procedure_recent_with_events

    @pytest.mark.xfail(
        reason="created_at utilise le timestamp de la transaction, pas du statement"
    )
    @pytest.mark.django_db
    def test_sans_prescription_utilise_date_creation(self) -> None:
        commune = CommuneFactory()
        procedure_vieille = ProcedureFactory(
            doc_type=core_enums.TypeDocument.PLUI, collectivite_porteuse=commune
        )
        procedure_recente = ProcedureFactory(
            doc_type=core_enums.TypeDocument.PLUI, collectivite_porteuse=commune
        )

        procedure_recent_with_events = core_models.Procedure.objects.with_events().get(
            id=procedure_recente.id
        )
        procedure_vieille_with_events = core_models.Procedure.objects.with_events().get(
            id=procedure_vieille.id
        )

        assert procedure_vieille_with_events < procedure_recent_with_events
        assert not procedure_vieille_with_events > procedure_recent_with_events


class TestProcedureStatut:
    @pytest.mark.django_db
    def test_principale_opposable(
        self, django_assert_num_queries: DjangoAssertNumQueries
    ) -> None:
        commune = CommuneFactory()
        procedure = ProcedureFactory(
            doc_type=core_enums.TypeDocument.PLUI, collectivite_porteuse=commune
        )
        event = procedure.event_set.create(
            type="Délibération d'approbation", date_evenement="2024-12-01"
        )

        assert event.category == core_models.EventCategory.APPROUVE
        with django_assert_num_queries(2):
            procedure_with_events = core_models.Procedure.objects.with_events().get(
                id=procedure.id
            )

            assert procedure_with_events.dernier_event_impactant == event
            assert procedure_with_events.statut == core_models.EventCategory.APPROUVE

    @pytest.mark.django_db
    @pytest.mark.parametrize("is_approuve", [True, False])
    def test_sd_est_toujours_caduc(
        self, is_approuve: bool, django_assert_num_queries: DjangoAssertNumQueries
    ) -> None:
        """https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000028809968/2015-08-09."""
        commune = CommuneFactory()
        procedure = ProcedureFactory(
            doc_type=core_enums.TypeDocument.SD, collectivite_porteuse=commune
        )
        if is_approuve:
            event = procedure.event_set.create(
                type="Délibération d'approbation", date_evenement="2004-12-01"
            )
            assert event.category == core_models.EventCategory.APPROUVE

        with django_assert_num_queries(2):
            procedure_with_events = core_models.Procedure.objects.with_events().get(
                id=procedure.id
            )

            assert procedure_with_events.statut == core_models.EventCategory.CADUC

    @pytest.mark.django_db
    @pytest.mark.parametrize(
        ("annee_limite", "statut"),
        [
            (2029, core_models.EventCategory.APPROUVE),
            (2030, core_models.EventCategory.CADUC),
        ],
    )
    def test_fin_d_echeance_impacte_caducite(
        self,
        annee_limite: int,
        statut: str,
    ) -> None:
        commune = CommuneFactory()
        procedure = ProcedureFactory(
            doc_type=core_enums.TypeDocument.PLUI, collectivite_porteuse=commune
        )
        procedure.event_set.create(
            type="Délibération d'approbation", date_evenement="2024-12-01"
        )
        procedure.event_set.create(type="Fin d'échéance", date_evenement="2030-12-01")
        procedure_with_events = core_models.Procedure.objects.with_events(
            avant=date(annee_limite, 12, 15)
        ).get(id=procedure.id)

        assert procedure_with_events.statut == statut

    @pytest.mark.django_db
    @pytest.mark.parametrize(
        ("jour_limite", "statut"),
        [
            (2, None),
            (3, core_models.EventCategory.PRESCRIPTION),
            (4, core_models.EventCategory.PRESCRIPTION),
            (5, core_models.EventCategory.APPROUVE),
        ],
    )
    def test_ignore_event_apres(
        self,
        django_assert_num_queries: DjangoAssertNumQueries,
        jour_limite: int,
        statut: core_models.EventCategory,
    ) -> None:
        commune = CommuneFactory()
        procedure = ProcedureFactory(
            doc_type=core_enums.TypeDocument.PLUI, collectivite_porteuse=commune
        )
        event_prescription = procedure.event_set.create(
            type="Délibération de prescription du conseil municipal ou communautaire",
            date_evenement="2024-12-03",
        )
        event_approbation = procedure.event_set.create(
            type="Délibération d'approbation", date_evenement="2024-12-05"
        )

        assert event_prescription.category == core_models.EventCategory.PRESCRIPTION
        assert event_approbation.category == core_models.EventCategory.APPROUVE
        with django_assert_num_queries(2):
            procedure_with_events = core_models.Procedure.objects.with_events(
                avant=date(2024, 12, jour_limite)
            ).get(id=procedure.id)

            assert procedure_with_events.statut == statut

    @pytest.mark.django_db
    @pytest.mark.parametrize(
        ("delta_jour", "statut"),
        [
            (-1, core_models.EventCategory.APPROUVE),
            (0, core_models.EventCategory.APPROUVE),
            (1, None),
        ],
    )
    def test_ignore_event_apres_aujourdhui_si_pas_de_date_fournie(
        self,
        django_assert_num_queries: DjangoAssertNumQueries,
        delta_jour: int,
        statut: core_models.EventCategory,
    ) -> None:
        today = timezone.now().date()

        commune = CommuneFactory()
        procedure = ProcedureFactory(
            doc_type=core_enums.TypeDocument.PLUI, collectivite_porteuse=commune
        )
        event_approbation = procedure.event_set.create(
            type="Délibération d'approbation",
            date_evenement=today + timedelta(days=delta_jour),
        )

        assert event_approbation.category == core_models.EventCategory.APPROUVE
        with django_assert_num_queries(2):
            procedure_with_events = core_models.Procedure.objects.with_events().get(
                id=procedure.id
            )

            assert procedure_with_events.statut == statut

    @pytest.mark.django_db
    def test_principale_sans_evenement(
        self, django_assert_num_queries: DjangoAssertNumQueries
    ) -> None:
        commune = CommuneFactory()
        procedure = ProcedureFactory(
            doc_type=core_enums.TypeDocument.PLUI, collectivite_porteuse=commune
        )

        with django_assert_num_queries(2):
            procedure_with_events = core_models.Procedure.objects.with_events().get(
                id=procedure.id
            )

            assert not procedure_with_events.dernier_event_impactant
            assert not procedure_with_events.statut

    @pytest.mark.django_db
    def test_principale_annule(
        self, django_assert_num_queries: DjangoAssertNumQueries
    ) -> None:
        commune = CommuneFactory()
        procedure = ProcedureFactory(
            doc_type=core_enums.TypeDocument.PLUI, collectivite_porteuse=commune
        )
        event = procedure.event_set.create(
            type="Abrogation", date_evenement="2024-12-01"
        )

        assert event.category == core_models.EventCategory.ANNULE
        with django_assert_num_queries(2):
            procedure_with_events = core_models.Procedure.objects.with_events().get(
                id=procedure.id
            )

            assert procedure_with_events.dernier_event_impactant == event
            assert procedure_with_events.statut == core_models.EventCategory.ANNULE

    @pytest.mark.django_db
    def test_principale_ignore_event_invalide(
        self, django_assert_num_queries: DjangoAssertNumQueries
    ) -> None:
        commune = CommuneFactory()
        procedure = ProcedureFactory(
            doc_type=core_enums.TypeDocument.PLUI, collectivite_porteuse=commune
        )
        event = procedure.event_set.create(
            type="Délibération d'approbation",
            date_evenement="2024-12-01",
            is_valid=False,
        )

        assert event.category is None
        with django_assert_num_queries(2):
            procedure_with_events = core_models.Procedure.objects.with_events().get(
                id=procedure.id
            )

            assert not procedure_with_events.dernier_event_impactant
            assert not procedure_with_events.statut

    @pytest.mark.django_db
    def test_principale_carte_communale_deliberation_d_approbation_pas_opposable(
        self, django_assert_num_queries: DjangoAssertNumQueries
    ) -> None:
        commune = CommuneFactory()
        procedure = ProcedureFactory(
            doc_type=core_enums.TypeDocument.CC, collectivite_porteuse=commune
        )
        event = procedure.event_set.create(
            type="Délibération d'approbation", date_evenement="2024-12-01"
        )

        assert event.category is None
        with django_assert_num_queries(2):
            procedure_with_events = core_models.Procedure.objects.with_events().get(
                id=procedure.id
            )

            assert not procedure_with_events.dernier_event_impactant
            assert not procedure_with_events.statut

    @pytest.mark.django_db
    def test_secondaire_non_opposable(
        self, django_assert_num_queries: DjangoAssertNumQueries
    ) -> None:
        commune = CommuneFactory()
        procedure_principale = ProcedureFactory(
            doc_type=core_enums.TypeDocument.PLUI, collectivite_porteuse=commune
        )
        procedure_secondaire = ProcedureFactory(
            parente=procedure_principale,
            doc_type=core_enums.TypeDocument.PLUI,
            collectivite_porteuse=commune,
        )
        procedure_secondaire.event_set.create(
            type="Délibération d'approbation", date_evenement="2024-12-01"
        )

        with django_assert_num_queries(2):
            procedure_with_events = core_models.Procedure.objects.with_events().get(
                id=procedure_secondaire.id
            )

            assert not procedure_with_events.dernier_event_impactant
            assert not procedure_with_events.statut

    @pytest.mark.django_db
    def test_approuvee_quand_prescription_et_approbation_meme_jour(
        self, django_assert_num_queries: DjangoAssertNumQueries
    ) -> None:
        commune = CommuneFactory()
        procedure = ProcedureFactory(
            doc_type=core_enums.TypeDocument.PLUI, collectivite_porteuse=commune
        )
        prescription_inseree_avant = procedure.event_set.create(
            type="Prescription", date_evenement="2023-04-26"
        )
        approbation = procedure.event_set.create(
            type="Délibération d'approbation", date_evenement="2023-04-26"
        )
        prescription_inseree_apres = procedure.event_set.create(
            type="Prescription", date_evenement="2023-04-26"
        )

        assert approbation.category == core_models.EventCategory.APPROUVE
        assert (
            prescription_inseree_avant.category
            == core_models.EventCategory.PRESCRIPTION
        )
        assert (
            prescription_inseree_apres.category
            == core_models.EventCategory.PRESCRIPTION
        )

        with django_assert_num_queries(2):
            procedure_with_events = core_models.Procedure.objects.with_events().first()

            assert procedure_with_events.dernier_event_impactant == approbation
            assert procedure_with_events.statut == core_models.EventCategory.APPROUVE

    @pytest.mark.django_db
    def test_abandon_quand_prescription_et_abandon_meme_jour(
        self, django_assert_num_queries: DjangoAssertNumQueries
    ) -> None:
        commune = CommuneFactory()
        procedure = ProcedureFactory(
            doc_type=core_enums.TypeDocument.PLUI, collectivite_porteuse=commune
        )
        prescription_insere_avant = procedure.event_set.create(
            type="Prescription", date_evenement="2023-04-26"
        )
        abandon = procedure.event_set.create(
            type="Abandon", date_evenement="2023-04-26"
        )
        prescription_insere_apres = procedure.event_set.create(
            type="Prescription", date_evenement="2023-04-26"
        )

        assert abandon.category == core_models.EventCategory.ABANDON
        assert (
            prescription_insere_avant.category == core_models.EventCategory.PRESCRIPTION
        )
        assert (
            prescription_insere_apres.category == core_models.EventCategory.PRESCRIPTION
        )

        with django_assert_num_queries(2):
            procedure_with_events = core_models.Procedure.objects.with_events().first()

            assert procedure_with_events.dernier_event_impactant == abandon
            assert procedure_with_events.statut == core_models.EventCategory.ABANDON

    @pytest.mark.django_db
    def test_event_sans_date_ignore(
        self, django_assert_num_queries: DjangoAssertNumQueries
    ) -> None:
        commune = CommuneFactory()
        procedure = ProcedureFactory(
            doc_type=core_enums.TypeDocument.PLUI, collectivite_porteuse=commune
        )
        event = procedure.event_set.create(type="Délibération d'approbation")

        assert event.category == core_models.EventCategory.APPROUVE
        with django_assert_num_queries(2):
            procedure_with_events = core_models.Procedure.objects.with_events().get(
                id=procedure.id
            )

            assert not procedure_with_events.dernier_event_impactant
            assert not procedure_with_events.statut


def create_impactful_event(
    procedure: core_models.Procedure,
    impact: core_enums.ProcedureStatusChoices,
    *,
    date_evenement: date,
    **kwargs: dict,
) -> core_models.Event:
    # The uuid suffix prevents unique constraint violations when two events
    # share the same date and impact.
    event_type = EventTypeFactory(
        name=f"Type {impact} {date_evenement} {uuid4().hex[:8]}", impact=impact
    )
    return EventFactory(
        procedure=procedure,
        event_type=event_type,
        date_evenement=date_evenement,
        **kwargs,
    )


@pytest.mark.django_db
class TestProcedureComputeStatus:
    DATE_PIVOT = date(2025, 6, 15)

    def test_secondary_returns_none(self) -> None:
        procedure = ProcedureFactory(with_parente=True)

        assert procedure.compute_status(self.DATE_PIVOT) is None

    def test_without_event_returns_en_projet(self) -> None:
        procedure = ProcedureFactory()

        assert (
            procedure.compute_status(self.DATE_PIVOT)
            == core_enums.ProcedureStatusChoices.EN_PROJET
        )

    def test_status_from_most_recent_impactful_event(self) -> None:
        procedure = ProcedureFactory()
        create_impactful_event(
            procedure,
            core_enums.ProcedureStatusChoices.ABANDON,
            date_evenement=date(2024, 6, 1),
        )
        create_impactful_event(
            procedure,
            core_enums.ProcedureStatusChoices.OPPOSABLE,
            date_evenement=date(2025, 1, 1),
        )

        assert (
            procedure.compute_status(self.DATE_PIVOT)
            == core_enums.ProcedureStatusChoices.OPPOSABLE
        )

    def test_event_after_pivot_ignored(self) -> None:
        procedure = ProcedureFactory()
        create_impactful_event(
            procedure,
            core_enums.ProcedureStatusChoices.ABANDON,
            date_evenement=date(2024, 6, 1),
        )
        create_impactful_event(
            procedure,
            core_enums.ProcedureStatusChoices.OPPOSABLE,
            date_evenement=date(2025, 12, 1),
        )

        assert (
            procedure.compute_status(self.DATE_PIVOT)
            == core_enums.ProcedureStatusChoices.ABANDON
        )

    def test_archived_event_ignored(self) -> None:
        procedure = ProcedureFactory()
        create_impactful_event(
            procedure,
            core_enums.ProcedureStatusChoices.OPPOSABLE,
            date_evenement=date(2025, 1, 1),
            archived=True,
        )
        create_impactful_event(
            procedure,
            core_enums.ProcedureStatusChoices.ANNULE,
            date_evenement=date(2024, 6, 1),
        )

        assert (
            procedure.compute_status(self.DATE_PIVOT)
            == core_enums.ProcedureStatusChoices.ANNULE
        )

    def test_invalid_event_ignored(self) -> None:
        procedure = ProcedureFactory()
        create_impactful_event(
            procedure,
            core_enums.ProcedureStatusChoices.OPPOSABLE,
            date_evenement=date(2025, 1, 1),
            is_valid=False,
        )
        create_impactful_event(
            procedure,
            core_enums.ProcedureStatusChoices.ANNULE,
            date_evenement=date(2024, 6, 1),
        )

        assert (
            procedure.compute_status(self.DATE_PIVOT)
            == core_enums.ProcedureStatusChoices.ANNULE
        )

    def test_event_without_type_or_type_not_impactful_ignored(self) -> None:
        procedure = ProcedureFactory()
        # Event type not set.
        EventFactory(
            procedure=procedure, event_type=None, date_evenement=date(2025, 1, 1)
        )
        # Event type without impact.
        event_type_not_impactful = EventTypeFactory(
            name="Type without impact", impact=""
        )
        EventFactory(
            procedure=procedure,
            event_type=event_type_not_impactful,
            date_evenement=date(2025, 2, 1),
        )
        create_impactful_event(
            procedure,
            core_enums.ProcedureStatusChoices.ANNULE,
            date_evenement=date(2024, 6, 1),
        )

        assert (
            procedure.compute_status(self.DATE_PIVOT)
            == core_enums.ProcedureStatusChoices.ANNULE
        )

    def test_event_without_date_ignored(self) -> None:
        procedure = ProcedureFactory()
        # Events without a date (historical data) are ignored.
        event_type_without_date = EventTypeFactory(
            name="Type without date", impact=core_enums.ProcedureStatusChoices.OPPOSABLE
        )
        EventFactory(
            procedure=procedure,
            event_type=event_type_without_date,
            date_evenement=None,
        )
        create_impactful_event(
            procedure,
            core_enums.ProcedureStatusChoices.ANNULE,
            date_evenement=date(2024, 6, 1),
        )

        assert (
            procedure.compute_status(self.DATE_PIVOT)
            == core_enums.ProcedureStatusChoices.ANNULE
        )
        # Without date_pivot, the event without a date is still ignored.
        assert procedure.compute_status() == core_enums.ProcedureStatusChoices.ANNULE

    @freeze_time("2026-10-15")
    def test_without_date_pivot_no_date_filter(self) -> None:
        procedure = ProcedureFactory()
        create_impactful_event(
            procedure,
            core_enums.ProcedureStatusChoices.ANNULE,
            date_evenement=date(2024, 6, 1),
        )
        create_impactful_event(
            procedure,
            core_enums.ProcedureStatusChoices.OPPOSABLE,
            date_evenement=date(2026, 12, 1),
        )

        # Without date_pivot, no date filter is applied: the future event
        # counts.
        assert procedure.compute_status() == core_enums.ProcedureStatusChoices.OPPOSABLE
        # With a date_pivot before the future event, it is ignored.
        assert (
            procedure.compute_status(date(2025, 6, 15))
            == core_enums.ProcedureStatusChoices.ANNULE
        )

    def test_same_date_breaks_tie_on_created_at(self) -> None:
        procedure = ProcedureFactory()
        create_impactful_event(
            procedure,
            core_enums.ProcedureStatusChoices.ABANDON,
            date_evenement=date(2024, 6, 1),
            created_at=datetime(2024, 6, 2, 12, 0, 0, tzinfo=UTC),
        )
        create_impactful_event(
            procedure,
            core_enums.ProcedureStatusChoices.OPPOSABLE,
            date_evenement=date(2024, 6, 1),
            created_at=datetime(2024, 6, 3, 12, 0, 0, tzinfo=UTC),
        )

        # Both events share the same date_evenement: the most recently created one wins.
        assert (
            procedure.compute_status(self.DATE_PIVOT)
            == core_enums.ProcedureStatusChoices.OPPOSABLE
        )

    def test_same_date_and_created_at_breaks_tie_on_from_sudocuh(self) -> None:
        procedure = ProcedureFactory()
        created_at = datetime(2024, 6, 2, 12, 0, 0, tzinfo=UTC)
        create_impactful_event(
            procedure,
            core_enums.ProcedureStatusChoices.ABANDON,
            date_evenement=date(2024, 6, 1),
            created_at=created_at,
            from_sudocuh=100,
        )
        create_impactful_event(
            procedure,
            core_enums.ProcedureStatusChoices.OPPOSABLE,
            date_evenement=date(2024, 6, 1),
            created_at=created_at,
            from_sudocuh=200,
        )

        # Both events share the same date_evenement and created_at:
        # the one with the highest legacy id (from_sudocuh) wins.
        assert (
            procedure.compute_status(self.DATE_PIVOT)
            == core_enums.ProcedureStatusChoices.OPPOSABLE
        )

    def test_without_impactful_event_returns_en_projet(self) -> None:
        procedure = ProcedureFactory()
        EventFactory(
            procedure=procedure,
            event_type=None,
            date_evenement=date(2024, 6, 1),
        )

        assert (
            procedure.compute_status(self.DATE_PIVOT)
            == core_enums.ProcedureStatusChoices.EN_PROJET
        )


class TestProcedureEnCours:
    @pytest.mark.django_db
    @pytest.mark.parametrize(
        ("event_type", "event_category", "expected_en_cours"),
        [
            ("Prescription", core_models.EventCategory.PRESCRIPTION, True),
            (
                "Publication périmètre",
                core_models.EventCategory.PUBLICATION_PERIMETRE,
                True,
            ),
            ("Délibération d'approbation", core_models.EventCategory.APPROUVE, False),
        ],
    )
    def test_categories_considerees_en_cours(
        self,
        event_type: str,
        event_category: core_models.EventCategory,
        expected_en_cours: bool,
        django_assert_num_queries: DjangoAssertNumQueries,
    ) -> None:
        commune = CommuneFactory()
        procedure = ProcedureFactory(
            doc_type=core_enums.TypeDocument.PLUI, collectivite_porteuse=commune
        )
        event = procedure.event_set.create(type=event_type, date_evenement="2024-12-01")

        assert event.category == event_category
        with django_assert_num_queries(2):
            procedure_with_events = core_models.Procedure.objects.with_events().get(
                id=procedure.id
            )

            assert procedure_with_events.dernier_event_impactant == event
            assert procedure_with_events.statut == event_category
            assert procedure_with_events.is_en_cours == expected_en_cours

    @pytest.mark.django_db
    def test_abrogation_jamais_en_cours(
        self, django_assert_num_queries: DjangoAssertNumQueries
    ) -> None:
        commune = CommuneFactory()

        procedure = ProcedureFactory(
            doc_type=core_enums.TypeDocument.PLUI,
            type="Abrogation",
            collectivite_porteuse=commune,
        )
        event = procedure.event_set.create(
            type="Prescription", date_evenement="2024-12-01"
        )

        with django_assert_num_queries(2):
            procedure_with_events = core_models.Procedure.objects.with_events().get(
                id=procedure.id
            )

            assert procedure_with_events.dernier_event_impactant == event
            assert (
                procedure_with_events.statut == core_models.EventCategory.PRESCRIPTION
            )
            assert not procedure_with_events.is_en_cours

    @pytest.mark.django_db
    def test_pos_jamais_en_cours(
        self, django_assert_num_queries: DjangoAssertNumQueries
    ) -> None:
        commune = CommuneFactory()

        procedure = ProcedureFactory(
            doc_type=core_enums.TypeDocument.POS, collectivite_porteuse=commune
        )
        event = procedure.event_set.create(
            type="Prescription", date_evenement="2024-12-01"
        )

        with django_assert_num_queries(2):
            procedure_with_events = core_models.Procedure.objects.with_events().get(
                id=procedure.id
            )

            assert procedure_with_events.dernier_event_impactant == event
            assert (
                procedure_with_events.statut == core_models.EventCategory.PRESCRIPTION
            )
            assert not procedure_with_events.is_en_cours


@pytest.mark.django_db
class TestProcedureClean:
    def test_principale_avec_status_en_cours(self) -> None:
        procedure = ProcedureFactory(status=core_enums.ProcedureStatusChoices.EN_COURS)

        assert procedure.status == core_enums.ProcedureStatusChoices.EN_COURS

    def test_secondaire_avec_status_null(self) -> None:
        principale = ProcedureFactory()
        procedure = ProcedureFactory(parente=principale, status=None)

        assert procedure.status is None

    def test_main_procedure_without_status_gets_en_projet_default(self) -> None:
        procedure = ProcedureFactory(status=None, parente=None)

        assert procedure.status == core_enums.ProcedureStatusChoices.EN_PROJET

    def test_secondaire_avec_status_en_cours(self) -> None:
        principale = ProcedureFactory()

        with pytest.raises(ValidationError) as error:
            ProcedureFactory(
                parente=principale, status=core_enums.ProcedureStatusChoices.EN_COURS
            )

        assert error.value.messages == [
            'A secondary procedure must not have a "status".'
        ]


@pytest.mark.django_db
class TestProcedureManagers:
    def test_base_manager(self, subtests: pytest.Subtests) -> None:
        ProcedureFactory()
        to_be_removed_fields = [
            "test",
            "testing",
            "doc_type_code",
            "is_sudocuh_scot",
            "previous_opposable_procedures_ids_id",
            "type_code",
            "initial_perimetre",
        ]
        heavy_fields = [
            "current_perimetre",
            "comment_dgd",
            "volet_qualitatif",
        ]

        procedure = core_models.Procedure.objects.earliest("id")
        for item in [*to_be_removed_fields, *heavy_fields]:
            with subtests.test(item, item=item):
                assert item not in procedure.__dict__

    @pytest.mark.django_db
    def test_full_objects_manager(self, subtests: pytest.Subtests) -> None:
        ProcedureFactory()
        to_be_removed_fields = [
            "test",
            "testing",
            "doc_type_code",
            "is_sudocuh_scot",
            "previous_opposable_procedures_ids_id",
            "type_code",
            "initial_perimetre",
        ]
        heavy_fields = [
            "current_perimetre",
            "comment_dgd",
            "volet_qualitatif",
        ]

        procedure = core_models.Procedure.full_objects.earliest("id")
        for item in [*to_be_removed_fields, *heavy_fields]:
            with subtests.test(item, item=item):
                assert item in procedure.__dict__


@pytest.mark.django_db
class TestEventIsImpactful:
    def test_impactful_event(self) -> None:
        event_type = EventTypeFactory(
            name="Impactful type", impact=core_enums.ProcedureStatusChoices.ANNULE
        )
        event = EventFactory(
            event_type=event_type,
            date_evenement=date(2024, 6, 1),
        )

        assert event.is_impactful

    def test_archived_event_is_not_impactful(self) -> None:
        event_type = EventTypeFactory(
            name="Archived impactful type",
            impact=core_enums.ProcedureStatusChoices.ANNULE,
        )
        event = EventFactory(
            event_type=event_type, date_evenement=date(2024, 6, 1), archived=True
        )

        assert not event.is_impactful

    def test_invalid_event_is_not_impactful(self) -> None:
        event_type = EventTypeFactory(
            name="Invalid impactful type",
            impact=core_enums.ProcedureStatusChoices.ANNULE,
        )
        event = EventFactory(
            event_type=event_type, date_evenement=date(2024, 6, 1), is_valid=False
        )

        assert not event.is_impactful

    def test_event_without_date_is_not_impactful(self) -> None:
        event_type = EventTypeFactory(
            name="Undated impactful type",
            impact=core_enums.ProcedureStatusChoices.ANNULE,
        )
        event = EventFactory(event_type=event_type, date_evenement=None)

        assert not event.is_impactful

    def test_event_without_type_is_not_impactful(self) -> None:
        event = EventFactory(event_type=None, date_evenement=date(2024, 6, 1))

        assert not event.is_impactful

    def test_event_with_type_without_impact_is_not_impactful(self) -> None:
        event_type_without_impact = EventTypeFactory(
            name="Type without impact", impact=""
        )
        event = EventFactory(
            event_type=event_type_without_impact, date_evenement=date(2024, 6, 1)
        )

        assert not event.is_impactful


class TestEvent:
    @pytest.mark.parametrize(
        ("doc_type", "type_event", "category"),
        [
            ("PLU", "lol", None),
            (
                "PLU",
                "Délibération de prescription du conseil municipal ou communautaire",
                "prescription",
            ),
            (
                "PLUi",
                "Délibération de prescription du conseil municipal ou communautaire",
                "prescription",
            ),
            ("CC", "Délibération d'approbation", None),
        ],
    )
    def test_event_category(
        self, doc_type: str, type_event: str, category: core_models.EventCategory
    ) -> None:
        procedure = core_models.Procedure(doc_type=doc_type)
        assert (
            core_models.Event(procedure=procedure, type=type_event).category == category
        )

    def test_date_null(self) -> None:
        procedure = core_models.Procedure()
        assert core_models.Event(procedure=procedure).date_evenement is None

    @pytest.mark.django_db
    def test_event_archived(self) -> None:
        profile = ProfileFactory()
        event = EventFactory()
        assert not event.is_archived

        event = EventFactory(archived_at=timezone.now(), archived_by=profile)
        assert event.is_archived

        with pytest.raises(ValidationError) as error:
            event = EventFactory(archived_at=timezone.now(), archived_by=None)
        assert error.value.messages == [
            "Le champ “archived_by” doit être renseigné uniquement si le champ “archived_at” est renseigné"
        ]

        with pytest.raises(ValidationError) as error:
            event = EventFactory(archived_at=None, archived_by=profile)
        assert error.value.messages == [
            "Le champ “archived_by” doit être renseigné uniquement si le champ “archived_at” est renseigné"
        ]

        event = EventFactory()
        event.archive(archived_by=profile)
        assert event.is_archived

    @pytest.mark.django_db
    def test_project_id(
        self,
        django_assert_num_queries: DjangoAssertNumQueries,
        subtests: pytest.Subtests,
    ) -> None:
        factories = [
            ProcedureFactory,
            partial(ProcedureFactory, project=None),
        ]
        for factory in factories:
            with subtests.test(factory, factory=factory):
                old_procedure = ProcedureFactory(with_event=True)
                event = old_procedure.event_set.first()
                new_procedure = factory()
                event.procedure = new_procedure
                with django_assert_num_queries(1):
                    event.save()
                event.refresh_from_db()
                assert event.project_id == new_procedure.project_id

        event = EventFactory(procedure__project=None)
        event.description = "Something new"
        event.save()
        event.refresh_from_db()
        assert not event.project_id


@pytest.mark.django_db
@pytest.mark.xfail(
    reason="The logic to compute the procedure status is in nuxt and have to be implemented in django instead"
)
class TestEventUpdate:
    def test_event_procedure_status_handler__status_update(self) -> None:
        procedure = ProcedureFactory(
            with_event=True,
            with_event__category=core_models.EventCategory.PUBLICATION_PERIMETRE,
            doc_type=core_enums.TypeDocument.CC,
        )
        procedure = core_models.Procedure.objects.with_events().get(pk=procedure.pk)
        procedure.status = procedure.statut
        assert procedure.status == core_models.EventCategory.PUBLICATION_PERIMETRE

        # Adding or updating an event triggers the `event_procedure_status_handler` sql function.
        procedure.event_set.add(*[EventFactory(type="Retrait de l'annulation totale")])
        procedure.refresh_from_db()
        assert procedure.status == "opposable"

    def test_event_procedure_status_handler__commune_procedure_update(self) -> None:
        commune = CommuneFactory()
        procedure = ProcedureFactory(
            with_event=True,
            with_event__category=core_models.EventCategory.PUBLICATION_PERIMETRE,
            doc_type=core_enums.TypeDocument.CC,
            with_perimetre=[commune],
        )
        procedure = core_models.Procedure.objects.with_events().get(pk=procedure.pk)
        procedure.status = procedure.statut
        assert not procedure.perimetre_through.first().opposable

        # Adding or updating an event triggers the `event_procedure_status_handler` sql function.
        event_type = "Retrait de l'annulation totale"
        procedure.event_set.add(*[EventFactory(type=event_type)])
        procedure.refresh_from_db()
        assert procedure.perimetre_through.first().opposable


@pytest.mark.django_db
class TestEventManagers:
    @pytest.mark.django_db
    def test_full_objects_manager(self, subtests: pytest.Subtests) -> None:
        EventFactory()
        to_be_removed_fields = [
            "code",
            "from_sudocuh_procedure_id",
        ]
        heavy_fields = [
            "description",
            "attachements",
        ]
        event = core_models.Event.full_objects.earliest("id")
        for item in [*to_be_removed_fields, *heavy_fields]:
            with subtests.test(item, item=item):
                assert item in event.__dict__

    def test_objects_manager(self, subtests: pytest.Subtests) -> None:
        EventFactory()
        to_be_removed_fields = [
            "code",
            "from_sudocuh_procedure_id",
        ]
        heavy_fields = [
            "description",
            "attachements",
        ]
        event = core_models.Event.objects.earliest("id")
        for item in [*to_be_removed_fields, *heavy_fields]:
            with subtests.test(item, item=item):
                assert item not in event.__dict__


@pytest.mark.django_db
class TestEventQueryset:
    def test_queryset_without_archived(self) -> None:
        event_not_archived = EventFactory()
        EventFactory(archived=True)

        queryset = core_models.Event.objects.all()
        assert queryset.count() == 2

        queryset = core_models.Event.objects.without_archived()
        assert queryset.count() == 1
        event = queryset.first()
        assert event.id == event_not_archived.id

    def test_queryset_filter_impactful_filters_by_date_pivot(self) -> None:
        event_type = EventTypeFactory(
            name="Impactful type pivot", impact=core_enums.ProcedureStatusChoices.ANNULE
        )
        event_past = EventFactory(
            event_type=event_type, date_evenement=date(2024, 6, 1)
        )
        event_future = EventFactory(
            event_type=event_type, date_evenement=date(2026, 12, 1)
        )

        queryset = core_models.Event.objects.filter_impactful()
        assert set(queryset) == {event_past, event_future}

        queryset = core_models.Event.objects.filter_impactful(date(2025, 6, 15))
        assert list(queryset) == [event_past]

    def test_queryset_filter_impactful_excludes_non_impactful_events(
        self, django_assert_num_queries: DjangoAssertNumQueries
    ) -> None:
        event_type_impactful = EventTypeFactory(
            name="Impactful type excluded",
            impact=core_enums.ProcedureStatusChoices.ANNULE,
        )
        event_type_not_impactful = EventTypeFactory(
            name="Type without impact excluded", impact=""
        )
        event = EventFactory(
            event_type=event_type_impactful, date_evenement=date(2024, 6, 1)
        )
        # Archived, invalid, without date, without type or type without impact: excluded.
        EventFactory(
            event_type=event_type_impactful,
            date_evenement=date(2024, 6, 1),
            archived=True,
        )
        EventFactory(
            event_type=event_type_impactful,
            date_evenement=date(2024, 6, 1),
            is_valid=False,
        )
        EventFactory(event_type=event_type_impactful, date_evenement=None)
        EventFactory(event_type=None, date_evenement=date(2024, 6, 1))
        EventFactory(
            event_type=event_type_not_impactful, date_evenement=date(2024, 6, 1)
        )
        with django_assert_num_queries(1):
            assert list(core_models.Event.objects.filter_impactful()) == [event]

    def test_queryset_bulk_unarchive(
        self, django_assert_num_queries: DjangoAssertNumQueries
    ) -> None:
        event_not_archived = EventFactory(archived_at=None, archived_by=None)
        event_archived = EventFactory(archived=True)

        with django_assert_num_queries(1):
            updated = core_models.Event.objects.all().unarchive()
            assert updated == 1

        event_archived.refresh_from_db()
        assert not event_archived.is_archived

        event_not_archived.refresh_from_db()
        assert not event_not_archived.is_archived

    def test_queryset_bulk_archive(
        self, django_assert_num_queries: DjangoAssertNumQueries
    ) -> None:
        archived_by = ProfileFactory()
        archived_at = timezone.now()
        event_not_archived = EventFactory(archived_at=None, archived_by=None)
        event_archived = EventFactory(
            archived_at=archived_at, archived_by=ProfileFactory()
        )

        with pytest.raises(
            ValidationError, match=r"Le champ “archived_by” doit être renseigné"
        ):
            core_models.Event.objects.all().archive(archived_by=None)

        with django_assert_num_queries(1):
            updated = core_models.Event.objects.all().archive(archived_by=archived_by)
            assert updated == 1

        event_archived.refresh_from_db()
        assert event_archived.is_archived
        assert str(event_archived.archived_by.pk) != archived_by.pk
        assert event_archived.archived_at == archived_at

        event_not_archived.refresh_from_db()
        assert event_not_archived.is_archived
        assert str(event_not_archived.archived_by.pk) == archived_by.pk


class TestCommuneProceduresPrincipales:
    @pytest.mark.django_db
    def test_exclut_secondaires(
        self, django_assert_num_queries: DjangoAssertNumQueries
    ) -> None:
        commune = CommuneFactory()

        procedure_secondaire = ProcedureFactory(
            with_parente=True,
            doc_type=core_enums.TypeDocument.PLUI,
            collectivite_porteuse=commune,
            with_perimetre=[commune],
            parente__with_perimetre=[commune],
        )
        procedure_principale = procedure_secondaire.parente

        with django_assert_num_queries(3):
            commune = core_models.Commune.objects.with_procedures_principales().get()
            assert commune.procedures_principales == [procedure_principale]

    @pytest.mark.django_db
    def test_exclut_archivees(
        self, django_assert_num_queries: DjangoAssertNumQueries
    ) -> None:
        commune = CommuneFactory()

        _procedure_supprimee = ProcedureFactory(
            soft_delete=True, collectivite_porteuse=commune, with_perimetre=[commune]
        )

        procedure_doublon = ProcedureFactory(
            with_doublon=True,
            doc_type=core_enums.TypeDocument.PLUI,
            collectivite_porteuse=commune,
            with_perimetre=[commune],
            doublon_cache_de__with_perimetre=[commune],
        )
        procedure_reelle = procedure_doublon.doublon_cache_de

        with django_assert_num_queries(3):
            commune = core_models.Commune.objects.with_procedures_principales().get()
            assert commune.procedures_principales == [procedure_reelle]


@pytest.mark.django_db
class TestCommuneProcedureGetOpposablesForCommune:
    def _create_procedure_on_commune(
        self,
        commune: core_models.Commune,
        *,
        doc_type: core_enums.TypeDocument = core_enums.TypeDocument.PLU,
        **kwargs: dict,
    ) -> core_models.Procedure:
        return ProcedureFactory(
            doc_type=doc_type,
            collectivite_porteuse=commune,
            with_perimetre=[commune],
            **kwargs,
        )

    @staticmethod
    def _perimetre_line(
        procedure: core_models.Procedure,
    ) -> core_models.CommuneProcedure:
        return procedure.perimetre_through.get()

    def test_unique_opposable_procedure_is_returned(self) -> None:
        commune = CommuneFactory()
        procedure = self._create_procedure_on_commune(commune)
        create_impactful_event(
            procedure,
            core_enums.ProcedureStatusChoices.OPPOSABLE,
            date_evenement=date(2025, 1, 1),
        )

        assert core_models.CommuneProcedure.get_opposables_for_commune(commune) == [
            self._perimetre_line(procedure)
        ]

    def test_procedures_without_opposable_event_are_not_returned(self) -> None:
        commune = CommuneFactory()
        procedure_en_cours = self._create_procedure_on_commune(commune)
        create_impactful_event(
            procedure_en_cours,
            core_enums.ProcedureStatusChoices.EN_COURS,
            date_evenement=date(2025, 1, 1),
        )
        self._create_procedure_on_commune(commune)

        assert core_models.CommuneProcedure.get_opposables_for_commune(commune) == []

    def test_most_recent_opposable_event_wins(self) -> None:
        commune = CommuneFactory()
        procedure_avant = self._create_procedure_on_commune(commune)
        create_impactful_event(
            procedure_avant,
            core_enums.ProcedureStatusChoices.OPPOSABLE,
            date_evenement=date(2024, 6, 1),
        )
        procedure_apres = self._create_procedure_on_commune(commune)
        create_impactful_event(
            procedure_apres,
            core_enums.ProcedureStatusChoices.OPPOSABLE,
            date_evenement=date(2025, 1, 1),
        )

        assert core_models.CommuneProcedure.get_opposables_for_commune(commune) == [
            self._perimetre_line(procedure_apres)
        ]

    def test_plan_and_schema_are_independent(self) -> None:
        commune = CommuneFactory()
        scot = self._create_procedure_on_commune(
            commune, doc_type=core_enums.TypeDocument.SCOT
        )
        create_impactful_event(
            scot,
            core_enums.ProcedureStatusChoices.OPPOSABLE,
            date_evenement=date(2025, 6, 1),
        )
        plu = self._create_procedure_on_commune(
            commune, doc_type=core_enums.TypeDocument.PLU
        )
        create_impactful_event(
            plu,
            core_enums.ProcedureStatusChoices.OPPOSABLE,
            date_evenement=date(2024, 1, 1),
        )

        # The SCOT event is more recent, but plans and schemas don't compete:
        # each category keeps its own opposable procedure.
        opposables = core_models.CommuneProcedure.get_opposables_for_commune(commune)
        assert len(opposables) == 2
        assert self._perimetre_line(scot) in opposables
        assert self._perimetre_line(plu) in opposables

    def test_secondary_procedure_is_excluded(self) -> None:
        commune = CommuneFactory()
        procedure_secondaire = self._create_procedure_on_commune(
            commune,
            with_parente=True,
            parente__with_perimetre=[commune],
        )
        create_impactful_event(
            procedure_secondaire,
            core_enums.ProcedureStatusChoices.OPPOSABLE,
            date_evenement=date(2025, 6, 1),
        )
        procedure_principale = procedure_secondaire.parente
        create_impactful_event(
            procedure_principale,
            core_enums.ProcedureStatusChoices.OPPOSABLE,
            date_evenement=date(2024, 6, 1),
        )

        # The secondary procedure is not a candidate, whatever its events.
        opposables = core_models.CommuneProcedure.get_opposables_for_commune(commune)
        assert self._perimetre_line(procedure_secondaire) not in opposables
        assert self._perimetre_line(procedure_principale) in opposables

    def test_archived_procedure_is_excluded(self) -> None:
        commune = CommuneFactory()
        procedure_supprimee = self._create_procedure_on_commune(
            commune, soft_delete=True
        )
        create_impactful_event(
            procedure_supprimee,
            core_enums.ProcedureStatusChoices.OPPOSABLE,
            date_evenement=date(2025, 6, 1),
        )
        procedure_reelle = self._create_procedure_on_commune(commune)
        create_impactful_event(
            procedure_reelle,
            core_enums.ProcedureStatusChoices.OPPOSABLE,
            date_evenement=date(2024, 6, 1),
        )

        opposables = core_models.CommuneProcedure.get_opposables_for_commune(commune)
        assert self._perimetre_line(procedure_supprimee) not in opposables
        assert self._perimetre_line(procedure_reelle) in opposables

    def test_last_impactful_event_not_opposable_excludes_procedure(self) -> None:
        commune = CommuneFactory()
        procedure_annulee = self._create_procedure_on_commune(commune)
        create_impactful_event(
            procedure_annulee,
            core_enums.ProcedureStatusChoices.OPPOSABLE,
            date_evenement=date(2024, 6, 1),
        )
        create_impactful_event(
            procedure_annulee,
            core_enums.ProcedureStatusChoices.ANNULE,
            date_evenement=date(2025, 1, 1),
        )
        procedure_opposable = self._create_procedure_on_commune(commune)
        create_impactful_event(
            procedure_opposable,
            core_enums.ProcedureStatusChoices.OPPOSABLE,
            date_evenement=date(2024, 9, 1),
        )

        # The last impactful event of the cancelled procedure is not opposable,
        # so it is no longer a candidate.
        opposables = core_models.CommuneProcedure.get_opposables_for_commune(commune)
        assert self._perimetre_line(procedure_annulee) not in opposables
        assert self._perimetre_line(procedure_opposable) in opposables

    def test_archived_event_is_ignored(self) -> None:
        commune = CommuneFactory()
        procedure = self._create_procedure_on_commune(commune)
        create_impactful_event(
            procedure,
            core_enums.ProcedureStatusChoices.OPPOSABLE,
            date_evenement=date(2025, 1, 1),
            archived=True,
        )

        assert core_models.CommuneProcedure.get_opposables_for_commune(commune) == []

    def test_invalid_event_is_ignored(self) -> None:
        commune = CommuneFactory()
        procedure = self._create_procedure_on_commune(commune)
        create_impactful_event(
            procedure,
            core_enums.ProcedureStatusChoices.OPPOSABLE,
            date_evenement=date(2025, 1, 1),
            is_valid=False,
        )

        assert core_models.CommuneProcedure.get_opposables_for_commune(commune) == []

    def test_event_without_date_is_ignored(self) -> None:
        commune = CommuneFactory()
        procedure = self._create_procedure_on_commune(commune)
        create_impactful_event(
            procedure,
            core_enums.ProcedureStatusChoices.OPPOSABLE,
            date_evenement=None,
        )

        assert core_models.CommuneProcedure.get_opposables_for_commune(commune) == []

    def test_only_the_given_commune_is_considered(self) -> None:
        commune = CommuneFactory()
        autre_commune = CommuneFactory()
        procedure = self._create_procedure_on_commune(commune)
        create_impactful_event(
            procedure,
            core_enums.ProcedureStatusChoices.OPPOSABLE,
            date_evenement=date(2024, 6, 1),
        )
        autre_procedure = self._create_procedure_on_commune(autre_commune)
        create_impactful_event(
            autre_procedure,
            core_enums.ProcedureStatusChoices.OPPOSABLE,
            date_evenement=date(2025, 6, 1),
        )

        assert core_models.CommuneProcedure.get_opposables_for_commune(commune) == [
            self._perimetre_line(procedure)
        ]
        assert core_models.CommuneProcedure.get_opposables_for_commune(
            autre_commune
        ) == [self._perimetre_line(autre_procedure)]

    def test_same_date_breaks_tie_on_created_at(self) -> None:
        commune = CommuneFactory()
        procedure_avant = self._create_procedure_on_commune(commune)
        create_impactful_event(
            procedure_avant,
            core_enums.ProcedureStatusChoices.OPPOSABLE,
            date_evenement=date(2024, 6, 1),
            created_at=datetime(2024, 6, 2, 12, 0, 0, tzinfo=UTC),
        )
        procedure_apres = self._create_procedure_on_commune(commune)
        create_impactful_event(
            procedure_apres,
            core_enums.ProcedureStatusChoices.OPPOSABLE,
            date_evenement=date(2024, 6, 1),
            created_at=datetime(2024, 6, 3, 12, 0, 0, tzinfo=UTC),
        )

        # Same date_evenement: the most recently created event wins.
        assert core_models.CommuneProcedure.get_opposables_for_commune(commune) == [
            self._perimetre_line(procedure_apres)
        ]

    @freeze_time("2025-06-15")
    def test_future_opposable_event_counts(self) -> None:
        commune = CommuneFactory()
        procedure = self._create_procedure_on_commune(commune)
        create_impactful_event(
            procedure,
            core_enums.ProcedureStatusChoices.OPPOSABLE,
            date_evenement=date(2025, 12, 1),
        )

        # There is no date_pivot: future events count.
        assert core_models.CommuneProcedure.get_opposables_for_commune(commune) == [
            self._perimetre_line(procedure)
        ]


class TestCommunePlanEnCours:
    @pytest.mark.django_db
    def test_plus_recent_en_cours(
        self, django_assert_num_queries: DjangoAssertNumQueries
    ) -> None:
        commune = CommuneFactory()

        procedure_saisie_avant = ProcedureFactory(
            doc_type=core_enums.TypeDocument.PLU,
            collectivite_porteuse=commune,
            with_perimetre=[commune],
        )
        procedure_saisie_avant.event_set.create(
            type="Prescription", date_evenement="2022-12-01"
        )

        procedure_en_cours = ProcedureFactory(
            doc_type=core_enums.TypeDocument.PLUI,
            collectivite_porteuse=commune,
            with_perimetre=[commune],
        )
        procedure_en_cours.event_set.create(
            type="Prescription", date_evenement="2024-12-01"
        )

        procedure_saisie_apres = ProcedureFactory(
            doc_type=core_enums.TypeDocument.PLU,
            collectivite_porteuse=commune,
            with_perimetre=[commune],
        )
        procedure_saisie_apres.event_set.create(
            type="Prescription", date_evenement="2023-12-01"
        )

        with django_assert_num_queries(3):
            commune = core_models.Commune.objects.with_procedures_principales().get()
            assert commune.procedures_principales_en_cours == [
                procedure_en_cours,
                procedure_saisie_apres,
                procedure_saisie_avant,
            ]
            assert commune.plan_en_cours == procedure_en_cours

    @pytest.mark.django_db
    def test_ignore_les_procedures_non_lancees(
        self, django_assert_num_queries: DjangoAssertNumQueries
    ) -> None:
        commune = CommuneFactory()

        procedure_en_cours = ProcedureFactory(
            doc_type=core_enums.TypeDocument.PLUI,
            collectivite_porteuse=commune,
            with_perimetre=[commune],
        )
        procedure_en_cours.event_set.create(
            type="Prescription", date_evenement="2024-12-01"
        )

        _procedure_pas_commencee = ProcedureFactory(
            doc_type=core_enums.TypeDocument.PLU,
            collectivite_porteuse=commune,
            with_perimetre=[commune],
        )

        with django_assert_num_queries(3):
            commune = core_models.Commune.objects.with_procedures_principales().get()
            assert commune.procedures_principales_en_cours == [procedure_en_cours]
            assert commune.plan_en_cours == procedure_en_cours


class TestCommune:
    @pytest.mark.django_db
    def test_is_pas_nouvelle(self) -> None:
        commune = CommuneFactory()

        assert not commune.is_nouvelle

    @pytest.mark.django_db
    def test_is_nouvelle(self) -> None:
        commune_nouvelle = CommuneFactory()
        _commune_deleguee = CommuneFactory(nouvelle=commune_nouvelle)

        assert commune_nouvelle.is_nouvelle

    @pytest.mark.parametrize(
        ("plan_opposable", "plan_en_cours", "collectivite_attendue"),
        [
            (False, True, "200003333"),
            (True, False, "200004444"),
            (True, True, "200003333"),
            (False, False, "13001"),
        ],
    )
    @pytest.mark.django_db
    def test_collectivite_porteuse_selon_situation_plans(
        self, plan_opposable: bool, plan_en_cours: bool, collectivite_attendue: str
    ) -> None:
        commune = CommuneFactory(code_insee_unique="13001")

        if plan_en_cours:
            collectivite = CollectiviteFactory(code_insee_unique="200003333")
            procedure = ProcedureFactory(
                doc_type=core_enums.TypeDocument.PLU,
                collectivite_porteuse=collectivite,
                with_perimetre=[commune],
            )
            procedure.event_set.create(type="Prescription", date_evenement="2022-12-01")

        if plan_opposable:
            collectivite = CollectiviteFactory(code_insee_unique="200004444")
            procedure = ProcedureFactory(
                doc_type=core_enums.TypeDocument.PLU,
                collectivite_porteuse=collectivite,
                with_perimetre=[commune],
            )
            procedure.event_set.create(
                type="Délibération d'approbation", date_evenement="2022-12-01"
            )

        commune = core_models.Commune.objects.with_procedures_principales().first()
        assert commune.collectivite_porteuse.code_insee_unique == collectivite_attendue


class TestCommuneOpposabilite:
    @pytest.mark.django_db
    def test_plus_recente_opposable(
        self, django_assert_num_queries: DjangoAssertNumQueries
    ) -> None:
        commune = CommuneFactory()
        procedure_precedente_saisie_avant = ProcedureFactory(
            doc_type=core_enums.TypeDocument.PLU,
            collectivite_porteuse=commune,
            with_perimetre=[commune],
        )
        procedure_precedente_saisie_avant.event_set.create(
            type="Délibération d'approbation", date_evenement="2022-12-01"
        )

        procedure_opposable = ProcedureFactory(
            doc_type=core_enums.TypeDocument.PLUI,
            collectivite_porteuse=commune,
            with_perimetre=[commune],
        )
        procedure_opposable.event_set.create(
            type="Délibération d'approbation", date_evenement="2024-12-01"
        )

        procedure_precedente_saisie_apres = ProcedureFactory(
            doc_type=core_enums.TypeDocument.PLU,
            collectivite_porteuse=commune,
            with_perimetre=[commune],
        )
        procedure_precedente_saisie_apres.event_set.create(
            type="Délibération d'approbation", date_evenement="2023-12-01"
        )

        with django_assert_num_queries(3):
            commune = core_models.Commune.objects.with_procedures_principales().get()
            assert commune.procedures_principales_approuvees == [
                procedure_opposable,
                procedure_precedente_saisie_apres,
                procedure_precedente_saisie_avant,
            ]

            assert commune.plan_opposable == procedure_opposable
            assert not commune.schema_opposable

            assert commune.is_opposable(procedure_opposable)
            assert not commune.is_opposable(procedure_precedente_saisie_apres)

    @pytest.mark.django_db
    def test_plans_et_schemas_opposable(
        self, django_assert_num_queries: DjangoAssertNumQueries
    ) -> None:
        commune = CommuneFactory()

        plan_opposable = ProcedureFactory(
            doc_type=core_enums.TypeDocument.PLUI,
            collectivite_porteuse=commune,
            with_perimetre=[commune],
        )
        plan_opposable.event_set.create(
            type="Délibération d'approbation", date_evenement="2024-01-02"
        )

        schema_opposable = ProcedureFactory(
            doc_type=core_enums.TypeDocument.SCOT,
            collectivite_porteuse=commune,
            with_perimetre=[commune],
        )
        schema_opposable.event_set.create(
            type="Délibération d'approbation", date_evenement="2024-01-01"
        )

        with django_assert_num_queries(3):
            commune = core_models.Commune.objects.with_procedures_principales().get()
            assert commune.procedures_principales_approuvees == [
                plan_opposable,
                schema_opposable,
            ]

            assert commune.plan_opposable == plan_opposable
            assert commune.schema_opposable == schema_opposable

            assert commune.is_opposable(plan_opposable)
            assert commune.is_opposable(schema_opposable)

    @pytest.mark.django_db
    def test_opposable_sans_prescription(
        self, django_assert_num_queries: DjangoAssertNumQueries
    ) -> None:
        commune = CommuneFactory()

        procedure_opposable = ProcedureFactory(
            collectivite_porteuse=commune,
            doc_type=core_enums.TypeDocument.PLUI,
            with_perimetre=[commune],
        )
        procedure_opposable.event_set.create(
            type="Délibération d'approbation", date_evenement="2024-12-01"
        )

        with django_assert_num_queries(3):
            commune = core_models.Commune.objects.with_procedures_principales().get()
            assert commune.procedures_principales_approuvees == [procedure_opposable]

            assert commune.plan_opposable == procedure_opposable
            assert not commune.schema_opposable

            assert commune.is_opposable(procedure_opposable)

    @pytest.mark.django_db
    def test_aucune_opposable(
        self, django_assert_num_queries: DjangoAssertNumQueries
    ) -> None:
        commune = CommuneFactory()

        procedure_en_cours = ProcedureFactory(
            collectivite_porteuse=commune,
            doc_type=core_enums.TypeDocument.PLUI,
            with_perimetre=[commune],
        )
        procedure_en_cours.event_set.create(
            type="Délibération de prescription du conseil municipal ou communautaire",
            date_evenement="2024-12-01",
        )

        with django_assert_num_queries(3):
            commune = core_models.Commune.objects.with_procedures_principales().get()
            assert commune.procedures_principales_approuvees == []

            assert not commune.plan_opposable
            assert not commune.schema_opposable

            assert not commune.is_opposable(procedure_en_cours)

    @pytest.mark.django_db
    def test_abrogation_non_opposable(
        self, django_assert_num_queries: DjangoAssertNumQueries
    ) -> None:
        commune = CommuneFactory()

        procedure_approuvee = ProcedureFactory(
            collectivite_porteuse=commune,
            doc_type=core_enums.TypeDocument.PLUI,
            type="Abrogation",
            with_perimetre=[commune],
        )
        procedure_approuvee.event_set.create(
            type="Délibération d'approbation", date_evenement="2024-12-01"
        )

        with django_assert_num_queries(3):
            commune = core_models.Commune.objects.with_procedures_principales().get()
            assert commune.procedures_principales_approuvees == []

            assert not commune.plan_opposable
            assert not commune.schema_opposable

            assert not commune.is_opposable(procedure_approuvee)

    @pytest.mark.django_db
    def test_ignore_procedures_secondaires(
        self, django_assert_num_queries: DjangoAssertNumQueries
    ) -> None:
        commune = CommuneFactory()

        procedure_secondaire = ProcedureFactory(
            with_parente=True,
            doc_type=core_enums.TypeDocument.PLUI,
            collectivite_porteuse=commune,
            with_perimetre=[commune],
            parente__with_perimetre=[commune],
        )
        procedure_principale = procedure_secondaire.parente
        procedure_secondaire.event_set.create(
            type="Délibération d'approbation", date_evenement="2024-12-01"
        )

        with django_assert_num_queries(3):
            commune = core_models.Commune.objects.with_procedures_principales().get()
            assert commune.procedures_principales_approuvees == []

            assert not commune.plan_opposable
            assert not commune.schema_opposable

            assert not commune.is_opposable(procedure_principale)
            assert not commune.is_opposable(procedure_secondaire)

    @pytest.mark.django_db
    def test_ignore_procedures_archivees(
        self, django_assert_num_queries: DjangoAssertNumQueries
    ) -> None:
        commune = CommuneFactory()

        procedure_supprimee = ProcedureFactory(
            collectivite_porteuse=commune, soft_delete=True, with_perimetre=[commune]
        )
        procedure_supprimee.event_set.create(
            type="Délibération d'approbation", date_evenement="2024-12-01"
        )

        procedure_doublon = ProcedureFactory(
            with_doublon=True,
            collectivite_porteuse=commune,
            with_perimetre=[commune],
            doublon_cache_de__with_perimetre=[commune],
        )
        procedure_reelle = procedure_doublon.doublon_cache_de
        procedure_doublon.event_set.create(
            type="Délibération d'approbation", date_evenement="2024-12-01"
        )

        with django_assert_num_queries(3):
            commune = core_models.Commune.objects.with_procedures_principales().get()
            assert commune.procedures_principales_approuvees == []

            assert not commune.plan_opposable
            assert not commune.schema_opposable

            assert not commune.is_opposable(procedure_reelle)
            assert not commune.is_opposable(procedure_supprimee)
            assert not commune.is_opposable(procedure_doublon)

    @pytest.mark.django_db
    def test_ignore_event_apres(
        self, django_assert_num_queries: DjangoAssertNumQueries
    ) -> None:
        commune = CommuneFactory()

        procedure_opposable_fevrier = ProcedureFactory(
            collectivite_porteuse=commune,
            doc_type=core_enums.TypeDocument.PLUI,
            with_perimetre=[commune],
        )
        procedure_opposable_fevrier.event_set.create(
            type="Délibération d'approbation", date_evenement="2024-02-02"
        )

        procedure_opposable_janvier = ProcedureFactory(
            collectivite_porteuse=commune,
            doc_type=core_enums.TypeDocument.PLU,
            with_perimetre=[commune],
        )
        procedure_opposable_janvier.event_set.create(
            type="Délibération d'approbation", date_evenement="2024-01-01"
        )

        with django_assert_num_queries(2):
            procedures = core_models.Procedure.objects.with_events()

            assert all(
                procedure.statut == core_models.EventCategory.APPROUVE
                for procedure in procedures
            )

        with django_assert_num_queries(3):
            commune = core_models.Commune.objects.with_procedures_principales(
                avant=date(2024, 2, 1)
            ).get()

        with django_assert_num_queries(0):
            assert set(commune.procedures_principales) == {
                procedure_opposable_fevrier,
                procedure_opposable_janvier,
            }
            assert commune.procedures_principales_approuvees == [
                procedure_opposable_janvier,
            ]
            assert commune.plan_opposable == procedure_opposable_janvier
            assert not commune.schema_opposable

            assert commune.is_opposable(procedure_opposable_janvier)
            assert not commune.is_opposable(procedure_opposable_fevrier)


class TestCommuneCodeEtat:
    @pytest.mark.django_db
    def test_commune_sans_plans(self) -> None:
        CommuneFactory()

        commune = core_models.Commune.objects.with_procedures_principales().first()
        assert commune.code_etat_simplifie == "99"
        assert commune.code_etat_complet == "9999"

    @pytest.mark.django_db
    @pytest.mark.parametrize(
        ("create_collectivite", "perimetre_count", "expected_code"),
        [
            (CommuneFactory, 1, core_models.CodeCompetencePerimetre.COMPETENCE_COMMUNE),
            (
                CollectiviteFactory,
                1,
                core_models.CodeCompetencePerimetre.COMPETENCE_EPCI_PROCEDURE_COMMUNALE,
            ),
            (
                CollectiviteFactory,
                2,
                core_models.CodeCompetencePerimetre.COMPETENCE_EPCI_PERIMETRE_INFERIEUR_EPCI,
            ),
            (
                CollectiviteFactory,
                3,
                core_models.CodeCompetencePerimetre.COMPETENCE_EPCI_PERIMETRE_EPCI,
            ),
        ],
    )
    def test_competence_intercommunalite_code(
        self,
        create_collectivite: Callable[[], core_models.Collectivite],
        perimetre_count: int,
        expected_code: core_models.CodeCompetencePerimetre,
    ) -> None:
        collectivite_porteuse = create_collectivite()

        if not collectivite_porteuse.is_commune:
            for _ in range(3):
                commune = CommuneFactory()
                commune.adhesions.add(collectivite_porteuse)

        core_models.MaterializedViewFlatMembership.refresh()

        procedure = ProcedureFactory(
            collectivite_porteuse=collectivite_porteuse,
            with_perimetre=[CommuneFactory() for _ in range(perimetre_count)],
        )

        procedure = core_models.Procedure.objects.get(id=procedure.id)
        assert (
            procedure.competence_intercommunalite_code(collectivite_porteuse)
            == expected_code
        )


class TestEnums:
    def test_type_collectivite_epci(self) -> None:
        assert core_enums.TypeCollectivite.CC in core_enums.TypeCollectivite.epci()
        assert core_enums.TypeCollectivite.COM not in core_enums.TypeCollectivite.epci()


class TestEventType:
    @pytest.mark.django_db
    def test_order(self) -> None:
        cc1 = EventTypeFactory(
            document_type=core_models.EventType.DocumentType.CC, name="CC1"
        )

        assert cc1.order == 1

        cc2 = EventTypeFactory(
            document_type=core_models.EventType.DocumentType.CC, name="CC2"
        )
        assert cc2.order == 2

        plu1 = EventTypeFactory(document_type=core_models.EventType.DocumentType.PLU)
        assert plu1.order == 1
