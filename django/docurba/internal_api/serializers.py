# ruff: noqa: N815, RUF012

from rest_framework import serializers

from docurba.core.models import Collectivite, Commune, EventType


class BaseCollectiviteSerializer(serializers.ModelSerializer):
    code = serializers.CharField(source="code_insee_unique")
    intitule = serializers.CharField(source="nom")
    departementCode = serializers.CharField(source="departement.code_insee")
    regionCode = serializers.CharField(source="departement.region.code_insee")

    class Meta:
        model = Collectivite
        fields = [
            "code",
            "siren",
            "type",
            "intitule",
            "regionCode",
            "departementCode",
        ]
        read_only_fields = fields


class MemberSerializer(BaseCollectiviteSerializer):
    pass


class CollectiviteSerializer(BaseCollectiviteSerializer):
    membres_niveaux_inferieurs = MemberSerializer(
        source="flat_members", many=True, read_only=True
    )
    membres = MemberSerializer(
        source="collectivites_adherentes", many=True, read_only=True
    )
    groupements_niveaux_superieurs = MemberSerializer(
        source="flat_groups", many=True, read_only=True
    )
    groupements = MemberSerializer(source="adhesions", many=True, read_only=True)

    class Meta:
        model = Collectivite
        fields = [
            *BaseCollectiviteSerializer.Meta.fields,
            "membres_niveaux_inferieurs",
            "membres",
            "groupements_niveaux_superieurs",
            "groupements",
        ]
        read_only_fields = fields

    def __init__(self, *args: list, **kwargs: dict) -> None:
        super().__init__(*args, **kwargs)

        with_flat_members = self.context.get("with_flat_members", False)
        if not with_flat_members:
            self.fields.pop("membres_niveaux_inferieurs")

        with_flat_groups = self.context.get("with_flat_groups", False)
        if not with_flat_groups:
            self.fields.pop("groupements_niveaux_superieurs")

        with_groups = self.context.get("with_groups", False)
        if not with_groups:
            self.fields.pop("groupements")

        with_members = self.context.get("with_members", False)
        if not with_members:
            self.fields.pop("membres")


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
