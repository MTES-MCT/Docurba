from unittest.mock import patch

import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from core.api_internes.paginators import DocurbaPagination
from core.tests.factories import create_groupement


@pytest.mark.django_db
def test_docurba_paginator(api_client: APIClient) -> None:
    for _ in range(5):
        create_groupement()
    url = reverse("api_internes:collectivites-list")

    # https://github.com/encode/django-rest-framework/issues/2466
    # https://github.com/encode/django-rest-framework/issues/6030
    with patch.object(DocurbaPagination, "page_size", 1):
        response = api_client.get(url, format="json")

    assert response.json()["num_pages"] == 5
