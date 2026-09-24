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

# TODO: add tenacity

import dataclasses
import logging

import httpx
from django.conf import settings

logger = logging.getLogger(__name__)


class PipedriveException(Exception):
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
            base_url=settings.PIPEDRIVE_BASE_URL,
            headers={"x-api-token": settings.PIPEDRIVE_TOKEN},
        )

    def __enter__(self):
        self.client.__enter__()
        return self

    def __exit__(self, type, value, traceback):
        self.client.__exit__(type, value, traceback)

    def _request(self, route, params, *, method="GET") -> httpx.Response:
        try:
            response = self.client.request(
                method, route, params=params, timeout=httpx.Timeout(5, read=60)
            ).raise_for_status()
        except httpx.HTTPError as exc:
            logger.exception("pipedrive exception")
            raise PipedriveException from exc

        return response

    def search_organizations(self, term, **params) -> list:
        # https://developers.pipedrive.com/docs/api/v1/Organizations
        params = {
            "term": term,  # mandatory
        } | params
        return self._request("/organizations/search", params).json()["data"]["items"]

    def find_organization_by_name(self, name: str) -> dict:
        results = self.search_organizations(term=name, fields=["name"])
        return results[0]["item"] if results else None

    def deals(self, **params):
        # https://developers.pipedrive.com/docs/api/v1/Deals
        return self._request("/deals", params).json()

    def get_organization_deals(self, organization_id):
        results = self.deals(org_id=organization_id)
        return results["data"] if results else None

    def update_deal(self, deal_id, **params) -> None:
        # https://developers.pipedrive.com/docs/api/v1/Deals
        return self._request("/organizations", params, method="PATCH").json()
