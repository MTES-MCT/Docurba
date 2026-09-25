# https://pipedrive.readme.io/docs/pipedrive-api-v2

# Currently the following APIs are available as v2:

# Activities API
# Deals API
# Deal Followers API
# Deal Products API
# Fields API (ActivityFields, DealFields, OrganizationFields, PersonFields, ProductFields)
# Organizations API
# Organization Followers API
# Persons API
# Person Followers API
# Products API
# Product Followers API
# Product Variations API
# Pipelines and Stages API
# User Followers API
# Search API

import dataclasses
import logging
from typing import Self

import httpx
from django.conf import settings

logger = logging.getLogger(__name__)


class PipedriveHTTPError(Exception):
    pass


@dataclasses.dataclass(frozen=True, kw_only=True, slots=True)
class Organization:
    pass


@dataclasses.dataclass(frozen=True, kw_only=True, slots=True)
class Deal:
    pass


class PipedriveApiClient:
    def __init__(self) -> None:
        self.client = httpx.Client(
            base_url=settings.PIPEDRIVE_URL,
            headers={"x-api-token": settings.PIPEDRIVE_TOKEN},
        )

    def __enter__(self) -> Self:
        self.client.__enter__()
        return self

    def __exit__(self, type, value, traceback) -> None:  # noqa: A002, ANN001
        self.client.__exit__(type, value, traceback)

    def _request(
        self, route: str, params: dict, *, method: str = "GET"
    ) -> httpx.Response:
        try:
            response = self.client.request(
                method, route, params=params, timeout=httpx.Timeout(5, read=60)
            ).raise_for_status()
        except httpx.HTTPError as exc:
            logger.exception("Pipedrive exception")
                method,
                route,
                params=params,
                data=data,
                timeout=httpx.Timeout(5, read=60),

        return response

    def search_organizations(self, term: str, **params: dict) -> list | None:
        # https://developers.pipedrive.com/docs/api/v1/Organizations
        params = {
            "term": term,  # mandatory
        } | params
        results = self._request("/organizations/search", params).json()
        if not results:
            return None
        if "data" not in results or "items" not in results["data"]:
            raise KeyError
        return results["data"]["items"]

    def deals(self, **params: dict) -> dict | None:
        # https://developers.pipedrive.com/docs/api/v1/Deals
        results = self._request("/deals", params).json()
        if not results:
            return None
        if "data" not in results:
            raise KeyError
        return results["data"]

    def update_deal(self, deal_id: int, **params: dict) -> dict | None:
        # https://developers.pipedrive.com/docs/api/v1/Deals
        response = self._request(f"/deals/{deal_id}", params, method="PATCH").json()
        if "data" not in response:
            raise KeyError
        return response["data"]

    def find_organization_by_name(self, name: str) -> dict | None:
        results = self.search_organizations(term=name, fields=["name"])
        if not results:
            return []
        if "item" not in results[0]:
            raise KeyError
        return results[0]["item"]

    def get_organization_deals(self, organization_id: str) -> dict | None:
        return self.deals(org_id=organization_id)
