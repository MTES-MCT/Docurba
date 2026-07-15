# ruff: noqa: FBT001, N803
from collections.abc import Callable
from contextlib import nullcontext as does_not_raise
from datetime import date, timedelta
from functools import partial

import pytest
from django.core.exceptions import PermissionDenied, ValidationError
from django.utils import timezone
from pytest_django import DjangoAssertNumQueries

from docurba.core.enums import TypeCollectivite
from docurba.core.models import (
    EVENT_CATEGORY_BY_DOC_TYPE,
    Adhesion,
    CodeCompetencePerimetre,
    Collectivite,
    Commune,
    Event,
    EventCategory,
    EventType,
    MaterializedViewFlatMembership,
    Procedure,
    Topic,
    TypeDocument,
)
from tests.core.factories import (
    CollectiviteFactory,
    CommuneFactory,
    DepartementFactory,
    EventFactory,
    EventTypeFactory,
    ProcedureFactory,
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
        assert Adhesion.objects.count() == 4
        assert MaterializedViewFlatMembership.objects.count() == 6

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
            assert MaterializedViewFlatMembership.objects.filter(
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

        MaterializedViewFlatMembership().refresh()

        assert Adhesion.objects.count() == 4
        assert MaterializedViewFlatMembership.objects.count() == 5

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
            MaterializedViewFlatMembership.objects.create(
                member_id=CollectiviteFactory().pk, group_id=CollectiviteFactory().pk
            )

        with pytest.raises(PermissionDenied):
            MaterializedViewFlatMembership.objects.bulk_create()

        memberships = MaterializedViewFlatMembership.objects.all()
        for membership in memberships:
            membership.group_id = CollectiviteFactory().pk

        with pytest.raises(PermissionDenied):
            memberships.bulk_update(memberships, fields=["group_id"])

        with pytest.raises(PermissionDenied):
            memberships.delete()


class TestProcedureQuerySet:
    @pytest.mark.django_db
    def test_with_concatenated_topics_as_string(
        self, django_assert_num_queries: DjangoAssertNumQueries
    ) -> None:
        topics = Topic.objects.filter(name__in=["zan", "forest_fire"])
        procedure = ProcedureFactory()
        procedure.topics.add(*topics)
        with django_assert_num_queries(1):
            procedure = Procedure.objects.with_concatenated_topics_as_string().get(
                pk=procedure.pk
            )
        assert hasattr(procedure, "concatenated_topics_as_string")
        assert procedure.concatenated_topics_as_string == "Feu de forêt,Trajectoire ZAN"


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
        MaterializedViewFlatMembership.refresh()

        procedure_sectorielle = ProcedureFactory(
            collectivite_porteuse=collectivite,
            doc_type=TypeDocument.PLU,
            with_perimetre=[commune_enfant],
        )
        with django_assert_num_queries(1):
            procedure_sectorielle_with_counts = Procedure.objects.get(
                id=procedure_sectorielle.id
            )
            assert procedure_sectorielle_with_counts.perimetre__count == 1
            assert procedure_sectorielle_with_counts.communes_adherentes__count == 3
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

        MaterializedViewFlatMembership.refresh()

        procedure_non_sectorielle = ProcedureFactory(
            collectivite_porteuse=collectivite,
            doc_type=TypeDocument.PLU,
            with_perimetre=[
                commune_enfant,
                commune_grand_enfant,
                commune_grand_grand_enfant,
            ],
        )

        with django_assert_num_queries(1):
            procedure_non_sectorielle_with_counts = Procedure.objects.get(
                id=procedure_non_sectorielle.id
            )
            assert procedure_non_sectorielle_with_counts.perimetre__count == 3
            assert procedure_non_sectorielle_with_counts.communes_adherentes__count == 3
            assert not procedure_non_sectorielle_with_counts.is_sectoriel_consolide

    @pytest.mark.django_db
    def test_exclut_commune_deleguee_du_perimetre_count(
        self, django_assert_num_queries: DjangoAssertNumQueries
    ) -> None:
        collectivite = CollectiviteFactory()

        commune_enfant = CommuneFactory()
        commune_enfant.adhesions.add(collectivite)

        commune_deleguee = CommuneFactory(nouvelle=commune_enfant)

        MaterializedViewFlatMembership.refresh()

        procedure = ProcedureFactory(
            collectivite_porteuse=collectivite,
            doc_type=TypeDocument.PLU,
            with_perimetre=[commune_enfant, commune_deleguee],
        )

        with django_assert_num_queries(1):
            procedure_with_counts = Procedure.objects.get(id=procedure.id)
            assert procedure_with_counts.perimetre__count == 1
            assert procedure_with_counts.communes_adherentes__count == 1

    @pytest.mark.django_db
    def test_retourne_zero_quand_pas_de_commune(
        self, django_assert_num_queries: DjangoAssertNumQueries
    ) -> None:
        collectivite = CollectiviteFactory()

        MaterializedViewFlatMembership.refresh()

        procedure = collectivite.procedure_set.create(doc_type=TypeDocument.PLU)

        with django_assert_num_queries(1):
            procedure_with_counts = Procedure.objects.get(id=procedure.id)
            assert procedure_with_counts.perimetre__count == 0
            assert procedure_with_counts.communes_adherentes__count == 0


def test_tous_document_types_ont_event_category() -> None:
    assert list(TypeDocument) == list(EVENT_CATEGORY_BY_DOC_TYPE.keys())


@pytest.mark.django_db
class TestCollectivite:
    def test_code_insee_integrity(self) -> None:
        departement = DepartementFactory(code_insee="30")
        collectivite = CollectiviteFactory.build(
            type=TypeCollectivite.CC, code_insee="12345", departement=departement
        )
        with pytest.raises(
            ValidationError, match=r"Seules les communes peuvent avoir un code INSEE."
        ):
            collectivite.save()

        collectivite = CollectiviteFactory.build(
            type=TypeCollectivite.COM, code_insee="12345", departement=departement
        )
        with does_not_raise():
            collectivite.save()


class TestCollectivitePortantScot:
    @pytest.mark.django_db
    def test_retourne_que_collectivite_avec_scot(
        self, django_assert_num_queries: DjangoAssertNumQueries
    ) -> None:
        collectivite_avec_scot = CollectiviteFactory()
        scot_en_cours = collectivite_avec_scot.procedure_set.create(
            doc_type=TypeDocument.SCOT
        )
        scot_en_cours.event_set.create(
            type="Délibération de l'établissement public qui prescrit",
            date_evenement="2024-12-01",
        )

        _collectivite_sans_procedure = CollectiviteFactory()

        collectivite_avec_plan = CollectiviteFactory()
        collectivite_avec_plan.procedure_set.create(doc_type=TypeDocument.PLU)

        with django_assert_num_queries(4):
            collectivites = list(Collectivite.objects.portant_scot())
            assert collectivites == [collectivite_avec_scot]

            assert collectivites[0].scots_pour_csv == [(None, scot_en_cours)]

    @pytest.mark.django_db
    def test_ignore_procedures_archivees(
        self, django_assert_num_queries: DjangoAssertNumQueries
    ) -> None:
        collectivite = CollectiviteFactory()
        scot_supprime = collectivite.procedure_set.create(
            doc_type=TypeDocument.SCOT, soft_delete=True
        )

        _scot_doublon = collectivite.procedure_set.create(
            doc_type=TypeDocument.SCOT, doublon_cache_de=scot_supprime
        )

        with django_assert_num_queries(1):
            assert list(Collectivite.objects.portant_scot()) == []

    @pytest.mark.django_db
    def test_ignore_procedures_secondaires(
        self, django_assert_num_queries: DjangoAssertNumQueries
    ) -> None:
        collectivite = CollectiviteFactory()
        parent_procedure = collectivite.procedure_set.create(
            doc_type=TypeDocument.SCOT, soft_delete=True
        )
        collectivite.procedure_set.create(
            doc_type=TypeDocument.SCOT, parente=parent_procedure, archived=False
        )

        with django_assert_num_queries(1):
            assert list(Collectivite.objects.portant_scot()) == []

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
                doc_type=TypeDocument.SCOT,
                with_perimetre=[commune],
            )
            scot_opposable.event_set.create(
                type="Délibération d'approbation", date_evenement=date_string
            )
            scots_opposables.append(scot_opposable)

        with django_assert_num_queries(6):
            collectivites = list(Collectivite.objects.portant_scot())
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
            scot_en_cours = collectivite_avec_scot.procedure_set.create(
                doc_type=TypeDocument.SCOT
            )
            scot_en_cours.event_set.create(
                type="Délibération de l'établissement public qui prescrit",
                date_evenement="2024-12-01",
            )
            scots_en_cours.append(scot_en_cours)

        with django_assert_num_queries(4):
            collectivites = list(Collectivite.objects.portant_scot())
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
            doc_type=TypeDocument.SCOT,
            type="A",
            with_perimetre=[commune_a],
        )
        scot_opposable_a.event_set.create(
            type="Délibération d'approbation", date_evenement="2024-01-01"
        )

        scot_precedent_a = ProcedureFactory(
            collectivite_porteuse=collectivite,
            doc_type=TypeDocument.SCOT,
            type="B",
            with_perimetre=[commune_a],
        )
        scot_precedent_a.event_set.create(
            type="Délibération d'approbation", date_evenement="1999-01-01"
        )

        scot_opposable_a_et_b = ProcedureFactory(
            collectivite_porteuse=collectivite,
            doc_type=TypeDocument.SCOT,
            type="C",
            with_perimetre=[commune_a, commune_b],
        )
        scot_opposable_a_et_b.event_set.create(
            type="Délibération d'approbation", date_evenement="2023-01-01"
        )

        with django_assert_num_queries(6):
            collectivites = list(Collectivite.objects.portant_scot())
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

        scot_en_cours = collectivite_avec_scot.procedure_set.create(
            doc_type=TypeDocument.SCOT
        )
        scot_en_cours.event_set.create(
            type="Délibération de l'établissement public qui prescrit",
            date_evenement="2024-12-01",
        )

        scots_opposables = []
        for commune in [commune_a, commune_b]:
            scot_opposable = ProcedureFactory(
                collectivite_porteuse=collectivite_avec_scot,
                doc_type=TypeDocument.SCOT,
                with_perimetre=[commune],
            )
            scot_opposable.event_set.create(
                type="Délibération d'approbation", date_evenement="2024-12-01"
            )
            scots_opposables.append(scot_opposable)

        with django_assert_num_queries(6):
            collectivites = list(Collectivite.objects.portant_scot())
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
            doc_type=TypeDocument.SCOT,
            with_perimetre=[commune],
        )
        scot_opposable.event_set.create(
            type="Délibération d'approbation", date_evenement="2025-12-11"
        )
        scot_opposable.event_set.create(
            type="Fin d'échéance", date_evenement="2025-12-14"
        )

        with django_assert_num_queries(6):
            collectivites = list(Collectivite.objects.portant_scot(avant=avant))
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
            doc_type=TypeDocument.SCOT,
            with_perimetre=[commune_a, commune_b],
        )
        scot_en_cours.event_set.create(type="Prescription", date_evenement="2024-12-01")

        with django_assert_num_queries(6):
            collectivites = list(Collectivite.objects.portant_scot())
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
            doc_type=TypeDocument.SCOT,
            with_perimetre=[commune_a, commune_b],
        )
        scot_en_cours.event_set.create(type="Prescription", date_evenement="2024-12-01")

        with django_assert_num_queries(6):
            collectivites = list(Collectivite.objects.portant_scot())
            assert collectivites == [collectivite_avec_scot]

            assert collectivites[0].scots[0].is_interdepartemental


