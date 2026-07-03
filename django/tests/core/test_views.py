import datetime
import uuid
from csv import DictReader
from typing import Any

import pytest
from django.test import Client
from django.urls import reverse
from freezegun import freeze_time
from pytest_django import DjangoAssertNumQueries
from syrupy import SnapshotAssertion

from docurba.core.enums import CommuneType
from docurba.core.models import (
    EVENT_TYPE_BY_EVENT_CATEGORY,
    Collectivite,
    Commune,
    EventCategory,
    Procedure,
    Topic,
    TypeCollectivite,
    TypeDocument,
)
from tests.core.factories import (
    CollectiviteFactory,
    CommuneFactory,
    EventFactory,
    ProcedureFactory,
)


def csv_to_json_like(content: bytes) -> list[dict[str | Any, str | Any]]:
    return list(DictReader(content.decode().splitlines()))


@pytest.mark.parametrize("view_name", ["api_perimetres", "api_communes", "api_scots"])
@pytest.mark.django_db
class TestEveryAPI:
    @pytest.mark.parametrize(
        ("avant"),
        ["2023-1-01", "2023-02-30", "invalid-date", "2023/01/01"],
    )
    def test_invalid_avant_filter(
        self,
        client: Client,
        view_name: str,
        avant: str,
    ) -> None:
        response = client.get(reverse(view_name), {"avant": avant})

        assert response.status_code == 400
        assert (
            response.content.decode()
            == "Le paramètre 'avant' doit être une date valide au format YYYY-MM-DD."
        )


@pytest.mark.parametrize(
    "view_name",
    ["api_perimetres", "api_communes"],
)
@pytest.mark.django_db
class TestApiPerimetresAndCommunes:
    def _default_procedure_factory_attrs(
        self, perimetre: list[Commune]
    ) -> dict[str, Any]:
        return {
            "for_snapshot": True,
            "with_perimetre": perimetre,
            "doc_type": TypeDocument.PLU,
            "with_event": True,
            "with_event__category": EventCategory.APPROUVE,
            "with_event__date_evenement": datetime.date(2024, 6, 6),
        }

    def test_is_intercommunal(
        self, client: Client, view_name: str, snapshot: SnapshotAssertion
    ) -> None:
        collectivite = CollectiviteFactory(for_snapshot=True)
        communes = [
            CommuneFactory(for_snapshot=True),
            CommuneFactory(
                code_insee="30135",
                nom="Jonquières-Saint-Vincent",
                departement__code_insee="30",
            ),
            CommuneFactory(
                code_insee="30189",
                nom="Nîmes",
                departement__code_insee="30",
            ),
        ]
        collectivite.adhesions.add(*communes)
        ProcedureFactory(
            **self._default_procedure_factory_attrs(perimetre=communes[1:])
            | {"doc_type": TypeDocument.PLUIH}
        )
        response = client.get(reverse(view_name))
        assert response.status_code == 200
        assert csv_to_json_like(response.content) == snapshot()

    def test_is_not_intercommunal(
        self, client: Client, view_name: str, snapshot: SnapshotAssertion
    ) -> None:
        collectivite = CollectiviteFactory(for_snapshot=True)
        commune = CommuneFactory(for_snapshot=True)
        collectivite.adhesions.add(*[commune])
        ProcedureFactory(**self._default_procedure_factory_attrs(perimetre=[commune]))
        response = client.get(reverse(view_name))
        assert response.status_code == 200
        assert csv_to_json_like(response.content) == snapshot()

    def test_is_not_plu_like(
        self, client: Client, view_name: str, snapshot: SnapshotAssertion
    ) -> None:
        collectivite = CollectiviteFactory(for_snapshot=True)
        commune = CommuneFactory(for_snapshot=True)
        collectivite.adhesions.add(*[commune])
        ProcedureFactory(
            **self._default_procedure_factory_attrs(perimetre=[commune])
            | {"doc_type": TypeDocument.CC},
        )

        response = client.get(reverse(view_name))
        assert response.status_code == 200
        assert csv_to_json_like(response.content) == snapshot()

    @pytest.mark.parametrize(("with_filter", "expected_lines"), [(False, 2), (True, 1)])
    def test_departement_filter(
        self,
        client: Client,
        view_name: str,
        with_filter: bool,  # noqa: FBT001
        expected_lines: int,
    ) -> None:
        commune_a = CommuneFactory(departement__code_insee="13")
        commune_b = CommuneFactory(departement__code_insee="84")
        ProcedureFactory(
            **self._default_procedure_factory_attrs(perimetre=[commune_a])
            | {"for_snapshot": False},
        )
        ProcedureFactory(
            **self._default_procedure_factory_attrs(perimetre=[commune_b])
            | {"for_snapshot": False},
        )

        filtre = {}
        if with_filter:
            filtre = {"departement": commune_a.departement.code_insee}
        response = client.get(reverse(view_name), filtre)
        results = csv_to_json_like(response.content)
        assert len(results) == expected_lines
        if with_filter:
            assert (
                results[0][
                    "collectivite_code"
                    if view_name == "api_perimetres"
                    else "code_insee"
                ]
                == commune_a.code_insee
            )


