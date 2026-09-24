from unittest import mock

import pytest
import tenacity
from respx import MockRouter

from docurba.utils.consumed_apis import pipedrive
from tests.utils.consumed_apis import pipedrive_mocks


def test_search_organizations(respx_mock: MockRouter) -> None:
    respx_mock.get(
        pipedrive_mocks.SEARCH_ORGANIZATIONS_BY_NAME[0],
    ).respond(200, json=pipedrive_mocks.SEARCH_ORGANIZATIONS_BY_NAME[1])
    with pipedrive.PipedriveApiClient() as client:
        result = client.search_organizations(term="DDT 30", fields=["name"])
    assert result == pipedrive_mocks.SEARCH_ORGANIZATIONS_BY_NAME[1]["data"]["items"]


def test_search_organizations_no_result(respx_mock: MockRouter) -> None:
    respx_mock.get(
        pipedrive_mocks.SEARCH_ORGANIZATIONS_BY_NAME[0],
    ).respond(
        200,
        json={
            "success": True,
            "data": {"items": []},
            "additional_data": {"next_cursor": None},
        },
    )
    with pipedrive.PipedriveApiClient() as client:
        result = client.search_organizations(term="DDT 30", fields=["name"])
    assert result == []


def test_find_organization_by_name(respx_mock: MockRouter) -> None:
    respx_mock.get(
        pipedrive_mocks.SEARCH_ORGANIZATIONS_BY_NAME[0],
    ).respond(200, json=pipedrive_mocks.SEARCH_ORGANIZATIONS_BY_NAME[1])

    with pipedrive.PipedriveApiClient() as client:
        result = client.find_organization_by_name(name="DDT 30")
    assert (
        result
        == pipedrive_mocks.SEARCH_ORGANIZATIONS_BY_NAME[1]["data"]["items"][0]["item"]
    )


def test_get_organization_deals(respx_mock: MockRouter) -> None:
    respx_mock.get(
        pipedrive_mocks.GET_DEAL_ORG_ID_1[0],
    ).respond(
        200,
        json=pipedrive_mocks.GET_DEAL_ORG_ID_1[1],
    )
    with pipedrive.PipedriveApiClient() as client:
        result = client.get_organization_deals(organization_id=1)
    assert result == pipedrive_mocks.GET_DEAL_ORG_ID_1[1]["data"]


def test_update_deal(respx_mock: MockRouter) -> None:
    respx_mock.patch(pipedrive_mocks.PATCH_DEAL_ID_1[0]).respond(
        200,
        json=pipedrive_mocks.PATCH_DEAL_ID_1[1],
    )
    with pipedrive.PipedriveApiClient() as client:
        result = client.update_deal(deal_id=1)
    assert result == pipedrive_mocks.PATCH_DEAL_ID_1[1]["data"]


@pytest.mark.parametrize(
    ("endpoint", "method", "method_args"),
    [
        pytest.param(
            "organizations/search?term=DDT%2001&fields=name",
            "find_organization_by_name",
            {"name": "DDT 01"},
            id="find_organization_by_name",
        ),
        pytest.param(
            "organizations/search?term=DDT%2001&fields=name",
            "search_organizations",
            {"term": "DDT 01", "fields": "name"},
            id="search_organizations",
        ),
    ],
)
def test_no_result__item_expected_in_dict(
    respx_mock: MockRouter, endpoint: str, method: str, method_args: dict
) -> None:
    respx_mock.get(
        f"https://fake-pipedrive.fr/{endpoint}",
    ).respond(
        200,
        json={
            "success": True,
            "data": {"items": []},
            "additional_data": {"next_cursor": None},
        },
    )
    with pipedrive.PipedriveApiClient() as client:
        result = getattr(client, method)(**method_args)
    assert result == []


@pytest.mark.parametrize(
    ("endpoint", "method", "method_args"),
    [
        pytest.param(
            "deals?org_id=1",
            "deals",
            {"org_id": 1},
            id="deals",
        ),
        pytest.param(
            "deals?org_id=1",
            "get_organization_deals",
            {"organization_id": 1},
            id="get_organization_deals",
        ),
    ],
)
def test_no_result(
    respx_mock: MockRouter, endpoint: str, method: str, method_args: dict
) -> None:
    respx_mock.get(
        f"https://fake-pipedrive.fr/{endpoint}",
    ).respond(
        200,
        json={
            "success": True,
            "data": [],
            "additional_data": {"next_cursor": None},
        },
    )
    with pipedrive.PipedriveApiClient() as client:
        result = getattr(client, method)(**method_args)
    assert result == []


def test_not_found_error(respx_mock: MockRouter) -> None:
    respx_mock.patch(
        "https://fake-pipedrive.fr/deals/1",
    ).respond(
        404, json={"success": False, "error": "Deal not found", "code": "ERR_NOT_FOUND"}
    )
    with (
        pipedrive.PipedriveApiClient() as client,
        pytest.raises(pipedrive.PipedriveNotFoundError),
    ):
        client.update_deal(deal_id=1)


def test_field_validation_error(respx_mock: MockRouter) -> None:
    # validation failed.
    respx_mock.patch(
        "https://fake-pipedrive.fr/deals/1",
    ).respond(
        400,
        json={
            "success": False,
            "error": "Validation failed: owner_id: User not found or not accessible.",
            "code": "ERR_SCHEMA_VALIDATION_FAILED",
        },
    )
    with (
        pipedrive.PipedriveApiClient() as client,
        pytest.raises(pipedrive.PipedriveFieldValidationdError),
    ):
        client.update_deal(deal_id=1)


@pytest.mark.parametrize("status_code", [408, 409, 429, 503])
def test_pipedrive_tenacity_error_not_fixed(
    respx_mock: MockRouter, status_code: int
) -> None:
    respx_mock.patch(
        "https://fake-pipedrive.fr/deals/1",
    ).respond(
        status_code,
        json={},
    )
    with (
        mock.patch("tenacity.nap.time.sleep", mock.MagicMock()),
        pipedrive.PipedriveApiClient() as client,
        pytest.raises(tenacity.RetryError),
    ):
        client.update_deal(deal_id=1)