class TestProcedure:
    def test_is_schema(self) -> None:
        assert not Procedure(doc_type=TypeDocument.CC).is_schema
        assert not Procedure(doc_type=TypeDocument.PLU).is_schema
        assert not Procedure(doc_type=TypeDocument.PLUI).is_schema
        assert not Procedure(doc_type=TypeDocument.PLUIM).is_schema
        assert not Procedure(doc_type=TypeDocument.PLUIH).is_schema
        assert not Procedure(doc_type=TypeDocument.PLUIHM).is_schema

        assert Procedure(doc_type=TypeDocument.SCOT).is_schema
        assert Procedure(doc_type=TypeDocument.SD).is_schema

    @pytest.mark.django_db
    def test_liable_a_collectivite_porteuse_inexistante(self) -> None:
        """Tant que l'on ne gère pas bien les communes des anciens COG."""
        Procedure.objects.create(collectivite_porteuse_id=12)

        assert Procedure.objects.count() == 1

    @pytest.mark.django_db
    def test_liable_a_commune_inexistante(self) -> None:
        """Tant que l'on ne gère pas bien les communes des anciens COG."""
        procedure = Procedure.objects.create()
        procedure.perimetre.through.objects.create(
            collectivite_code=12,
            collectivite_type="COM",
            procedure=procedure,
        )

        assert procedure.perimetre.through.objects.count() == 1