@pytest.mark.django_db
class TestAPIPerimetres:
    def _default_procedure_factory_params(
        self,
        perimetre: list | None = None,
        collectivite_porteuse: Collectivite | None = None,
        procedure_status: EventCategory | None = None,
    ) -> dict[str, Any]:
        if perimetre is None:
            perimetre = [CommuneFactory()]

        if not collectivite_porteuse:
            collectivite_porteuse = perimetre[0]

        params = {
            "doc_type": TypeDocument.PLU,
            "collectivite_porteuse": collectivite_porteuse,
            "with_perimetre": perimetre,
            "with_event": True,
        }
        if procedure_status:
            params["with_event__category"] = procedure_status
        return params

    @pytest.mark.parametrize(
        "nb_communes",
        [
            pytest.param(1, id="one_commune"),
            pytest.param(2, id="several_communes"),
        ],
    )
    @pytest.mark.parametrize(
        "nb_procedures",
        [
            pytest.param(1, id="one_procedure"),
            pytest.param(2, id="several_procedures"),
        ],
    )
    def test_nominal(
        self,
        client: Client,
        django_assert_num_queries: DjangoAssertNumQueries,
        nb_communes: int,
        nb_procedures: int,
        snapshot: SnapshotAssertion,
    ) -> None:
        communes = [("30032", "Beaucaire"), ("30135", "Jonquières-Saint-Vincent")]
        for i in range(nb_communes):
            CommuneFactory(
                code_insee=communes[i][0],
                nom=communes[i][1],
                departement__code_insee="30",
            )
        procedures_uids = [
            uuid.UUID("2cd65b57-7027-4aa5-8d19-5e1baf8d6f07"),
            uuid.UUID("2cd65b57-7027-4aa5-8d19-5e1baf8d6f08"),
            uuid.UUID("2cd65b57-7027-4aa5-8d19-5e1baf8d6f09"),
            uuid.UUID("2cd65b57-7027-4aa5-8d19-5e1baf8d6f10"),
        ]
        for i in range(nb_communes):
            for ii in range(nb_procedures):
                commune = Commune.objects.get(code_insee=communes[i][0])
                ProcedureFactory(
                    pk=procedures_uids[i * nb_communes + ii],
                    collectivite_porteuse=commune,
                    doc_type=TypeDocument.PLU,
                    with_perimetre=[commune],
                )

        with django_assert_num_queries(3):
            response = client.get(
                reverse("api_perimetres"),
            )

        assert response.status_code == 200
        assert csv_to_json_like(response.content) == snapshot()

    @pytest.mark.parametrize(
        ("procedure_status", "expected_result"),
        [
            pytest.param(EventCategory.APPROUVE, "True", id="opposable"),
            pytest.param(EventCategory.PRESCRIPTION, "False", id="not_opposable"),
        ],
    )
    def test_column_opposable(
        self,
        client: Client,
        procedure_status: str,
        expected_result: str,
    ) -> None:
        ProcedureFactory(
            **self._default_procedure_factory_params(procedure_status=procedure_status)
        )
        response = client.get(reverse("api_perimetres"))
        results = csv_to_json_like(response.content)
        assert results[0]["opposable"] == expected_result

    def test_procedures_principales_sans_secondaires(
        self,
        client: Client,
    ) -> None:
        commune = CommuneFactory()
        # Procédure principale
        principal_procedure = ProcedureFactory(
            collectivite_porteuse=commune,
            doc_type=TypeDocument.PLU,
            with_perimetre=[commune],
        )
        # Procédure secondaire : belongs to a parent procedure.
        ProcedureFactory(
            collectivite_porteuse=commune,
            doc_type=TypeDocument.PLU,
            with_perimetre=[commune],
            parente=principal_procedure,
        )
        # Archived are also ignored.
        # Archived if soft delete is true or doublon_cache_de is filled.
        ProcedureFactory(
            collectivite_porteuse=commune,
            doc_type=TypeDocument.PLU,
            with_perimetre=[commune],
            soft_delete=True,
        )
        ProcedureFactory(
            collectivite_porteuse=commune,
            doc_type=TypeDocument.PLU,
            with_perimetre=[commune],
            doublon_cache_de=principal_procedure,
        )
        response = client.get(reverse("api_perimetres"))
        results = csv_to_json_like(response.content)
        assert len(results) == 1
        assert results[0]["procedure_id"] == str(principal_procedure.pk)

    @pytest.mark.parametrize("commune_type", TypeCollectivite.communes())
    def test_communes_types(
        self,
        client: Client,
        snapshot: SnapshotAssertion,
        commune_type: TypeCollectivite,
    ) -> None:
        commune = CommuneFactory(type=commune_type, for_snapshot=True)
        ProcedureFactory(
            **self._default_procedure_factory_params(perimetre=[commune]),
            for_snapshot=True,
        )
        response = client.get(reverse("api_perimetres"))
        assert csv_to_json_like(response.content) == snapshot()

    @pytest.mark.parametrize(
        ("avant_value", "approval_date", "expected_opposable_value"),
        [
            pytest.param(
                "2026-07-05", "2026-07-04", "True", id="avant_is_after_approval_date"
            ),
            pytest.param(
                "2026-07-04", "2026-07-04", "True", id="avant_is_same_as_approval_date"
            ),
            pytest.param(
                "2026-07-02", "2026-07-04", "False", id="avant_is_before_approval_date"
            ),
            pytest.param(
                "", "2026-07-04", "True", id="no_filter_approval_date_in_past"
            ),
            pytest.param(
                "", "2026-07-20", "False", id="no_filter_approval_date_in_future"
            ),
        ],
    )
    @freeze_time("2026-07-08")
    def test_avant_filter(
        self,
        client: Client,
        django_assert_num_queries: DjangoAssertNumQueries,
        avant_value: bool,  # noqa: FBT001
        approval_date: datetime.date,
        expected_opposable_value: int,
    ) -> None:
        ProcedureFactory(
            **self._default_procedure_factory_params(),
            with_event__category=EventCategory.APPROUVE,
            with_event__date_evenement=approval_date,
        )
        with django_assert_num_queries(3):
            response = client.get(f"{reverse('api_perimetres')}?avant={avant_value}")
        results = csv_to_json_like(response.content)
        assert len(results) == 1
        assert results[0]["opposable"] == expected_opposable_value


