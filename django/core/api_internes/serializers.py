# ruff: noqa: N815, RUF012
from rest_framework import serializers

from core.models import Collectivite, Commune


class CollectiviteSerializer(serializers.ModelSerializer):
    code = serializers.CharField(source="code_insee_unique")
    intitule = serializers.CharField(source="nom")
    departementCode = serializers.CharField(source="departement.code_insee")
    regionCode = serializers.CharField(source="departement.region.code_insee")

    class Meta:
        model = Collectivite
        fields = ["code", "type", "intitule", "departementCode", "regionCode"]
        read_only_fields = fields


class CommuneSerializer(serializers.ModelSerializer):
    code = serializers.CharField(source="code_insee_unique")
    intitule = serializers.CharField(source="nom")
    departementCode = serializers.CharField(source="departement.code_insee")
    regionCode = serializers.CharField(source="departement.region.code_insee")

    class Meta:
        model = Commune
        fields = ["code", "type", "intitule", "departementCode", "regionCode"]
        read_only_fields = fields