class TestProcedureDates:
    @pytest.mark.django_db
    def test_none_quand_inexistantes(
        self, django_assert_num_queries: DjangoAssertNumQueries
    ) -> None:
        commune = CommuneFactory()
        Procedure.objects.create(
            doc_type=TypeDocument.SCOT, collectivite_porteuse=commune
        )

        with django_assert_num_queries(2):
            procedure = Procedure.objects.with_events().first()

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
        procedure = Procedure.objects.create(
            doc_type=TypeDocument.SCOT,
            collectivite_porteuse=commune,
        )
        for date_string in ("2022-12-01", "2024-12-01", "2023-12-01"):
            procedure.event_set.create(type=event_type, date_evenement=date_string)

        with django_assert_num_queries(2):
            procedure_with_events = Procedure.objects.with_events().first()

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
        procedure = Procedure.objects.create(
            doc_type=TypeDocument.SCOT, collectivite_porteuse=commune
        )
        procedure.event_set.create(
            type=event_type, date_evenement="2024-12-01", is_valid=False
        )

        with django_assert_num_queries(2):
            procedure_with_events = Procedure.objects.with_events().first()

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
        procedure = Procedure.objects.create(
            doc_type=TypeDocument.SCOT, collectivite_porteuse=commune
        )
        procedure.event_set.create(type=event_type, date_evenement="2022-12-01")
        procedure.event_set.create(type="Fin d'échéance", date_evenement="2022-12-01")

        with django_assert_num_queries(2):
            procedure_with_events = Procedure.objects.with_events(
                avant="2022-11-29"
            ).first()
            assert getattr(procedure_with_events, date_attribute) is None
            assert procedure_with_events.date_fin_echeance == date(2022, 12, 1)

        with django_assert_num_queries(2):
            procedure_with_events = Procedure.objects.with_events(
                avant="2022-11-30"
            ).first()
            assert getattr(procedure_with_events, date_attribute) is None
            assert procedure_with_events.date_fin_echeance == date(2022, 12, 1)

        with django_assert_num_queries(2):
            procedure_with_events = Procedure.objects.with_events(
                avant="2022-12-01"
            ).first()
            assert getattr(procedure_with_events, date_attribute) == date(2022, 12, 1)
            assert procedure_with_events.date_fin_echeance == date(2022, 12, 1)


