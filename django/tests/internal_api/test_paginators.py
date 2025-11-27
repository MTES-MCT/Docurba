from unittest.mock import patch

import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from docurba.internal_api.paginators import DocurbaPagination
from tests.core.factories import CollectiviteFactory


@pytest.mark.django_db
def test_docurba_paginator(api_client: APIClient) -> None:
    CollectiviteFactory.create_batch(5)
    url = reverse("internal_api:collectivites-list")

    # https://github.com/encode/django-rest-framework/issues/2466
    # https://github.com/encode/django-rest-framework/issues/6030
    with patch.object(DocurbaPagination, "page_size", 1):
        response = api_client.get(url, format="json")

    assert response.json()["num_pages"] == 5
