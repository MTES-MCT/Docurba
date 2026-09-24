# https://pipedrive.readme.io/docs/pipedrive-api-v2
import logging
from typing import Self

import httpx
import tenacity
from django.conf import settings

logger = logging.getLogger(__name__)


class PipedriveHTTPError(Exception):
    pass


class PipedriveRateLimitError(PipedriveHTTPError):
    pass


class PipedriveTimeOutError(PipedriveHTTPError):
    pass


class PipedriveNotFoundError(PipedriveHTTPError):
    pass


class PipedriveFieldValidationdError(PipedriveHTTPError):
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

    @tenacity.retry(
        stop=tenacity.stop_after_attempt(10),
        wait=tenacity.wait_fixed(1),
        retry=tenacity.retry_if_exception_type(
            (PipedriveRateLimitError, PipedriveTimeOutError)
        ),
    )
    def _request(
        self,
        route: str,
        params: dict | None = None,
        data: dict | None = None,
        method: str = "GET",
    ) -> httpx.Response:
        try:
            response = self.client.request(
                method,
                route,
                params=params or None,
                json=data or None,
                timeout=httpx.Timeout(5, read=60),
            ).raise_for_status()
        except httpx.HTTPStatusError as exc:
            logger.exception("Pipedrive HTTPStatusError")
            match exc.response.status_code:
                case 400:
                    error_message = exc.response.json()["error"]
                    raise PipedriveFieldValidationdError(error_message) from exc
                case 404:
                    error_message = exc.response.json()["error"]
                    raise PipedriveNotFoundError(error_message) from exc
                case 429:
                    # https://pipedrive.readme.io/docs/core-api-concepts-rate-limiting
                    # We could use the Retry-After header to set a retry delay
                    # but it's not really possible with tenacity.
                    message = "Rate limiting error"
                    raise PipedriveRateLimitError(message) from exc
                case 408 | 409 | 503:
                    # 408 RequestTimeout
                    # 409 Conflict: a request using the same token with same parameters is in progress.
                    # 503: Service unavailable
                    message = "Timeout error"
                    raise PipedriveTimeOutError(message) from exc
                case _:
                    message = "HTTP error"
                    raise PipedriveHTTPError(message) from exc

        return response.json()

    def search_organizations(self, term: str, **params: dict) -> list | None:
        # https://developers.pipedrive.com/docs/api/v1/Organizations
        params = {
            "term": term,  # mandatory
        } | params
        results = self._request("/organizations/search", params)
        if not results:
            return None
        return results["data"]["items"]

    def deals(self, **params: dict) -> dict | None:
        # https://developers.pipedrive.com/docs/api/v1/Deals
        results = self._request("/deals", params=params)
        if not results:
            return None
        return results["data"]

    def update_deal(self, deal_id: int, **data: dict) -> dict | None:
        # https://developers.pipedrive.com/docs/api/v1/Deals
        response = self._request(f"/deals/{deal_id}", data=data, method="PATCH")
        return response["data"]

    def find_organization_by_name(self, name: str) -> dict | None:
        results = self.search_organizations(term=name, fields=["name"])
        if not results:
            return []
        return results[0]["item"]

    def get_organization_deals(self, organization_id: str) -> dict | None:
        return self.deals(org_id=organization_id)