@pytest.mark.django_db
class TestAPICommunes:
    def _default_procedure_factory_params(
        self,
        perimetre: list | None = None,
        collectivite_porteuse: list | None = None,
        procedure_status: EventCategory | None = None,
    ) -> dict[str, Any]:
        if perimetre is None:
            perimetre = [CommuneFactory()]

        if not collectivite_porteuse:
            collectivite_porteuse = perimetre[0]

        params = {
            "doc_type": TypeDocument.PLU,
            "collectivite_porteuse": collectivite_porteuse,
            "with_perimetre": perimetre,
            "with_event": True,
        }
        if procedure_status:
            params["with_event__category"] = procedure_status
        return params

    def _create_event(
        self,
        category: EventCategory,
        procedure: Procedure,
        date: datetime.date | None = None,
    ) -> None:
        return procedure.event_set.create(
            type=EVENT_TYPE_BY_EVENT_CATEGORY[procedure.doc_type][category][0],
            date_evenement=date or datetime.date(2025, 11, 11),
        )

    @pytest.mark.parametrize(
        ("commune_type", "is_expected_in_results"),
        [
            pytest.param(TypeCollectivite.COMA, False, id="COMA"),
            pytest.param(TypeCollectivite.COMD, False, id="COMD"),
            pytest.param(TypeCollectivite.COM, True, id="COM"),
        ],
    )
    def test_communes_types(
        self,
        client: Client,
        commune_type: TypeCollectivite,
        is_expected_in_results: bool,  # noqa: FBT001
    ) -> None:
        perimetre = [CommuneFactory(type=commune_type)]
        ProcedureFactory(**self._default_procedure_factory_params(perimetre=perimetre))
        response = client.get(reverse("api_communes"))
        assert bool(csv_to_json_like(response.content)) == is_expected_in_results

    def test_nominal(
        self,
        client: Client,
        snapshot: SnapshotAssertion,
    ) -> None:
        intercommunalite = CollectiviteFactory(
            siren="243000585",
            type=TypeCollectivite.CC,
            nom="CC Beaucaire Terre d'Argence",
            departement__code_insee="30",
        )
        commune = CommuneFactory(for_snapshot=True, intercommunalite=intercommunalite)
        collectivite_porteuse = CollectiviteFactory(
            for_snapshot=True, with_members=True, with_members__list=[commune]
        )

        ongoing_procedure = ProcedureFactory(
            **self._default_procedure_factory_params(
                perimetre=[commune],
                collectivite_porteuse=collectivite_porteuse,
                procedure_status=EventCategory.PRESCRIPTION,
            ),
            pk=uuid.UUID("1cd65b57-7027-4aa5-8d19-5e1baf8d6f09"),
            with_event__date_evenement=datetime.date(2026, 5, 5),
        )
        self._create_event(
            procedure=ongoing_procedure,
            category=EventCategory.ARRET_DE_PROJET,
            date=datetime.date(2025, 6, 6),
        )
        self._create_event(
            procedure=ongoing_procedure,
            category=EventCategory.PORTER_A_CONNAISSANCE,
            date=datetime.date(2025, 7, 7),
        )
        self._create_event(
            procedure=ongoing_procedure,
            category=EventCategory.PORTER_A_CONNAISSANCE_COMPLEMENTAIRE,
            date=datetime.date(2025, 8, 8),
        )
        approved_procedure = ProcedureFactory(
            pk=uuid.UUID("1cd65b57-7027-4aa5-8d19-5e1baf8d6f10"),
            **self._default_procedure_factory_params(
                perimetre=[commune],
                collectivite_porteuse=collectivite_porteuse,
                procedure_status=EventCategory.APPROUVE,
            ),
            with_event__date_evenement=datetime.date(2026, 7, 6),
        )
        self._create_event(
            procedure=approved_procedure,
            category=EventCategory.PRESCRIPTION,
            date=datetime.date(2025, 1, 1),
        )
        self._create_event(
            procedure=approved_procedure,
            category=EventCategory.PORTER_A_CONNAISSANCE,
            date=datetime.date(2025, 2, 2),
        )
        self._create_event(
            procedure=approved_procedure,
            category=EventCategory.PORTER_A_CONNAISSANCE_COMPLEMENTAIRE,
            date=datetime.date(2025, 3, 3),
        )

        self._create_event(
            procedure=approved_procedure,
            category=EventCategory.CARACTERE_EXECUTOIRE,
            date=datetime.date(2025, 4, 4),
        )

        self._create_event(
            procedure=approved_procedure,
            category=EventCategory.ARRET_DE_PROJET,
            date=datetime.date(2025, 5, 5),
        )

        response = client.get(reverse("api_communes"))
        assert response.status_code == 200
        assert response["content-type"] == "text/csv;charset=utf-8"
        results = csv_to_json_like(response.content)
        assert results == snapshot()

    def test_nb_queries(
        self, client: Client, django_assert_num_queries: DjangoAssertNumQueries
    ) -> None:
        for _ in range(2):
            ProcedureFactory(**self._default_procedure_factory_params())
            with django_assert_num_queries(3):
                response = client.get(reverse("api_communes"))
        assert response.status_code == 200

    def test_is_nouvelle(
        self,
        client: Client,
    ) -> None:
        commune = CommuneFactory()
        ProcedureFactory(
            **self._default_procedure_factory_params(perimetre=[commune]),
        )

        commune_deleguee = CommuneFactory(
            type=TypeCollectivite.COMD,
            nouvelle=commune,
            code_insee="30032",
            nom="Beaucaire déleguée",
            departement__code_insee="30",
        )
        ProcedureFactory(
            **self._default_procedure_factory_params(perimetre=[commune_deleguee]),
        )
        response = client.get(reverse("api_communes"))
        results = csv_to_json_like(response.content)
        assert len(results) == 1
        assert results[0]["com_nouvelle"] == "True"

    @pytest.mark.parametrize(
        (
            "with_procedure",
            "procedure_status",
        ),
        [
            pytest.param(
                True,
                EventCategory.APPROUVE,
                id="approved_procedure",
            ),
            pytest.param(
                True,
                EventCategory.PRESCRIPTION,
                id="ongoing_procedure",
            ),
            pytest.param(False, "", id="no_procedure"),
        ],
    )
    def test_commune_collectivite_porteuse(
        self,
        client: Client,
        with_procedure: bool,  # noqa: FBT001
        procedure_status: EventCategory,
        snapshot: SnapshotAssertion,
    ) -> None:
        commune = CommuneFactory(for_snapshot=True)
        collectivite = CollectiviteFactory(
            type=TypeCollectivite.CC,
            for_snapshot=True,
        )
        if with_procedure:
            ProcedureFactory(
                **self._default_procedure_factory_params(
                    perimetre=[commune], collectivite_porteuse=collectivite
                ),
                pk=uuid.UUID("1cd65b57-7027-4aa5-8d19-5e1baf8d6f09"),
                with_event__category=procedure_status,
                with_event__date_evenement=datetime.date(2025, 2, 2),
            )
        response = client.get(reverse("api_communes"))
        results = csv_to_json_like(response.content)
        assert len(results) == 1
        assert results == snapshot()

    @pytest.mark.parametrize(
        "procedure_status",
        [
            pytest.param(
                EventCategory.PUBLICATION_PERIMETRE,
                id="ongoing_procedure",
            ),
            pytest.param(
                EventCategory.APPROUVE,
                id="approved_procedure",
            ),
        ],
    )
    def test_num_procedure_sudocuh(
        self, client: Client, procedure_status: EventCategory
    ) -> None:
        ProcedureFactory(
            **self._default_procedure_factory_params(procedure_status=procedure_status),
            from_sudocuh="12345",
        )
        response = client.get(reverse("api_communes"))
        assert response.status_code == 200
        results = csv_to_json_like(response.content)
        if procedure_status == EventCategory.PUBLICATION_PERIMETRE:
            assert results[0]["pc_num_procedure_sudocuh"] == "12345"
        elif EventCategory.APPROUVE:
            assert results[0]["pa_num_procedure_sudocuh"] == "12345"

    @pytest.mark.parametrize(
        "procedure_status",
        [
            pytest.param(
                EventCategory.PUBLICATION_PERIMETRE,
                id="ongoing_procedure",
            ),
            pytest.param(
                EventCategory.APPROUVE,
                id="approved_procedure",
            ),
        ],
    )
    def test_nb_communes(self, client: Client, procedure_status: EventCategory) -> None:
        perimetre = [
            CommuneFactory(),
            CommuneFactory(type=CommuneType.COMD),
            CommuneFactory(type=CommuneType.COMA),
        ]
        ProcedureFactory(
            **self._default_procedure_factory_params(
                procedure_status=procedure_status,
                perimetre=perimetre,
            ),
        )
        response = client.get(reverse("api_communes"))
        assert response.status_code == 200
        results = csv_to_json_like(response.content)
        if procedure_status == EventCategory.PUBLICATION_PERIMETRE:
            assert results[0]["pc_nb_communes"] == "3"
        elif EventCategory.APPROUVE:
            assert results[0]["pa_nb_communes"] == "3"

    @pytest.mark.parametrize(
        "procedure_status",
        [
            pytest.param(
                EventCategory.PUBLICATION_PERIMETRE,
                id="ongoing_procedure",
            ),
            pytest.param(
                EventCategory.APPROUVE,
                id="approved_procedure",
            ),
        ],
    )
    def test_moe_fields(self, client: Client, procedure_status: EventCategory) -> None:
        ProcedureFactory(
            **self._default_procedure_factory_params(
                procedure_status=procedure_status,
            ),
            maitrise_d_oeuvre={
                "coutplanht": 10000,
                "coutplanttc": 12000,
                "nomprestaexterne": "Groupement des béliers",
            },
        )
        response = client.get(reverse("api_communes"))
        assert response.status_code == 200
        results = csv_to_json_like(response.content)
        if procedure_status == EventCategory.PUBLICATION_PERIMETRE:
            assert results[0]["pc_nom_sst"] == "Groupement des béliers"
            assert results[0]["pc_cout_sst_ht"] == "10000"
            assert results[0]["pc_cout_sst_ttc"] == "12000"
        elif EventCategory.APPROUVE:
            assert results[0]["pa_nom_sst"] == "Groupement des béliers"
            assert results[0]["pa_cout_sst_ht"] == "10000"
            assert results[0]["pa_cout_sst_ttc"] == "12000"

    @pytest.mark.parametrize(
        "procedure_status",
        [
            pytest.param(
                EventCategory.PUBLICATION_PERIMETRE,
                id="ongoing_procedure",
            ),
            pytest.param(
                EventCategory.APPROUVE,
                id="approved_procedure",
            ),
        ],
    )
    def test_moe_empty_fields(
        self, client: Client, procedure_status: EventCategory
    ) -> None:
        ProcedureFactory(
            **self._default_procedure_factory_params(
                procedure_status=procedure_status,
            ),
            maitrise_d_oeuvre={
                "coutplanht": None,
                "coutplanttc": None,
                "nomprestaexterne": None,
            },
        )
        response = client.get(reverse("api_communes"))
        assert response.status_code == 200
        results = csv_to_json_like(response.content)
        if procedure_status == EventCategory.PUBLICATION_PERIMETRE:
            assert results[0]["pc_nom_sst"] == ""
            assert results[0]["pc_cout_sst_ht"] == ""
            assert results[0]["pc_cout_sst_ttc"] == ""
        elif EventCategory.APPROUVE:
            assert results[0]["pa_nom_sst"] == ""
            assert results[0]["pa_cout_sst_ht"] == ""
            assert results[0]["pa_cout_sst_ttc"] == ""

    @pytest.mark.parametrize(
        "procedure_status",
        [
            pytest.param(
                EventCategory.PUBLICATION_PERIMETRE,
                id="ongoing_procedure",
            ),
            pytest.param(
                EventCategory.APPROUVE,
                id="approved_procedure",
            ),
        ],
    )
    def test_pluih(self, client: Client, procedure_status: EventCategory) -> None:
        perimetre = [CommuneFactory(), CommuneFactory()]
        ProcedureFactory(
            **self._default_procedure_factory_params(
                procedure_status=procedure_status, perimetre=perimetre
            ),
            vaut_PLH=True,
        )
        response = client.get(reverse("api_communes"))
        assert response.status_code == 200
        results = csv_to_json_like(response.content)
        if procedure_status == EventCategory.PUBLICATION_PERIMETRE:
            assert results[0]["pc_pluih"] == "True"
        elif EventCategory.APPROUVE:
            assert results[0]["pa_pluih"] == "True"

    @pytest.mark.parametrize(
        "procedure_status",
        [
            pytest.param(
                EventCategory.PUBLICATION_PERIMETRE,
                id="ongoing_procedure",
            ),
            pytest.param(
                EventCategory.APPROUVE,
                id="approved_procedure",
            ),
        ],
    )
    def test_sectoriel(self, client: Client, procedure_status: EventCategory) -> None:
        # We need to specify the INSEE code because results are ordered by the INSEE code
        # and we need to check the first result.
        perimetre = [CommuneFactory(code_insee="30135")]
        collectivite_porteuse = CollectiviteFactory(
            with_members=True,
            with_members__list=[*perimetre, CommuneFactory(code_insee="30189")],
        )
        ProcedureFactory(
            **self._default_procedure_factory_params(
                procedure_status=procedure_status,
                perimetre=perimetre,
                collectivite_porteuse=collectivite_porteuse,
            ),
        )
        response = client.get(reverse("api_communes"))
        assert response.status_code == 200
        results = csv_to_json_like(response.content)
        if procedure_status == EventCategory.PUBLICATION_PERIMETRE:
            assert results[0]["pc_sectoriel"] == "True"
        elif EventCategory.APPROUVE:
            assert results[0]["pa_sectoriel"] == "True"

    @pytest.mark.parametrize(
        "procedure_status",
        [
            pytest.param(
                EventCategory.PUBLICATION_PERIMETRE,
                id="ongoing_procedure",
            ),
            pytest.param(
                EventCategory.APPROUVE,
                id="approved_procedure",
            ),
        ],
    )
    def test_pdu_tient_lieu(
        self, client: Client, procedure_status: EventCategory
    ) -> None:
        perimetre = [CommuneFactory(), CommuneFactory()]
        ProcedureFactory(
            **self._default_procedure_factory_params(
                procedure_status=procedure_status, perimetre=perimetre
            ),
            vaut_PDM=True,
        )
        response = client.get(reverse("api_communes"))
        assert response.status_code == 200
        results = csv_to_json_like(response.content)
        if procedure_status == EventCategory.PUBLICATION_PERIMETRE:
            assert results[0]["pc_pdu_tient_lieu"] == "True"
        elif EventCategory.APPROUVE:
            assert results[0]["pa_pdu_tient_lieu"] == "True"

    @pytest.mark.parametrize(
        "procedure_status",
        [
            pytest.param(
                EventCategory.PUBLICATION_PERIMETRE,
                id="ongoing_procedure",
            ),
            pytest.param(
                EventCategory.APPROUVE,
                id="approved_procedure",
            ),
        ],
    )
    def test_pdu_obligatoire(
        self, client: Client, procedure_status: EventCategory
    ) -> None:
        ProcedureFactory(
            **self._default_procedure_factory_params(procedure_status=procedure_status),
            obligation_PDU=True,
        )
        response = client.get(reverse("api_communes"))
        assert response.status_code == 200
        results = csv_to_json_like(response.content)
        if procedure_status == EventCategory.PUBLICATION_PERIMETRE:
            assert results[0]["pc_pdu_obligatoire"] == "True"
        elif EventCategory.APPROUVE:
            assert results[0]["pa_pdu_obligatoire"] == "True"

    @pytest.mark.parametrize(
        "procedure_status",
        [
            pytest.param(
                EventCategory.PUBLICATION_PERIMETRE,
                id="ongoing_procedure",
            ),
            pytest.param(
                EventCategory.APPROUVE,
                id="approved_procedure",
            ),
        ],
    )
    def test_plui_valant_scot(
        self, client: Client, procedure_status: EventCategory
    ) -> None:
        ProcedureFactory(
            **self._default_procedure_factory_params(procedure_status=procedure_status),
            vaut_SCoT=True,
        )
        response = client.get(reverse("api_communes"))
        assert response.status_code == 200
        results = csv_to_json_like(response.content)
        if procedure_status == EventCategory.PUBLICATION_PERIMETRE:
            assert results[0]["pc_plui_valant_scot"] == "True"
        elif EventCategory.APPROUVE:
            assert results[0]["pa_plui_valant_scot"] == "True"

    def test_commune_sans_intercommunalite_ne_crashe_pas(self, client: Client) -> None:
        """
        4 îles n'ont pas d'intercommunalité.

        https://fr.wikipedia.org/wiki/Catégorie:Commune_hors_intercommunalité_à_fiscalité_propre_en_France
        """
        commune = CommuneFactory(intercommunalite=None)
        ProcedureFactory(**self._default_procedure_factory_params(perimetre=[commune]))
        response = client.get(reverse("api_communes"))
        assert response.status_code == 200
        results = csv_to_json_like(response.content)
        assert len(results) == 1

    @pytest.mark.parametrize(
        "procedure_status",
        [
            pytest.param(
                EventCategory.PUBLICATION_PERIMETRE,
                id="ongoing_procedure",
            ),
            pytest.param(
                EventCategory.APPROUVE,
                id="approved_procedure",
            ),
        ],
    )
    @pytest.mark.parametrize(
        ("procedure_topics", "expected_result"),
        [
            pytest.param("", "", id="no_topic"),
            pytest.param(["zan"], "Trajectoire ZAN", id="one_topic"),
            pytest.param(
                ["zan", "forest_fire"],
                "Feu de forêt,Trajectoire ZAN",
                id="several_topics",
            ),
        ],
    )
    def test_with_topics(
        self,
        procedure_status: EventCategory,
        procedure_topics: str,
        expected_result: str,
        client: Client,
        django_assert_num_queries: DjangoAssertNumQueries,
    ) -> None:
        procedure = ProcedureFactory(
            **self._default_procedure_factory_params(procedure_status=procedure_status)
        )
        if procedure_topics:
            topics = Topic.objects.filter(name__in=procedure_topics)
            procedure.topics.add(*topics)

        with django_assert_num_queries(3):
            response = client.get(reverse("api_communes"))

        results = csv_to_json_like(response.content)
        assert results[0]["pc_objets"] == (
            expected_result
            if procedure_status == EventCategory.PUBLICATION_PERIMETRE
            else ""
        )
        assert results[0]["pa_objets"] == (
            expected_result if procedure_status == EventCategory.APPROUVE else ""
        )

    @pytest.mark.parametrize(
        ("event_type", "date_key"),
        [
            pytest.param(
                EventCategory.PORTER_A_CONNAISSANCE_COMPLEMENTAIRE,
                "date_pac_comp",
                id="pac_complementaire",
            ),
            pytest.param(
                EventCategory.PORTER_A_CONNAISSANCE,
                "date_pac",
                id="pac",
            ),
            pytest.param(
                EventCategory.ARRET_DE_PROJET,
                "date_arret_projet",
                id="arret_projet",
            ),
        ],
    )
    @pytest.mark.parametrize(
        ("procedure_status"),
        [
            pytest.param(
                EventCategory.PUBLICATION_PERIMETRE,
                id="ongoing_procedure",
            ),
            pytest.param(
                EventCategory.APPROUVE,
                id="approved_procedure",
            ),
        ],
    )
    def test_dates_pa_pc(
        self,
        event_type: EventCategory,
        date_key: str,
        procedure_status: EventCategory,
        client: Client,
    ) -> None:
        procedure = ProcedureFactory(
            **self._default_procedure_factory_params(procedure_status=procedure_status),
            with_event__date_evenement=datetime.date(2025, 10, 10),
        )
        EventFactory(
            type=EVENT_TYPE_BY_EVENT_CATEGORY[procedure.doc_type][event_type][0],
            date_evenement=datetime.date(2025, 11, 11),
            procedure=procedure,
        )
        response = client.get(reverse("api_communes"))
        results = list(DictReader(response.content.decode().splitlines()))
        assert results[0][f"pc_{date_key}"] == (
            "2025-11-11"
            if procedure_status == EventCategory.PUBLICATION_PERIMETRE
            else ""
        )
        assert results[0][f"pa_{date_key}"] == (
            "2025-11-11" if procedure_status == EventCategory.APPROUVE else ""
        )

    @pytest.mark.parametrize(
        ("event_type", "date_key"),
        [
            pytest.param(
                EventCategory.CARACTERE_EXECUTOIRE,
                "date_executoire",
                id="executoire",
            ),
            pytest.param(
                EventCategory.APPROUVE,
                "date_approbation",
                id="date_approbation",
            ),
        ],
    )
    def test_dates_pa_only(
        self,
        event_type: EventCategory,
        date_key: str,
        client: Client,
    ) -> None:
        procedure = ProcedureFactory(
            **self._default_procedure_factory_params(
                procedure_status=EventCategory.APPROUVE
            ),
            with_event__date_evenement=datetime.date(2025, 10, 10),
        )
        EventFactory(
            type=EVENT_TYPE_BY_EVENT_CATEGORY[procedure.doc_type][event_type][0],
            date_evenement=datetime.date(2025, 11, 11),
            procedure=procedure,
        )
        response = client.get(reverse("api_communes"))
        results = list(DictReader(response.content.decode().splitlines()))
        assert results[0][f"pa_{date_key}"] == "2025-11-11"

    @pytest.mark.parametrize(
        ("event_type", "date_key"),
        [
            pytest.param(
                EventCategory.PRESCRIPTION,
                "date_prescription",
                id="prescription",
            ),
        ],
    )
    def test_dates_pc_only(
        self,
        event_type: EventCategory,
        date_key: str,
        client: Client,
    ) -> None:
        procedure = ProcedureFactory(
            **self._default_procedure_factory_params(
                procedure_status=EventCategory.PUBLICATION_PERIMETRE
            ),
            with_event__date_evenement=datetime.date(2025, 10, 10),
        )
        EventFactory(
            type=EVENT_TYPE_BY_EVENT_CATEGORY[procedure.doc_type][event_type][0],
            date_evenement=datetime.date(2025, 11, 11),
            procedure=procedure,
        )
        response = client.get(reverse("api_communes"))
        results = list(DictReader(response.content.decode().splitlines()))
        assert results[0][f"pc_{date_key}"] == "2025-11-11"

    ###############################################################################
    ################################ FILTERS ######################################
    ###############################################################################
    @pytest.mark.parametrize(
        ("avant_value", "approval_date", "expected_procedure_is_approved"),
        [
            pytest.param(
                "2026-07-05", "2026-07-04", True, id="avant_is_after_approval_date"
            ),
            pytest.param(
                "2026-07-04", "2026-07-04", True, id="avant_is_same_as_approval_date"
            ),
            pytest.param(
                "2026-07-02", "2026-07-04", False, id="avant_is_before_approval_date"
            ),
            pytest.param("", "2026-07-04", True, id="no_filter_approval_date_in_past"),
            pytest.param(
                "", "2026-07-20", False, id="no_filter_approval_date_in_future"
            ),
        ],
    )
    @freeze_time("2026-07-08")
    def test_avant_filter(
        self,
        client: Client,
        django_assert_num_queries: DjangoAssertNumQueries,
        avant_value: bool,  # noqa: FBT001
        approval_date: datetime.date,
        expected_procedure_is_approved: int,
    ) -> None:
        procedure = ProcedureFactory(**self._default_procedure_factory_params())
        procedure.event_set.create(
            type=EVENT_TYPE_BY_EVENT_CATEGORY[procedure.doc_type][
                EventCategory.APPROUVE
            ][0],
            date_evenement=approval_date,  # 2026-07-04
        )
        with django_assert_num_queries(3):
            response = client.get(f"{reverse('api_communes')}?avant={avant_value}")
        results = csv_to_json_like(response.content)
        assert len(results) == 1
        if expected_procedure_is_approved:
            assert results[0]["pa_docurba_id"] == str(procedure.pk)
        else:
            assert results[0]["pc_docurba_id"] == str(procedure.pk)

    ###############################################################################
    ################################ Codes état ###################################
    ###############################################################################

    @pytest.mark.parametrize(
        ("with_ongoing", "with_approved"),
        [
            pytest.param(
                False,
                False,
                id="no_procedure",
            ),
            pytest.param(
                True,
                False,
                id="ongoing_procedure",
            ),
            pytest.param(
                False,
                True,
                id="approved_procedure",
            ),
            pytest.param(
                True,
                True,
                id="ongoing_and_approved",
            ),
        ],
    )
    @pytest.mark.parametrize(
        ("doc_type", "expected_code"),
        [
            (TypeDocument.CC, "1"),
            (TypeDocument.POS, "2"),
            (TypeDocument.PLU, "3"),
        ],
    )
    def test_code_etat_simplifie(
        self,
        client: Client,
        with_ongoing: bool,  # noqa: FBT001
        with_approved: bool,  # noqa: FBT001
        doc_type: TypeDocument,
        expected_code: str,
    ) -> None:
        perimetre = [CommuneFactory()]
        if with_ongoing:
            ProcedureFactory(
                **self._default_procedure_factory_params(
                    perimetre=perimetre,
                    procedure_status=EventCategory.PUBLICATION_PERIMETRE,
                )
                | {"doc_type": doc_type},
            )
        if with_approved:
            ProcedureFactory(
                **self._default_procedure_factory_params(
                    perimetre=perimetre, procedure_status=EventCategory.APPROUVE
                )
                | {"doc_type": doc_type},
            )
        response = client.get(reverse("api_communes"))
        results = csv_to_json_like(response.content)
        if with_approved:
            assert results[0]["plan_code_etat_simplifie"][0] == expected_code
            assert results[0]["plan_code_etat_complet"][0] == expected_code
        else:
            assert results[0]["plan_code_etat_simplifie"][0] == "9"
            assert results[0]["plan_code_etat_complet"][0] == "9"

        if with_ongoing and doc_type != TypeDocument.POS:
            assert results[0]["plan_code_etat_simplifie"][1] == expected_code
            assert results[0]["plan_code_etat_complet"][2] == expected_code
        else:
            assert results[0]["plan_code_etat_simplifie"][1] == "9"
            assert results[0]["plan_code_etat_complet"][2] == "9"
        assert results[0]["plan_libelle_code_etat_simplifie"]
        assert results[0]["plan_libelle_code_etat_complet"]

    def test_code_etat_complet_pas_procedure(self, client: Client) -> None:
        CommuneFactory()
        response = client.get(reverse("api_communes"))
        results = csv_to_json_like(response.content)
        assert results[0]["plan_code_etat_complet"][1] == "9"
        assert results[0]["plan_code_etat_complet"][3] == "9"

    def test_code_etat_complet_competence_commune(self, client: Client) -> None:
        collectivite_porteuse = CommuneFactory()
        perimetre = [collectivite_porteuse]
        ProcedureFactory(
            **self._default_procedure_factory_params(
                collectivite_porteuse=collectivite_porteuse, perimetre=perimetre
            )
        )
        ProcedureFactory(
            **self._default_procedure_factory_params(
                collectivite_porteuse=collectivite_porteuse,
                perimetre=perimetre,
                procedure_status=EventCategory.APPROUVE,
            )
        )
        response = client.get(reverse("api_communes"))
        results = csv_to_json_like(response.content)
        assert results[0]["plan_code_etat_complet"][1] == "1"
        assert results[0]["plan_code_etat_complet"][3] == "1"
        assert results[0]["plan_libelle_code_etat_complet"]

    def test_code_etat_complet_interco_competence_epci(self, client: Client) -> None:
        perimetre = [CommuneFactory(), CommuneFactory()]
        collectivite_porteuse = CollectiviteFactory()
        ProcedureFactory(
            **self._default_procedure_factory_params(
                collectivite_porteuse=collectivite_porteuse, perimetre=perimetre
            )
        )
        ProcedureFactory(
            **self._default_procedure_factory_params(
                collectivite_porteuse=collectivite_porteuse,
                perimetre=perimetre,
                procedure_status=EventCategory.APPROUVE,
            )
        )
        response = client.get(reverse("api_communes"))
        results = csv_to_json_like(response.content)
        assert results[0]["plan_code_etat_complet"][1] == "2"
        assert results[0]["plan_code_etat_complet"][3] == "2"
        assert results[0]["plan_libelle_code_etat_complet"]

    def test_code_etat_sectoriel_competence_epci(self, client: Client) -> None:
        perimetre = [CommuneFactory(), CommuneFactory()]
        collectivite_porteuse = CollectiviteFactory(
            with_members=True, with_members__list=[*perimetre, CommuneFactory()]
        )
        ProcedureFactory(
            **self._default_procedure_factory_params(
                collectivite_porteuse=collectivite_porteuse, perimetre=perimetre
            )
        )
        ProcedureFactory(
            **self._default_procedure_factory_params(
                collectivite_porteuse=collectivite_porteuse,
                perimetre=perimetre,
                procedure_status=EventCategory.APPROUVE,
            )
        )
        response = client.get(reverse("api_communes"))
        results = csv_to_json_like(response.content)
        assert results[0]["plan_code_etat_complet"][1] == "3"
        assert results[0]["plan_code_etat_complet"][3] == "3"
        assert results[0]["plan_libelle_code_etat_complet"]

    def test_code_competence_epci(self, client: Client) -> None:
        perimetre = [CommuneFactory()]
        collectivite_porteuse = CollectiviteFactory()
        ProcedureFactory(
            **self._default_procedure_factory_params(
                collectivite_porteuse=collectivite_porteuse, perimetre=perimetre
            )
        )
        ProcedureFactory(
            **self._default_procedure_factory_params(
                collectivite_porteuse=collectivite_porteuse,
                perimetre=perimetre,
                procedure_status=EventCategory.APPROUVE,
            )
        )
        response = client.get(reverse("api_communes"))
        results = csv_to_json_like(response.content)
        assert results[0]["plan_code_etat_complet"][1] == "4"
        assert results[0]["plan_code_etat_complet"][3] == "4"
        assert results[0]["plan_libelle_code_etat_complet"]

    def test_code_3234(self, client: Client) -> None:
        perimetre = [CommuneFactory()]
        collectivite_porteuse = CollectiviteFactory()
        ProcedureFactory(
            **self._default_procedure_factory_params(
                collectivite_porteuse=collectivite_porteuse,
                perimetre=[*perimetre, CommuneFactory(code_insee="30189")],
                procedure_status=EventCategory.APPROUVE,
            )
        )
        ProcedureFactory(
            **self._default_procedure_factory_params(
                collectivite_porteuse=collectivite_porteuse, perimetre=perimetre
            )
        )
        response = client.get(reverse("api_communes"))
        results = csv_to_json_like(response.content)
        assert results[0]["plan_code_etat_complet"] == "3234"
        assert results[0]["plan_libelle_code_etat_complet"]

    def test_code_3214(self, client: Client) -> None:
        perimetre = [CommuneFactory()]
        collectivite_porteuse = CollectiviteFactory()
        ProcedureFactory(
            **self._default_procedure_factory_params(
                collectivite_porteuse=collectivite_porteuse,
                perimetre=[*perimetre, CommuneFactory(code_insee="30189")],
                procedure_status=EventCategory.APPROUVE,
            )
        )
        ProcedureFactory(
            **self._default_procedure_factory_params(
                collectivite_porteuse=collectivite_porteuse, perimetre=perimetre
            )
            | {"doc_type": TypeDocument.CC}
        )
        response = client.get(reverse("api_communes"))
        results = csv_to_json_like(response.content)
        assert results[0]["plan_code_etat_complet"] == "3214"
        assert results[0]["plan_libelle_code_etat_complet"]


