from rest_framework import pagination
from rest_framework.response import Response


class DocurbaPagination(pagination.PageNumberPagination):
    # https://github.com/encode/django-rest-framework/blob/main/rest_framework/pagination.py#L230-L236
    def get_paginated_response(self, data: dict) -> Response:
        response = super().get_paginated_response(data)
        # https://docs.djangoproject.com/en/6.0/ref/paginator/#django.core.paginator.Paginator.num_pages
        response.data["num_pages"] = self.page.paginator.num_pages
        return response