class TestProcedureTypeDocument:
    def test_non_plu_like(self) -> None:
        assert Procedure(doc_type=TypeDocument.CC).type_document == TypeDocument.CC
        assert Procedure(doc_type=TypeDocument.SCOT).type_document == TypeDocument.SCOT
        assert Procedure(doc_type=TypeDocument.SD).type_document == TypeDocument.SD

    @pytest.mark.django_db
    @pytest.mark.parametrize(
        "doc_type",
        [
            (TypeDocument.PLU),
            (TypeDocument.PLUI),
            (TypeDocument.PLUIH),
            (TypeDocument.PLUIM),
            (TypeDocument.PLUIHM),
        ],
    )
    def test_plu(
        self, doc_type: TypeDocument, django_assert_num_queries: DjangoAssertNumQueries
    ) -> None:
        commune = CommuneFactory()
        procedure = ProcedureFactory(
            doc_type=doc_type, collectivite_porteuse=commune, with_perimetre=[commune]
        )

        with django_assert_num_queries(1):
            procedure = Procedure.objects.get(id=procedure.id)
            assert procedure.type_document == TypeDocument.PLU
            assert not procedure.vaut_PLH_consolide
            assert not procedure.vaut_PDM_consolide

    @pytest.mark.django_db
    @pytest.mark.parametrize(
        "doc_type",
        [
            (TypeDocument.PLU),
            (TypeDocument.PLUI),
        ],
    )
    def test_plui(
        self, doc_type: TypeDocument, django_assert_num_queries: DjangoAssertNumQueries
    ) -> None:
        commune_a = CommuneFactory()
        commune_b = CommuneFactory()

        procedure = ProcedureFactory(
            collectivite_porteuse=commune_a,
            doc_type=doc_type,
            with_perimetre=[commune_a, commune_b],
        )

        with django_assert_num_queries(1):
            procedure = Procedure.objects.get(id=procedure.id)
            assert procedure.type_document == TypeDocument.PLUI
            assert not procedure.vaut_PLH_consolide
            assert not procedure.vaut_PDM_consolide

    @pytest.mark.django_db
    @pytest.mark.parametrize(
        ("doc_type", "vaut_PLH"),
        [
            (TypeDocument.PLU, True),
            (TypeDocument.PLUI, True),
            (TypeDocument.PLUIH, False),
            (TypeDocument.PLUIH, True),
        ],
    )
    def test_pluih(
        self,
        doc_type: TypeDocument,
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
            procedure = Procedure.objects.get(id=procedure.id)
            assert procedure.type_document == TypeDocument.PLUIH
            assert procedure.vaut_PLH_consolide
            assert not procedure.vaut_PDM_consolide

    @pytest.mark.django_db
    @pytest.mark.parametrize(
        ("doc_type", "vaut_PDM"),
        [
            (TypeDocument.PLU, True),
            (TypeDocument.PLUI, True),
            (TypeDocument.PLUIM, False),
            (TypeDocument.PLUIM, True),
        ],
    )
    def test_pluim(
        self,
        doc_type: TypeDocument,
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
            procedure = Procedure.objects.get(id=procedure.id)
            assert procedure.type_document == TypeDocument.PLUIM
            assert not procedure.vaut_PLH_consolide
            assert procedure.vaut_PDM_consolide

    @pytest.mark.django_db
    @pytest.mark.parametrize(
        ("doc_type", "vaut_PLH", "vaut_PDM"),
        [
            (TypeDocument.PLU, True, True),
            (TypeDocument.PLUI, True, True),
            (TypeDocument.PLUIH, True, True),
            (TypeDocument.PLUIM, True, True),
            (TypeDocument.PLUIHM, False, False),
            (TypeDocument.PLUIHM, False, True),
            (TypeDocument.PLUIHM, True, False),
            (TypeDocument.PLUIHM, True, True),
        ],
    )
    def test_pluihm(
        self,
        doc_type: TypeDocument,
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
            procedure = Procedure.objects.get(id=procedure.id)
            assert procedure.type_document == TypeDocument.PLUIHM
            assert procedure.vaut_PLH_consolide
            assert procedure.vaut_PDM_consolide

    @pytest.mark.django_db
    @pytest.mark.parametrize(
        ("src_doc_type", "expected_doc_type"),
        [
            (TypeDocument.PLU, TypeDocument.PLUIS),
            (TypeDocument.PLUI, TypeDocument.PLUIS),
            (TypeDocument.PLUIH, TypeDocument.PLUISH),
            (TypeDocument.PLUIM, TypeDocument.PLUISM),
            (TypeDocument.PLUIHM, TypeDocument.PLUISHM),
        ],
    )
    def test_type_document_pour_procedure_sectorielle(
        self,
        src_doc_type: TypeDocument,
        expected_doc_type: TypeDocument,
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
        procedure = Procedure.objects.get(id=procedure.id)
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
        procedure = Procedure.objects.create(
            doc_type=TypeDocument.PLUI, collectivite_porteuse=commune
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

        procedure_with_events = Procedure.objects.with_events().get(id=procedure.id)
        assert procedure_with_events.delai_d_approbation is None

    @pytest.mark.django_db
    def test_delai_d_approbation_calcule(self) -> None:
        commune = CommuneFactory()
        procedure = Procedure.objects.create(
            doc_type=TypeDocument.PLUI, collectivite_porteuse=commune
        )
        procedure.event_set.create(type="Prescription", date_evenement="2024-01-01")
        procedure.event_set.create(
            type="Délibération d'approbation", date_evenement="2024-02-01"
        )

        procedure_with_events = Procedure.objects.with_events().get(id=procedure.id)
        assert procedure_with_events.delai_d_approbation == 31


class TestProcedureSort:
    @pytest.mark.django_db
    def test_approuvee_plus_recemment(self) -> None:
        commune = CommuneFactory()
        procedure_recente = Procedure.objects.create(
            doc_type=TypeDocument.PLUI, collectivite_porteuse=commune
        )
        procedure_recente.event_set.create(
            type="Délibération d'approbation", date_evenement="2024-12-01"
        )

        procedure_vieille = Procedure.objects.create(
            doc_type=TypeDocument.PLUI, collectivite_porteuse=commune
        )
        procedure_vieille.event_set.create(
            type="Délibération d'approbation", date_evenement="2023-12-01"
        )

        procedure_recent_with_events = Procedure.objects.with_events().get(
            id=procedure_recente.id
        )
        procedure_vieille_with_events = Procedure.objects.with_events().get(
            id=procedure_vieille.id
        )
        assert procedure_vieille_with_events < procedure_recent_with_events

    @pytest.mark.django_db
    def test_prescrite_plus_recemment(self) -> None:
        commune = CommuneFactory()
        procedure_recente = Procedure.objects.create(
            doc_type=TypeDocument.PLUI, collectivite_porteuse=commune
        )
        procedure_recente.event_set.create(
            type="Prescription", date_evenement="2024-12-01"
        )

        procedure_vieille = Procedure.objects.create(
            doc_type=TypeDocument.PLUI, collectivite_porteuse=commune
        )
        procedure_vieille.event_set.create(
            type="Prescription", date_evenement="2023-12-01"
        )

        procedure_recent_with_events = Procedure.objects.with_events().get(
            id=procedure_recente.id
        )
        procedure_vieille_with_events = Procedure.objects.with_events().get(
            id=procedure_vieille.id
        )
        assert procedure_vieille_with_events < procedure_recent_with_events

    @pytest.mark.django_db
    def test_date_approbation_priorite_quand_date_entremelees(self) -> None:
        commune = CommuneFactory()
        procedure_recente = Procedure.objects.create(
            doc_type=TypeDocument.PLUI, collectivite_porteuse=commune
        )
        procedure_recente.event_set.create(
            type="Prescription", date_evenement="1999-12-01"
        )
        procedure_recente.event_set.create(
            type="Délibération d'approbation", date_evenement="2024-12-01"
        )

        procedure_vieille = Procedure.objects.create(
            doc_type=TypeDocument.PLUI, collectivite_porteuse=commune
        )
        procedure_vieille.event_set.create(
            type="Prescription", date_evenement="2023-12-01"
        )
        procedure_vieille.event_set.create(
            type="Délibération d'approbation", date_evenement="2023-12-02"
        )

        procedure_recent_with_events = Procedure.objects.with_events().get(
            id=procedure_recente.id
        )
        procedure_vieille_with_events = Procedure.objects.with_events().get(
            id=procedure_vieille.id
        )
        assert procedure_vieille_with_events < procedure_recent_with_events

    @pytest.mark.xfail(
        reason="created_at utilise le timestamp de la transaction, pas du statement"
    )
    @pytest.mark.django_db
    def test_sans_prescription_utilise_date_creation(self) -> None:
        commune = CommuneFactory()
        procedure_vieille = Procedure.objects.create(
            doc_type=TypeDocument.PLUI, collectivite_porteuse=commune
        )
        procedure_recente = Procedure.objects.create(
            doc_type=TypeDocument.PLUI, collectivite_porteuse=commune
        )

        procedure_recent_with_events = Procedure.objects.with_events().get(
            id=procedure_recente.id
        )
        procedure_vieille_with_events = Procedure.objects.with_events().get(
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
        procedure = Procedure.objects.create(
            doc_type=TypeDocument.PLUI, collectivite_porteuse=commune
        )
        event = procedure.event_set.create(
            type="Délibération d'approbation", date_evenement="2024-12-01"
        )

        assert event.category == EventCategory.APPROUVE
        with django_assert_num_queries(2):
            procedure_with_events = Procedure.objects.with_events().get(id=procedure.id)

            assert procedure_with_events.dernier_event_impactant == event
            assert procedure_with_events.statut == EventCategory.APPROUVE

    @pytest.mark.django_db
    @pytest.mark.parametrize("is_approuve", [True, False])
    def test_sd_est_toujours_caduc(
        self, is_approuve: bool, django_assert_num_queries: DjangoAssertNumQueries
    ) -> None:
        """https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000028809968/2015-08-09."""
        commune = CommuneFactory()
        procedure = Procedure.objects.create(
            doc_type=TypeDocument.SD, collectivite_porteuse=commune
        )
        if is_approuve:
            event = procedure.event_set.create(
                type="Délibération d'approbation", date_evenement="2004-12-01"
            )
            assert event.category == EventCategory.APPROUVE

        with django_assert_num_queries(2):
            procedure_with_events = Procedure.objects.with_events().get(id=procedure.id)

            assert procedure_with_events.statut == EventCategory.CADUC

    @pytest.mark.django_db
    @pytest.mark.parametrize(
        ("annee_limite", "statut"),
        [
            (2029, EventCategory.APPROUVE),
            (2030, EventCategory.CADUC),
        ],
    )
    def test_fin_d_echeance_impacte_caducite(
        self,
        annee_limite: int,
        statut: str,
    ) -> None:
        commune = CommuneFactory()
        procedure = Procedure.objects.create(
            doc_type=TypeDocument.PLUI, collectivite_porteuse=commune
        )
        procedure.event_set.create(
            type="Délibération d'approbation", date_evenement="2024-12-01"
        )
        procedure.event_set.create(type="Fin d'échéance", date_evenement="2030-12-01")
        procedure_with_events = Procedure.objects.with_events(
            avant=date(annee_limite, 12, 15)
        ).get(id=procedure.id)

        assert procedure_with_events.statut == statut

    @pytest.mark.django_db
    @pytest.mark.parametrize(
        ("jour_limite", "statut"),
        [
            (2, None),
            (3, EventCategory.PRESCRIPTION),
            (4, EventCategory.PRESCRIPTION),
            (5, EventCategory.APPROUVE),
        ],
    )
    def test_ignore_event_apres(
        self,
        django_assert_num_queries: DjangoAssertNumQueries,
        jour_limite: int,
        statut: EventCategory,
    ) -> None:
        commune = CommuneFactory()
        procedure = Procedure.objects.create(
            doc_type=TypeDocument.PLUI, collectivite_porteuse=commune
        )
        event_prescription = procedure.event_set.create(
            type="Délibération de prescription du conseil municipal ou communautaire",
            date_evenement="2024-12-03",
        )
        event_approbation = procedure.event_set.create(
            type="Délibération d'approbation", date_evenement="2024-12-05"
        )

        assert event_prescription.category == EventCategory.PRESCRIPTION
        assert event_approbation.category == EventCategory.APPROUVE
        with django_assert_num_queries(2):
            procedure_with_events = Procedure.objects.with_events(
                avant=date(2024, 12, jour_limite)
            ).get(id=procedure.id)

            assert procedure_with_events.statut == statut

    @pytest.mark.django_db
    @pytest.mark.parametrize(
        ("delta_jour", "statut"),
        [
            (-1, EventCategory.APPROUVE),
            (0, EventCategory.APPROUVE),
            (1, None),
        ],
    )
    def test_ignore_event_apres_aujourdhui_si_pas_de_date_fournie(
        self,
        django_assert_num_queries: DjangoAssertNumQueries,
        delta_jour: int,
        statut: EventCategory,
    ) -> None:
        today = timezone.now().date()

        commune = CommuneFactory()
        procedure = Procedure.objects.create(
            doc_type=TypeDocument.PLUI, collectivite_porteuse=commune
        )
        event_approbation = procedure.event_set.create(
            type="Délibération d'approbation",
            date_evenement=today + timedelta(days=delta_jour),
        )

        assert event_approbation.category == EventCategory.APPROUVE
        with django_assert_num_queries(2):
            procedure_with_events = Procedure.objects.with_events().get(id=procedure.id)

            assert procedure_with_events.statut == statut

    @pytest.mark.django_db
    def test_principale_sans_evenement(
        self, django_assert_num_queries: DjangoAssertNumQueries
    ) -> None:
        commune = CommuneFactory()
        procedure = Procedure.objects.create(
            doc_type=TypeDocument.PLUI, collectivite_porteuse=commune
        )

        with django_assert_num_queries(2):
            procedure_with_events = Procedure.objects.with_events().get(id=procedure.id)

            assert not procedure_with_events.dernier_event_impactant
            assert not procedure_with_events.statut

    @pytest.mark.django_db
    def test_principale_annule(
        self, django_assert_num_queries: DjangoAssertNumQueries
    ) -> None:
        commune = CommuneFactory()
        procedure = Procedure.objects.create(
            doc_type=TypeDocument.PLUI, collectivite_porteuse=commune
        )
        event = procedure.event_set.create(
            type="Abrogation", date_evenement="2024-12-01"
        )

        assert event.category == EventCategory.ANNULE
        with django_assert_num_queries(2):
            procedure_with_events = Procedure.objects.with_events().get(id=procedure.id)

            assert procedure_with_events.dernier_event_impactant == event
            assert procedure_with_events.statut == EventCategory.ANNULE

    @pytest.mark.django_db
    def test_principale_ignore_event_invalide(
        self, django_assert_num_queries: DjangoAssertNumQueries
    ) -> None:
        commune = CommuneFactory()
        procedure = Procedure.objects.create(
            doc_type=TypeDocument.PLUI, collectivite_porteuse=commune
        )
        event = procedure.event_set.create(
            type="Délibération d'approbation",
            date_evenement="2024-12-01",
            is_valid=False,
        )

        assert event.category is None
        with django_assert_num_queries(2):
            procedure_with_events = Procedure.objects.with_events().get(id=procedure.id)

            assert not procedure_with_events.dernier_event_impactant
            assert not procedure_with_events.statut

    @pytest.mark.django_db
    def test_principale_carte_communale_deliberation_d_approbation_pas_opposable(
        self, django_assert_num_queries: DjangoAssertNumQueries
    ) -> None:
        commune = CommuneFactory()
        procedure = Procedure.objects.create(
            doc_type=TypeDocument.CC, collectivite_porteuse=commune
        )
        event = procedure.event_set.create(
            type="Délibération d'approbation", date_evenement="2024-12-01"
        )

        assert event.category is None
        with django_assert_num_queries(2):
            procedure_with_events = Procedure.objects.with_events().get(id=procedure.id)

            assert not procedure_with_events.dernier_event_impactant
            assert not procedure_with_events.statut

    @pytest.mark.django_db
    def test_secondaire_non_opposable(
        self, django_assert_num_queries: DjangoAssertNumQueries
    ) -> None:
        commune = CommuneFactory()
        procedure_principale = Procedure.objects.create(
            doc_type=TypeDocument.PLUI, collectivite_porteuse=commune
        )
        procedure_secondaire = Procedure.objects.create(
            parente=procedure_principale,
            doc_type=TypeDocument.PLUI,
            collectivite_porteuse=commune,
        )
        procedure_secondaire.event_set.create(
            type="Délibération d'approbation", date_evenement="2024-12-01"
        )

        with django_assert_num_queries(2):
            procedure_with_events = Procedure.objects.with_events().get(
                id=procedure_secondaire.id
            )

            assert not procedure_with_events.dernier_event_impactant
            assert not procedure_with_events.statut

    @pytest.mark.django_db
    def test_approuvee_quand_prescription_et_approbation_meme_jour(
        self, django_assert_num_queries: DjangoAssertNumQueries
    ) -> None:
        commune = CommuneFactory()
        procedure = Procedure.objects.create(
            doc_type=TypeDocument.PLUI, collectivite_porteuse=commune
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

        assert approbation.category == EventCategory.APPROUVE
        assert prescription_inseree_avant.category == EventCategory.PRESCRIPTION
        assert prescription_inseree_apres.category == EventCategory.PRESCRIPTION

        with django_assert_num_queries(2):
            procedure_with_events = Procedure.objects.with_events().first()

            assert procedure_with_events.dernier_event_impactant == approbation
            assert procedure_with_events.statut == EventCategory.APPROUVE

    @pytest.mark.django_db
    def test_abandon_quand_prescription_et_abandon_meme_jour(
        self, django_assert_num_queries: DjangoAssertNumQueries
    ) -> None:
        commune = CommuneFactory()
        procedure = Procedure.objects.create(
            doc_type=TypeDocument.PLUI, collectivite_porteuse=commune
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

        assert abandon.category == EventCategory.ABANDON
        assert prescription_insere_avant.category == EventCategory.PRESCRIPTION
        assert prescription_insere_apres.category == EventCategory.PRESCRIPTION

        with django_assert_num_queries(2):
            procedure_with_events = Procedure.objects.with_events().first()

            assert procedure_with_events.dernier_event_impactant == abandon
            assert procedure_with_events.statut == EventCategory.ABANDON

    @pytest.mark.django_db
    def test_event_sans_date_ignore(
        self, django_assert_num_queries: DjangoAssertNumQueries
    ) -> None:
        commune = CommuneFactory()
        procedure = Procedure.objects.create(
            doc_type=TypeDocument.PLUI, collectivite_porteuse=commune
        )
        event = procedure.event_set.create(type="Délibération d'approbation")

        assert event.category == EventCategory.APPROUVE
        with django_assert_num_queries(2):
            procedure_with_events = Procedure.objects.with_events().get(id=procedure.id)

            assert not procedure_with_events.dernier_event_impactant
            assert not procedure_with_events.statut


class TestProcedureEnCours:
    @pytest.mark.django_db
    @pytest.mark.parametrize(
        ("event_type", "event_category", "expected_en_cours"),
        [
            ("Prescription", EventCategory.PRESCRIPTION, True),
            ("Publication périmètre", EventCategory.PUBLICATION_PERIMETRE, True),
            ("Délibération d'approbation", EventCategory.APPROUVE, False),
        ],
    )
    def test_categories_considerees_en_cours(
        self,
        event_type: str,
        event_category: EventCategory,
        expected_en_cours: bool,
        django_assert_num_queries: DjangoAssertNumQueries,
    ) -> None:
        commune = CommuneFactory()
        procedure = Procedure.objects.create(
            doc_type=TypeDocument.PLUI, collectivite_porteuse=commune
        )
        event = procedure.event_set.create(type=event_type, date_evenement="2024-12-01")

        assert event.category == event_category
        with django_assert_num_queries(2):
            procedure_with_events = Procedure.objects.with_events().get(id=procedure.id)

            assert procedure_with_events.dernier_event_impactant == event
            assert procedure_with_events.statut == event_category
            assert procedure_with_events.is_en_cours == expected_en_cours

    @pytest.mark.django_db
    def test_abrogation_jamais_en_cours(
        self, django_assert_num_queries: DjangoAssertNumQueries
    ) -> None:
        commune = CommuneFactory()

        procedure = Procedure.objects.create(
            doc_type=TypeDocument.PLUI,
            type="Abrogation",
            collectivite_porteuse=commune,
        )
        event = procedure.event_set.create(
            type="Prescription", date_evenement="2024-12-01"
        )

        with django_assert_num_queries(2):
            procedure_with_events = Procedure.objects.with_events().get(id=procedure.id)

            assert procedure_with_events.dernier_event_impactant == event
            assert procedure_with_events.statut == EventCategory.PRESCRIPTION
            assert not procedure_with_events.is_en_cours

    @pytest.mark.django_db
    def test_pos_jamais_en_cours(
        self, django_assert_num_queries: DjangoAssertNumQueries
    ) -> None:
        commune = CommuneFactory()

        procedure = Procedure.objects.create(
            doc_type=TypeDocument.POS, collectivite_porteuse=commune
        )
        event = procedure.event_set.create(
            type="Prescription", date_evenement="2024-12-01"
        )

        with django_assert_num_queries(2):
            procedure_with_events = Procedure.objects.with_events().get(id=procedure.id)

            assert procedure_with_events.dernier_event_impactant == event
            assert procedure_with_events.statut == EventCategory.PRESCRIPTION
            assert not procedure_with_events.is_en_cours


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

        procedure = Procedure.objects.earliest("id")
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

        procedure = Procedure.full_objects.earliest("id")
        for item in [*to_be_removed_fields, *heavy_fields]:
            with subtests.test(item, item=item):
                assert item in procedure.__dict__


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
        self, doc_type: str, type_event: str, category: EventCategory
    ) -> None:
        procedure = Procedure(doc_type=doc_type)
        assert Event(procedure=procedure, type=type_event).category == category

    def test_date_null(self) -> None:
        procedure = Procedure()
        assert Event(procedure=procedure).date_evenement is None

    @pytest.mark.django_db
    def test_event_archived(self) -> None:
        profile = ProfileFactory()
        event = EventFactory.build()
        assert not event.is_archived

        event = EventFactory.build(archived_at=timezone.now(), archived_by=profile)
        assert event.is_archived

        event = EventFactory.build(archived_at=timezone.now(), archived_by=None)
        with pytest.raises(ValidationError) as error:
            event.save()
        assert error.value.messages == [
            "Le champ “archived_by” doit être renseigné uniquement si le champ “archived_at” est renseigné"
        ]

        event = EventFactory.build(archived_at=None, archived_by=profile)
        with pytest.raises(ValidationError) as error:
            event.save()
        assert error.value.messages == [
            "Le champ “archived_by” doit être renseigné uniquement si le champ “archived_at” est renseigné"
        ]

        event = EventFactory.build()
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

        event = EventFactory(procedure=None)
        event.description = "Something new"
        event.save()
        event.refresh_from_db()
        assert not event.project_id


@pytest.mark.django_db
class TestEventUpdate:
    def test_event_procedure_status_handler__status_update(self) -> None:
        procedure = ProcedureFactory(
            with_event=True,
            with_event__category=EventCategory.PUBLICATION_PERIMETRE,
            doc_type=TypeDocument.CC,
        )
        procedure = Procedure.objects.with_events().get(pk=procedure.pk)
        procedure.status = procedure.statut
        assert procedure.status == EventCategory.PUBLICATION_PERIMETRE

        # Adding or updating an event triggers the `event_procedure_status_handler` sql function.
        procedure.event_set.add(*[EventFactory(type="Retrait de l'annulation totale")])
        procedure.refresh_from_db()
        assert procedure.status == "opposable"

    @pytest.mark.xfail(
        reason="DB calls the Nuxt3 endpoint which is not listening on test and is impossible to mock."
    )
    def test_event_procedure_status_handler__commune_procedure_update(self) -> None:
        commune = CommuneFactory()
        procedure = ProcedureFactory(
            with_event=True,
            with_event__category=EventCategory.PUBLICATION_PERIMETRE,
            doc_type=TypeDocument.CC,
            with_perimetre=[commune],
        )
        procedure = Procedure.objects.with_events().get(pk=procedure.pk)
        procedure.status = procedure.statut
        assert not procedure.perimetre_through.first().opposable

        # Adding or updating an event triggers the `event_procedure_status_handler` sql function.
        event_type = "Retrait de l'annulation totale"
        procedure.event_set.add(*[EventFactory(type=event_type)])
        procedure.refresh_from_db()
        assert procedure.perimetre_through.first().opposable


@pytest.mark.django_db
class TestEventManagers:
    def test_base_manager(self, subtests: pytest.Subtests) -> None:
        EventFactory()
        to_be_removed_fields = [
            "is_sudocuh_scot",
            "test",  # Still set in Nuxt code but not read.
            "code",
            "from_sudocuh_procedure_id",
        ]
        heavy_fields = [
            "description",
            "attachements",
            "actors",
        ]
        event = Event.objects.earliest("id")
        for item in [*to_be_removed_fields, *heavy_fields]:
            with subtests.test(item, item=item):
                assert item not in event.__dict__

    @pytest.mark.django_db
    def test_managers_archived_events(self) -> None:
        event_not_archived = EventFactory(archived_at=None, archived_by=None)
        EventFactory(archived_at=timezone.now(), archived_by=ProfileFactory())

        queryset = Event.objects.all()
        assert queryset.count() == 1
        event = queryset.first()
        assert event.id == event_not_archived.id

        queryset = Event.full_objects.all()
        assert queryset.count() == 2

        queryset = Event.full_objects.without_archived()
        assert queryset.count() == 1
        event = queryset.first()
        assert event.id == event_not_archived.id

    @pytest.mark.django_db
    def test_full_objects_manager(self, subtests: pytest.Subtests) -> None:
        EventFactory()
        to_be_removed_fields = [
            "is_sudocuh_scot",
            "test",
            "code",
            "from_sudocuh_procedure_id",
        ]
        heavy_fields = [
            "description",
            "attachements",
            "actors",
        ]
        event = Event.full_objects.earliest("id")
        for item in [*to_be_removed_fields, *heavy_fields]:
            with subtests.test(item, item=item):
                assert item in event.__dict__


class TestCommuneProceduresPrincipales:
    @pytest.mark.django_db
    def test_exclut_secondaires(
        self, django_assert_num_queries: DjangoAssertNumQueries
    ) -> None:
        commune = CommuneFactory()

        procedure_secondaire = ProcedureFactory(
            with_parente=True,
            doc_type=TypeDocument.PLUI,
            collectivite_porteuse=commune,
            with_perimetre=[commune],
            parente__with_perimetre=[commune],
        )
        procedure_principale = procedure_secondaire.parente

        with django_assert_num_queries(3):
            commune = Commune.objects.with_procedures_principales().get()
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
            doc_type=TypeDocument.PLUI,
            collectivite_porteuse=commune,
            with_perimetre=[commune],
            doublon_cache_de__with_perimetre=[commune],
        )
        procedure_reelle = procedure_doublon.doublon_cache_de

        with django_assert_num_queries(3):
            commune = Commune.objects.with_procedures_principales().get()
            assert commune.procedures_principales == [procedure_reelle]


class TestCommunePlanEnCours:
    @pytest.mark.django_db
    def test_plus_recent_en_cours(
        self, django_assert_num_queries: DjangoAssertNumQueries
    ) -> None:
        commune = CommuneFactory()

        procedure_saisie_avant = ProcedureFactory(
            doc_type=TypeDocument.PLU,
            collectivite_porteuse=commune,
            with_perimetre=[commune],
        )
        procedure_saisie_avant.event_set.create(
            type="Prescription", date_evenement="2022-12-01"
        )

        procedure_en_cours = ProcedureFactory(
            doc_type=TypeDocument.PLUI,
            collectivite_porteuse=commune,
            with_perimetre=[commune],
        )
        procedure_en_cours.event_set.create(
            type="Prescription", date_evenement="2024-12-01"
        )

        procedure_saisie_apres = ProcedureFactory(
            doc_type=TypeDocument.PLU,
            collectivite_porteuse=commune,
            with_perimetre=[commune],
        )
        procedure_saisie_apres.event_set.create(
            type="Prescription", date_evenement="2023-12-01"
        )

        with django_assert_num_queries(3):
            commune = Commune.objects.with_procedures_principales().get()
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
            doc_type=TypeDocument.PLUI,
            collectivite_porteuse=commune,
            with_perimetre=[commune],
        )
        procedure_en_cours.event_set.create(
            type="Prescription", date_evenement="2024-12-01"
        )

        _procedure_pas_commencee = ProcedureFactory(
            doc_type=TypeDocument.PLU,
            collectivite_porteuse=commune,
            with_perimetre=[commune],
        )

        with django_assert_num_queries(3):
            commune = Commune.objects.with_procedures_principales().get()
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
                doc_type=TypeDocument.PLU,
                collectivite_porteuse=collectivite,
                with_perimetre=[commune],
            )
            procedure.event_set.create(type="Prescription", date_evenement="2022-12-01")

        if plan_opposable:
            collectivite = CollectiviteFactory(code_insee_unique="200004444")
            procedure = ProcedureFactory(
                doc_type=TypeDocument.PLU,
                collectivite_porteuse=collectivite,
                with_perimetre=[commune],
            )
            procedure.event_set.create(
                type="Délibération d'approbation", date_evenement="2022-12-01"
            )

        commune = Commune.objects.with_procedures_principales().first()
        assert commune.collectivite_porteuse.code_insee_unique == collectivite_attendue


class TestCommuneOpposabilite:
    @pytest.mark.django_db
    def test_plus_recente_opposable(
        self, django_assert_num_queries: DjangoAssertNumQueries
    ) -> None:
        commune = CommuneFactory()
        procedure_precedente_saisie_avant = ProcedureFactory(
            doc_type=TypeDocument.PLU,
            collectivite_porteuse=commune,
            with_perimetre=[commune],
        )
        procedure_precedente_saisie_avant.event_set.create(
            type="Délibération d'approbation", date_evenement="2022-12-01"
        )

        procedure_opposable = ProcedureFactory(
            doc_type=TypeDocument.PLUI,
            collectivite_porteuse=commune,
            with_perimetre=[commune],
        )
        procedure_opposable.event_set.create(
            type="Délibération d'approbation", date_evenement="2024-12-01"
        )

        procedure_precedente_saisie_apres = ProcedureFactory(
            doc_type=TypeDocument.PLU,
            collectivite_porteuse=commune,
            with_perimetre=[commune],
        )
        procedure_precedente_saisie_apres.event_set.create(
            type="Délibération d'approbation", date_evenement="2023-12-01"
        )

        with django_assert_num_queries(3):
            commune = Commune.objects.with_procedures_principales().get()
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
            doc_type=TypeDocument.PLUI,
            collectivite_porteuse=commune,
            with_perimetre=[commune],
        )
        plan_opposable.event_set.create(
            type="Délibération d'approbation", date_evenement="2024-01-02"
        )

        schema_opposable = ProcedureFactory(
            doc_type=TypeDocument.SCOT,
            collectivite_porteuse=commune,
            with_perimetre=[commune],
        )
        schema_opposable.event_set.create(
            type="Délibération d'approbation", date_evenement="2024-01-01"
        )

        with django_assert_num_queries(3):
            commune = Commune.objects.with_procedures_principales().get()
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
            doc_type=TypeDocument.PLUI,
            with_perimetre=[commune],
        )
        procedure_opposable.event_set.create(
            type="Délibération d'approbation", date_evenement="2024-12-01"
        )

        with django_assert_num_queries(3):
            commune = Commune.objects.with_procedures_principales().get()
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
            doc_type=TypeDocument.PLUI,
            with_perimetre=[commune],
        )
        procedure_en_cours.event_set.create(
            type="Délibération de prescription du conseil municipal ou communautaire",
            date_evenement="2024-12-01",
        )

        with django_assert_num_queries(3):
            commune = Commune.objects.with_procedures_principales().get()
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
            doc_type=TypeDocument.PLUI,
            type="Abrogation",
            with_perimetre=[commune],
        )
        procedure_approuvee.event_set.create(
            type="Délibération d'approbation", date_evenement="2024-12-01"
        )

        with django_assert_num_queries(3):
            commune = Commune.objects.with_procedures_principales().get()
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
            doc_type=TypeDocument.PLUI,
            collectivite_porteuse=commune,
            with_perimetre=[commune],
            parente__with_perimetre=[commune],
        )
        procedure_principale = procedure_secondaire.parente
        procedure_secondaire.event_set.create(
            type="Délibération d'approbation", date_evenement="2024-12-01"
        )

        with django_assert_num_queries(3):
            commune = Commune.objects.with_procedures_principales().get()
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
            commune = Commune.objects.with_procedures_principales().get()
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
            doc_type=TypeDocument.PLUI,
            with_perimetre=[commune],
        )
        procedure_opposable_fevrier.event_set.create(
            type="Délibération d'approbation", date_evenement="2024-02-02"
        )

        procedure_opposable_janvier = ProcedureFactory(
            collectivite_porteuse=commune,
            doc_type=TypeDocument.PLU,
            with_perimetre=[commune],
        )
        procedure_opposable_janvier.event_set.create(
            type="Délibération d'approbation", date_evenement="2024-01-01"
        )

        with django_assert_num_queries(2):
            procedures = Procedure.objects.with_events()

            assert all(
                procedure.statut == EventCategory.APPROUVE for procedure in procedures
            )

        with django_assert_num_queries(3):
            commune = Commune.objects.with_procedures_principales(
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

        commune = Commune.objects.with_procedures_principales().first()
        assert commune.code_etat_simplifie == "99"
        assert commune.code_etat_complet == "9999"

    @pytest.mark.django_db
    @pytest.mark.parametrize(
        ("create_collectivite", "perimetre_count", "expected_code"),
        [
            (CommuneFactory, 1, CodeCompetencePerimetre.COMPETENCE_COMMUNE),
            (
                CollectiviteFactory,
                1,
                CodeCompetencePerimetre.COMPETENCE_EPCI_PROCEDURE_COMMUNALE,
            ),
            (
                CollectiviteFactory,
                2,
                CodeCompetencePerimetre.COMPETENCE_EPCI_PERIMETRE_INFERIEUR_EPCI,
            ),
            (
                CollectiviteFactory,
                3,
                CodeCompetencePerimetre.COMPETENCE_EPCI_PERIMETRE_EPCI,
            ),
        ],
    )
    def test_competence_intercommunalite_code(
        self,
        create_collectivite: Callable[[], Collectivite],
        perimetre_count: int,
        expected_code: CodeCompetencePerimetre,
    ) -> None:
        collectivite_porteuse = create_collectivite()

        if not collectivite_porteuse.is_commune:
            for _ in range(3):
                commune = CommuneFactory()
                commune.adhesions.add(collectivite_porteuse)

        MaterializedViewFlatMembership.refresh()

        procedure = ProcedureFactory(
            collectivite_porteuse=collectivite_porteuse,
            with_perimetre=[CommuneFactory() for _ in range(perimetre_count)],
        )

        procedure = Procedure.objects.get(id=procedure.id)
        assert (
            procedure.competence_intercommunalite_code(collectivite_porteuse)
            == expected_code
        )


class TestEnums:
    def test_type_collectivite_epci(self) -> None:
        assert TypeCollectivite.CC in TypeCollectivite.epci()
        assert TypeCollectivite.COM not in TypeCollectivite.epci()


class TestEventType:
    @pytest.mark.django_db
    def test_order(self) -> None:
        cc1 = EventTypeFactory(document_type=EventType.DocumentType.CC, name="CC1")

        assert cc1.order == 1

        cc2 = EventTypeFactory(document_type=EventType.DocumentType.CC, name="CC2")
        assert cc2.order == 2

        plu1 = EventTypeFactory(document_type=EventType.DocumentType.PLU)
        assert plu1.order == 1
