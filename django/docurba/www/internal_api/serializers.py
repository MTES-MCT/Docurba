# ruff: noqa: N815, RUF012


from django.db import models
from rest_framework import serializers

from docurba.core.enums import ProcedureType, TypeDocument
from docurba.core.models import (
    Collectivite,
    Commune,
    EventType,
    Procedure,
    Topic,
)


class BaseCollectiviteSerializer(serializers.ModelSerializer):
    codeInsee = serializers.CharField(source="code_insee")
    intitule = serializers.CharField(source="nom")
    departementCode = serializers.CharField(source="departement.code_insee")
    regionCode = serializers.CharField(source="departement.region.code_insee")
    intercommunaliteCode = serializers.SerializerMethodField()

    class Meta:
        model = Collectivite
        fields = [
            "codeInsee",
            "siren",
            "type",
            "intitule",
            "regionCode",
            "departementCode",
            "intercommunaliteCode",
        ]
        read_only_fields = fields

    def get_intercommunaliteCode(self, obj) -> str:  # noqa: ANN001, N802
        # serializer.CharField(default="") does not return the default value
        # because of the foreign key.
        # This is a workaround to avoid returning None.
        if (
            obj.is_commune
            and hasattr(obj, "commune")
            and obj.commune.intercommunalite_id
        ):
            return obj.commune.intercommunalite.siren
        return ""


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
    code = serializers.CharField(source="code_insee")
    intitule = serializers.CharField(source="nom")
    departementCode = serializers.CharField(source="departement.code_insee")
    regionCode = serializers.CharField(source="departement.region.code_insee")
    intercommunaliteCode = serializers.CharField(
        source="intercommunalite.siren", allow_blank=True, default=""
    )
    is_opposable = serializers.CharField(source="opposable", required=False)

    class Meta:
        model = Commune
        fields = [
            "code",
            "type",
            "intitule",
            "departementCode",
            "regionCode",
            "intercommunaliteCode",
            "is_opposable",
        ]
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


class TopicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Topic
        fields = ["name"]
        read_only_fields = fields


class ProcedureNameSerializer(serializers.ModelSerializer):
    parentId = serializers.UUIDField(source="parente_id", required=False)
    type = serializers.ChoiceField(choices=ProcedureType)
    number = serializers.CharField(required=False, source="numero")
    docType = serializers.ChoiceField(
        required=False, choices=TypeDocument, source="doc_type"
    )
    nameComplement = serializers.CharField(required=False, source="name_complement")
    perimetreCodes = serializers.ListField(
        required=False, child=serializers.CharField()
    )
    collectiviteCode = serializers.CharField(required=False)

    class Meta:
        model = Procedure
        fields = [
            "parentId",
            "type",
            "docType",
            "nameComplement",
            "number",
            "perimetreCodes",
            "collectiviteCode",
        ]

    # TODO: validate together: when principal or secondary procedure

    def to_representation(self, instance):
        parente_id = self.validated_data.pop("parente_id", None)
        if parente_id:
            parent_procedure = Procedure.objects.prefetch_related(
                models.Prefetch(
                    "perimetre",
                    Commune.objects.select_related(
                        "departement",
                        "departement__region",
                        "intercommunalite",
                    ).with_opposable(),
                ),
            ).get(pk=parente_id)
            collectivite_porteuse = (
                Collectivite.objects.with_communes_adherentes_count().get(
                    pk=parent_procedure.collectivite_porteuse.pk
                )
            )
            instance = Procedure(
                cached_perimetre=parent_procedure.perimetre.all(),
                collectivite_porteuse=collectivite_porteuse,
                doc_type=parent_procedure.doc_type,
                type=self.validated_data["type"],
                name_complement=self.validated_data.get("name_complement"),
                numero=self.validated_data.get("number"),
            )

        else:
            collectivite_code = self.validated_data.pop("collectiviteCode")
            perimetre_codes = self.validated_data.pop("perimetreCodes")
            perimetre = Commune.objects.filter(
                code_insee__in=perimetre_codes
            ).with_opposable()
            collectivite = (
                Collectivite.objects.filter(
                    models.Q(siren=collectivite_code)
                    | models.Q(code_insee=collectivite_code)
                )
                .with_communes_adherentes_count()
                .get()
            )
            instance = Procedure(
                cached_perimetre=perimetre,
                collectivite_porteuse=collectivite,
                **self.validated_data,
            )
        return {"name": instance.computed_name}


class ProcedureSerializer(serializers.ModelSerializer):
    id = serializers.CharField()
    parentId = serializers.UUIDField(source="parente_id")
    collectivite_porteuse = CollectiviteSerializer()
    docType = serializers.ChoiceField(choices=TypeDocument, source="type_document")
    startedBeforeHuwartLaw = serializers.BooleanField(
        source="started_before_huwart_law", default=False
    )
    topics = TopicSerializer(many=True)
    perimetre = CommuneSerializer(many=True)
    name = serializers.CharField(source="computed_name")
    approval_date = serializers.DateField(source="date_approbation")

    class Meta:
        model = Procedure
        read_only_fields = [
            "id",
            "project_id",
        ]
        fields = [
            *read_only_fields,
            "collectivite_porteuse",
            "project_id",
            "perimetre",
            "docType",
            "startedBeforeHuwartLaw",
            "type",
            "numero",
            "name",
            "status",
            "topics",
            "approval_date",
            "parentId",
        ]
        depth = 4
