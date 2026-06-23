# ruff: noqa: N815, RUF012
from rest_framework import serializers

from docurba.core.models import Collectivite, Commune, Event


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


class EventListSerializer(serializers.ModelSerializer):
    dateEvenement = serializers.DateField(source="date_evenement")
    fromSudocuh = serializers.IntegerField(source="from_sudocuh", required=False)
    isValid = serializers.BooleanField(source="is_valid", read_only=True)
    visibility = serializers.CharField()

    class Meta:
        model = Event
        read_only_fields = ["id", "isValid", "fromSudocuh"]
        fields = [
            *read_only_fields,
            "procedure",
            "type",
            "dateEvenement",
            "visibility",
        ]


class EventDetailSerializer(EventListSerializer):
    class Meta(EventListSerializer.Meta):
        fields = [
            *EventListSerializer.Meta.fields,
            "description",
            "attachements",  # TODO: Use specific endpoint for attachements # noqa: FIX002
        ]


class EventCreateSerializer(EventDetailSerializer):
    class Meta(EventDetailSerializer.Meta):
        read_only_fields = [*EventDetailSerializer.Meta.read_only_fields, "procedure"]
