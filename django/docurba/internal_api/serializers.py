# ruff: noqa: N815, RUF012

from rest_framework import serializers

from docurba.core.models import Collectivite, Commune


class BaseCollectiviteSerializer(serializers.ModelSerializer):
    code = serializers.CharField(source="code_insee_unique")
    intitule = serializers.CharField(source="nom")
    departementCode = serializers.CharField(source="departement.code_insee")
    regionCode = serializers.CharField(source="departement.region.code_insee")

    class Meta:
        model = Collectivite
        fields = [
            "code",
            "type",
            "intitule",
            "regionCode",
            "departementCode",
        ]
        read_only_fields = fields


class MemberSerializer(BaseCollectiviteSerializer):
    pass


class CollectiviteSerializer(BaseCollectiviteSerializer):
    membres = MemberSerializer(source="flat_members", many=True, read_only=True)
    groupements = MemberSerializer(source="flat_groups", many=True, read_only=True)

    class Meta:
        model = Collectivite
        fields = [
            *BaseCollectiviteSerializer.Meta.fields,
            "membres",
            "groupements",
        ]
        read_only_fields = fields

    def __init__(self, *args: list, **kwargs: dict) -> None:
        super().__init__(*args, **kwargs)

        with_members = self.context.get("with_members", False)
        if not with_members:
            self.fields.pop("membres")

        with_groups = self.context.get("with_groups", False)
        if not with_groups:
            self.fields.pop("groupements")


class CommuneSerializer(serializers.ModelSerializer):
    code = serializers.CharField(source="code_insee_unique")
    intitule = serializers.CharField(source="nom")
    departementCode = serializers.CharField(source="departement.code_insee")
    regionCode = serializers.CharField(source="departement.region.code_insee")

    class Meta:
        model = Commune
        fields = ["code", "type", "intitule", "departementCode", "regionCode"]
        read_only_fields = fields
