# ruff: noqa: N815, RUF012
from rest_framework import serializers

from core.models import Collectivite


# The django-rest-framework-gis package provides a GeoFeatureModelSerializer serializer class that supports GeoJSON both for read and write operations.
class CollectiviteSerializer(serializers.ModelSerializer):
    code = serializers.CharField(source="code_insee_unique")
    intitule = serializers.CharField(source="nom")
    departementCode = serializers.CharField(source="departement.code_insee")
    regionCode = serializers.CharField(source="departement.region.code_insee")

    class Meta:
        model = Collectivite
        fields = ["code", "type", "intitule", "departementCode", "regionCode"]
        read_only_fields = fields