@pytest.mark.django_db
class TestAPIScots:
    def _default_procedure_factory_params(
        self,
        perimetre: list | None = None,
        collectivite: Collectivite | None = None,
        procedure_status: EventCategory | None = None,
    ) -> dict[str, Any]:
        if perimetre is None:
            perimetre = [CommuneFactory()]
        if not collectivite:
            collectivite = CollectiviteFactory(
                with_members=True, with_members__list=perimetre
            )
        params = {
            "doc_type": TypeDocument.SCOT,
            "collectivite_porteuse": collectivite,
            "with_perimetre": perimetre,
            "with_event": True,
        }
        if procedure_status:
            params["with_event__category"] = procedure_status
        return params

    def _create_event(
        self,
        category: EventCategory,
        procedure: Procedure,
        date: datetime.date | None = None,
    ) -> None:
        return procedure.event_set.create(
            type=EVENT_TYPE_BY_EVENT_CATEGORY[procedure.doc_type][category][0],
            date_evenement=date or datetime.date(2025, 11, 11),
        )

    def test_nominal(self, client: Client, snapshot: SnapshotAssertion) -> None:
        commune = CommuneFactory(for_snapshot=True)
        collectivite_porteuse = CollectiviteFactory(for_snapshot=True)
        # pc_*
        # pc_date_perscription
        ongoing_procedure = ProcedureFactory(
            **self._default_procedure_factory_params(
                perimetre=[commune],
                collectivite=collectivite_porteuse,
                procedure_status=EventCategory.PRESCRIPTION,
            ),
            with_event__date_evenement=datetime.date(2025, 10, 10),
            for_snapshot=True,
        )
        # pa_date_prescription
        self._create_event(
            procedure=ongoing_procedure,
            category=EventCategory.PUBLICATION_PERIMETRE,
            date=datetime.date(2025, 11, 11),
        )
        # pa_date_prescription
        self._create_event(
            procedure=ongoing_procedure,
            category=EventCategory.ARRET_DE_PROJET,
            date=datetime.date(2025, 12, 11),
        )
        # pa_*
        # dates: pa_date_approbation, pa_annee_approbation
        approved_procedure = ProcedureFactory(
            **self._default_procedure_factory_params(
                perimetre=[commune],
                collectivite=collectivite_porteuse,
                procedure_status=EventCategory.APPROUVE,
            ),
            with_event__date_evenement=datetime.date(2026, 1, 1),
            pk=uuid.UUID("1cd65b57-7027-4aa5-8d19-5e1baf8d6f10"),
        )
        # pa_date_prescription
        self._create_event(
            procedure=approved_procedure,
            category=EventCategory.PRESCRIPTION,
            date=datetime.date(2025, 9, 11),
        )
        # pa_date_publication_perimetre
        self._create_event(
            procedure=approved_procedure,
            category=EventCategory.PUBLICATION_PERIMETRE,
            date=datetime.date(2025, 10, 11),
        )

        # pa_date_arret_projet
        self._create_event(
            procedure=approved_procedure,
            category=EventCategory.ARRET_DE_PROJET,
            date=datetime.date(2025, 11, 11),
        )

        response = client.get(reverse("api_scots"))
        assert csv_to_json_like(response.content) == snapshot()

    def test_nb_queries(
        self, client: Client, django_assert_num_queries: DjangoAssertNumQueries
    ) -> None:
        for _ in range(2):
            ProcedureFactory(**self._default_procedure_factory_params())
            with django_assert_num_queries(6):
                response = client.get(reverse("api_scots"))
        assert response.status_code == 200

    @pytest.mark.xfail(
        reason="procedure.statut is CADUC when FIN ECHEANCE category event is set"
    )
    def test_date_fin_echeance(
        self,
        client: Client,
    ) -> None:
        procedure = ProcedureFactory(
            **self._default_procedure_factory_params(
                procedure_status=EventCategory.FIN_ECHEANCE
            ),
            with_event__date_evenement=datetime.date(2025, 10, 10),
        )
        self._create_event(
            procedure=procedure,
            type=EventCategory.APPROUVE,
            date=datetime.date(2025, 11, 11),
        )
        response = client.get(f"{reverse('api_scots')}")
        results = csv_to_json_like(response.content)
        assert results[0]["pa_date_fin_echeance"] == "2025-10-10"

    @pytest.mark.parametrize(
        "procedure_status",
        [
            pytest.param(EventCategory.APPROUVE, id="approuve"),
            pytest.param(EventCategory.PUBLICATION_PERIMETRE, id="en_cours"),
        ],
    )
    @pytest.mark.parametrize("nb_communes", [3, 0])
    def test_nombre_communes(
        self,
        client: Client,
        django_assert_num_queries: DjangoAssertNumQueries,
        nb_communes: int,
        procedure_status: dict[str, EventCategory],
    ) -> None:
        perimetre = CommuneFactory.create_batch(nb_communes)
        ProcedureFactory(
            **self._default_procedure_factory_params(
                procedure_status=procedure_status, perimetre=perimetre
            ),
        )

        with django_assert_num_queries(6 if nb_communes else 4):
            response = client.get(reverse("api_scots"))
        result = csv_to_json_like(response.content)
        if procedure_status == EventCategory.APPROUVE and nb_communes != 0:
            assert result[0]["pa_nombre_communes"] == str(nb_communes)
        elif procedure_status == EventCategory.PUBLICATION_PERIMETRE:
            assert result[0]["pc_nombre_communes"] == str(nb_communes)

    @pytest.mark.parametrize(
        "procedure_status",
        [
            pytest.param(EventCategory.APPROUVE, id="approuve"),
            pytest.param(EventCategory.PUBLICATION_PERIMETRE, id="en_cours"),
        ],
    )
    def test_noserie_procedure(
        self,
        client: Client,
        procedure_status: dict[str, EventCategory],
    ) -> None:
        ProcedureFactory(
            **self._default_procedure_factory_params(procedure_status=procedure_status),
            from_sudocuh="12345",
        )

        response = client.get(reverse("api_scots"))
        result = csv_to_json_like(response.content)
        if procedure_status == EventCategory.APPROUVE:
            assert result[0]["pa_noserie_procedure"] == "12345"
        elif procedure_status == EventCategory.PUBLICATION_PERIMETRE:
            assert result[0]["pc_noserie_procedure"] == "12345"

    @pytest.mark.parametrize(
        "procedure_status",
        [
            pytest.param(EventCategory.APPROUVE, id="approuve"),
            pytest.param(EventCategory.PUBLICATION_PERIMETRE, id="en_cours"),
        ],
    )
    def test_is_interdepartemental(
        self,
        client: Client,
        procedure_status: dict[str, EventCategory],
    ) -> None:
        perimetre = [
            CommuneFactory(departement__code_insee="84"),
            CommuneFactory(departement__code_insee="13"),
        ]
        ProcedureFactory(
            **self._default_procedure_factory_params(
                procedure_status=procedure_status, perimetre=perimetre
            ),
        )

        response = client.get(reverse("api_scots"))
        result = csv_to_json_like(response.content)
        if procedure_status == EventCategory.APPROUVE:
            assert result[0]["pa_scot_interdepartement"] == "True"
        elif procedure_status == EventCategory.PUBLICATION_PERIMETRE:
            assert result[0]["pc_scot_interdepartement"] == "True"

    @pytest.mark.parametrize(
        ("procedure_status", "expected_filled_key", "expected_empty_key"),
        [
            pytest.param(
                EventCategory.PUBLICATION_PERIMETRE,
                "pc_objets",
                "pa_objets",
                id="ongoing_procedure",
            ),
            pytest.param(
                EventCategory.APPROUVE,
                "pa_objets",
                "pc_objets",
                id="approved_procedure",
            ),
        ],
    )
    @pytest.mark.parametrize(
        ("procedure_topics", "expected_result"),
        [
            pytest.param("", "", id="no_topic"),
            pytest.param(["zan"], "Trajectoire ZAN", id="one_topic"),
            pytest.param(
                ["zan", "forest_fire"],
                "Feu de forêt,Trajectoire ZAN",
                id="several_topics",
            ),
        ],
    )
    @pytest.mark.django_db
    def test_with_topics(
        self,
        procedure_status: EventCategory,
        expected_filled_key: str,
        expected_empty_key: str,
        procedure_topics: str,
        expected_result: str,
        client: Client,
        django_assert_num_queries: DjangoAssertNumQueries,
    ) -> None:
        procedure = ProcedureFactory(
            **self._default_procedure_factory_params(
                procedure_status=procedure_status,
            ),
        )

        if procedure_topics:
            topics = Topic.objects.filter(name__in=procedure_topics)
            procedure.topics.add(*topics)

        with django_assert_num_queries(6):
            response = client.get(reverse("api_scots"))

        results = csv_to_json_like(response.content)
        assert results[0][expected_filled_key] == expected_result
        assert results[0][expected_empty_key] == ""

    @pytest.mark.parametrize("commune_type", TypeCollectivite.communes())
    def test_communes_types(
        self,
        client: Client,
        commune_type: TypeCollectivite,
    ) -> None:
        perimetre = [CommuneFactory(type=commune_type)]
        procedure = ProcedureFactory(
            **self._default_procedure_factory_params(perimetre=perimetre),
        )
        response = client.get(reverse("api_scots"))
        results = csv_to_json_like(response.content)
        assert len(results) == 1
        assert (
            results[0]["scot_codecollectivite"] == procedure.collectivite_porteuse.siren
        )

    ###############################################################################
    ################################ FILTERS ######################################
    ###############################################################################
    @pytest.mark.parametrize(("with_filter", "expected_lines"), [(False, 2), (True, 1)])
    def test_departement_filter(
        self,
        client: Client,
        with_filter: bool,  # noqa: FBT001
        expected_lines: int,
    ) -> None:
        commune_a = CommuneFactory(departement__code_insee="13")
        commune_b = CommuneFactory(departement__code_insee="84")
        collectivite_porteuse_a = CollectiviteFactory(
            departement__code_insee="13",
            with_members=True,
            with_members__list=[commune_a],
        )
        collectivite_porteuse_b = CollectiviteFactory(
            departement__code_insee="84",
            with_members=True,
            with_members__list=[commune_b],
        )
        ProcedureFactory(
            collectivite_porteuse=collectivite_porteuse_a,
            doc_type=TypeDocument.SCOT,
            with_event=True,
            with_event__category=EventCategory.APPROUVE,
            with_perimetre=[commune_a],
        )
        ProcedureFactory(
            collectivite_porteuse=collectivite_porteuse_b,
            doc_type=TypeDocument.SCOT,
            with_event=True,
            with_event__category=EventCategory.APPROUVE,
            with_perimetre=[commune_b],
        )

        filtre = {}
        if with_filter:
            filtre = {"departement": collectivite_porteuse_a.departement.code_insee}
        response = client.get(reverse("api_scots"), filtre)
        results = csv_to_json_like(response.content)
        assert len(results) == expected_lines
        if with_filter:
            assert results[0]["scot_codecollectivite"] == collectivite_porteuse_a.siren

    @pytest.mark.parametrize(
        ("avant_value", "approval_date", "expected_procedure_is_approved"),
        [
            pytest.param(
                "2026-07-05", "2026-07-04", True, id="avant_is_after_approval_date"
            ),
            pytest.param(
                "2026-07-04", "2026-07-04", True, id="avant_is_same_as_approval_date"
            ),
            pytest.param(
                "2026-07-02", "2026-07-04", False, id="avant_is_before_approval_date"
            ),
            pytest.param("", "2026-07-04", True, id="no_filter_approval_date_in_past"),
            pytest.param(
                "", "2026-07-20", False, id="no_filter_approval_date_in_future"
            ),
        ],
    )
    @freeze_time("2026-07-08")
    def test_avant_filter(
        self,
        client: Client,
        django_assert_num_queries: DjangoAssertNumQueries,
        avant_value: bool,  # noqa: FBT001
        approval_date: datetime.date,
        expected_procedure_is_approved: int,
    ) -> None:
        procedure = ProcedureFactory(
            **self._default_procedure_factory_params(),
        )
        procedure.event_set.create(
            type=EVENT_TYPE_BY_EVENT_CATEGORY[procedure.doc_type][
                EventCategory.APPROUVE
            ][0],
            date_evenement=approval_date,  # 2026-07-04
        )
        with django_assert_num_queries(6):
            response = client.get(f"{reverse('api_scots')}?avant={avant_value}")
        results = csv_to_json_like(response.content)
        assert len(results) == 1
        if expected_procedure_is_approved:
            assert results[0]["pa_id"] == str(procedure.pk)
        else:
            assert results[0]["pc_id"] == str(procedure.pk)
