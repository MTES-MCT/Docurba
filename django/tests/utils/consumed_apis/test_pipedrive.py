
# import tenacity

from docurba.utils.consumed_apis.pipedrive import PipedriveApiClient


def test_search_organizations(respx_mock) -> None:
    expected = [
        {
            "result_score": 0.35513002,
            "item": {
                "id": 1,
                "type": "organization",
                "name": "DDT 01",
                "address": None,
                "visible_to": 3,
                "owner": {"id": 123456789},
                "custom_fields": ["AuRA"],
                "notes": ["Some personal notes"],
            },
        }
    ]
    respx_mock.get(
        "https://fake-pipedrive.fr/organizations/search?term=DDT%2001&fields=name",
    ).respond(
        200,
        json={
            "success": True,
            "data": {"items": expected},
            "additional_data": {"next_cursor": None},
        },
    )
    with PipedriveApiClient() as client:
        result = client.search_organizations(term="DDT 01", fields=["name"])
    assert result == expected


def test_search_organizations_no_result(respx_mock) -> None:
    respx_mock.get(
        "https://fake-pipedrive.fr/organizations/search?term=DDT%2001&fields=name",
    ).respond(
        200,
        json={
            "success": True,
            "data": {"items": []},
            "additional_data": {"next_cursor": None},
        },
    )
    with PipedriveApiClient() as client:
        result = client.search_organizations(term="DDT 01", fields=["name"])
    assert result == []


def test_find_organization_by_name(respx_mock) -> None:
    expected = {
        "id": 1,
        "type": "organization",
        "name": "DDT 01",
        "address": None,
        "visible_to": 3,
        "owner": {"id": 123456789},
        "custom_fields": ["AuRA"],
        "notes": ["Some personal notes"],
    }

    respx_mock.get(
        "https://fake-pipedrive.fr/organizations/search?term=DDT%2001&fields=name",
    ).respond(
        200,
        json={
            "success": True,
            "data": {
                "items": [
                    {
                        "result_score": 0.35513002,
                        "item": expected,
                    }
                ]
            },
            "additional_data": {"next_cursor": None},
        },
    )
    with PipedriveApiClient() as client:
        result = client.find_organization_by_name(name="DDT 01")
    assert result == expected


def test_find_organization_by_name_no_result(respx_mock) -> None:
    respx_mock.get(
        "https://fake-pipedrive.fr/organizations/search?term=DDT%2001&fields=name",
    ).respond(
        200,
        json={
            "success": True,
            "data": {"items": []},
            "additional_data": {"next_cursor": None},
        },
    )
    with PipedriveApiClient() as client:
        result = client.find_organization_by_name(name="DDT 01")
    assert result is None


def test_get_organization_deals(respx_mock) -> None:
    expected = [
        {
            "id": 51,
            "title": "🌐 📝 01 Ain",
            "creator_user_id": 123456789,
            "value": 0.0,
            "person_id": 1111,
            "org_id": 1,
            "stage_id": 77,
            "currency": "EUR",
            "add_time": "2024-08-18T13:39:22Z",
            "update_time": "2026-07-01T16:28:13Z",
            "status": "open",
            "probability": None,
            "lost_reason": None,
            "visible_to": 3,
            "close_time": None,
            "pipeline_id": 8,
            "won_time": None,
            "lost_time": None,
            "stage_change_time": "2025-10-16T14:06:23Z",
            "local_won_date": None,
            "local_lost_date": None,
            "local_close_date": None,
            "expected_close_date": None,
            "custom_fields": {
                "62964f49dba625be71f3a403652d37c8fa1b93f6": None,
                "51228cc35804435b6db33c9860c9445bee15b206": None,
            },
            "owner_id": 123456789,
            "label_ids": [],
            "is_deleted": False,
            "origin": "ManuallyCreated",
            "origin_id": None,
            "channel": None,
            "channel_id": None,
            "acv": None,
            "arr": None,
            "mrr": None,
            "is_archived": False,
            "archive_time": None,
        }
    ]

    respx_mock.get(
        "https://fake-pipedrive.fr/deals?org_id=1",
    ).respond(
        200,
        json={
            "success": True,
            "data": expected,
            "additional_data": {"next_cursor": None},
        },
    )
    with PipedriveApiClient() as client:
        result = client.get_organization_deals(organization_id=1)
    assert result == expected
