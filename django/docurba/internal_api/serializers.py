# ruff: noqa: N815, RUF012
from rest_framework import serializers

from docurba.core.models import Collectivite, Commune, EventType


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


class EventTypeSerializer(serializers.ModelSerializer):
    documentType = serializers.CharField(source="document_type")
    isStructuring = serializers.BooleanField(source="is_structuring")
    sudocuhName = serializers.CharField(source="sudocuh_name")
    scopeList = serializers.JSONField(source="scope_list")
    scopeSugg = serializers.JSONField(source="scope_sugg")

    # TODO: remove  # noqa: FIX002
    # is_structuring AND sudocuh_name are needed by nuxt
    # when Event will references EventType, the information will be provided directly by EventSerializer
    class Meta:
        model = EventType
        fields = [
            "id",
            "documentType",
            "name",
            "scopeList",
            "scopeSugg",
            "isStructuring",  # TODO: remove  # noqa: FIX002
            "sudocuhName",  # TODO: remove  # noqa: FIX002
        ]
        read_only_fields = fields
