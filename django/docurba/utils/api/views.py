from rest_framework.permissions import AllowAny
from rest_framework.views import APIView


class PublicAPIView(APIView):
    permission_classes = [AllowAny]  # noqa: RUF012
