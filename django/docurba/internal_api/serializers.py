# ruff: noqa: N815, RUF012

from django.shortcuts import get_object_or_404
from rest_framework import serializers

from docurba.core.enums import CommuneType, ProcedureType
from docurba.core.models import (
    Collectivite,
    Commune,
    CommuneProcedure,
    EventType,
    Procedure,
    ProcedureTopic,
    Project,
    Topic,
    TypeDocument,
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

    class Meta:
        model = Commune
        fields = [
            "code",
            "type",
            "intitule",
            "departementCode",
            "regionCode",
            "intercommunaliteCode",
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


class BaseProcedureSerializer(serializers.ModelSerializer):
    id = serializers.CharField(read_only=True)
    project_id = serializers.CharField(read_only=True)
    perimetreCommunesCodes = serializers.ListField(
        write_only=True, source="perimetre", child=serializers.CharField()
    )
    collectiviteCode = serializers.CharField(
        write_only=True,
    )
    docType = serializers.ChoiceField(choices=TypeDocument, source="doc_type")
    startedBeforeHuwartLaw = serializers.BooleanField(
        source="started_before_huwart_law", default=False
    )
    topics = serializers.ListField(
        write_only=True, child=serializers.CharField(), allow_empty=True
    )
    otherTopicComment = serializers.CharField(allow_blank=True, write_only=True)

    def create(self, validated_data: dict) -> Procedure:
        owner_id = self.context["request"].user.username

        collectivite_code = validated_data["collectiviteCode"]
        # As long as the code_insee is not in Collectivite,
        # we have two classes.
        if len(collectivite_code) == 5:  # noqa: PLR2004
            collectivite_qs = Commune.objects.filter(
                code_insee=collectivite_code
            ).select_related("intercommunalite")
        else:
            collectivite_qs = Collectivite.objects.filter(siren=collectivite_code)
        collectivite = get_object_or_404(collectivite_qs)
        collectivite_porteuse = Procedure.get_collectivite_porteuse(
            collectivite=collectivite, doc_type=validated_data["doc_type"]
        )

        if validated_data["type"] in ProcedureType.principal():
            name = f"{validated_data['type']} {validated_data['doc_type']}"
            collectivite_intercommunalite = (
                collectivite.intercommunalite
                if collectivite.type in CommuneType
                else None
            )
            project_collectivite_id = (
                collectivite_intercommunalite.code_insee_unique
                if collectivite_intercommunalite
                else collectivite_porteuse.code_insee_unique
            )
            project = Project.objects.create(
                name=name,
                doc_type=validated_data["doc_type"],
                region=collectivite.departement.region.code_insee,
                collectivite_id=project_collectivite_id,
                collectivite_porteuse_id=collectivite_porteuse.code_insee_unique,
                test=True,
                owner_id=owner_id,
            )
        # Remove these keys from `validated_data` because they are not Procedure attributes.
        validated_data.pop("collectiviteCode")
        perimetre_codes = validated_data.pop("perimetre")
        topics_list = validated_data.pop("topics")
        other_topic_comment = (
            "otherTopicComment" in self.validated_data
            and validated_data.pop("otherTopicComment")
        )
        instance_data = validated_data | {
            "testing": True,
            "owner_id": owner_id,
            "project_id": project.id,
            "collectivite_porteuse_id": collectivite_porteuse.code_insee_unique,
        }
        instance = super().create(validated_data=instance_data)

        communes = Commune.objects.filter(code_insee__in=perimetre_codes)
        for commune in communes:
            CommuneProcedure.objects.create(
                commune=commune,
                procedure=instance,
                commune_id=f"{commune.code_insee}_{commune.type}",
                # Always a code_insee, never a SIREN.
                collectivite_code=commune.code_insee,
                # In enums.CommuneType only
                collectivite_type=commune.type,
                opposable=False,
                departement=commune.departement.code_insee,
            )
        # project.current_perimetre is a denormalized information that needs to
        # be re-computed after CommuneProcedure creation.
        project.current_perimetre = instance.current_perimetre
        project.save()

        for topic in topics_list:
            if topic == "other" and other_topic_comment:
                ProcedureTopic.objects.create(
                    procedure_id=instance.pk,
                    topic_id=Topic.objects.get(name="other").pk,
                    comment=other_topic_comment,
                )
                del topic
        topics = Topic.objects.filter(name__in=topics_list)
        instance.topics.add(*topics)
        return instance

    def validate(self, data: dict) -> dict:
        error_msg = None
        if len(data["perimetre"]) == 1 and data["doc_type"] in [
            "PLUi",
            "PLUiH",
            "PLUiM",
            "PLUiHM",
            "SCOT",
        ]:
            error_msg = f"{data['doc_type']} est un document intercommunal mais une seule commune fait partie du périmètre de la procédure."

        if len(data["perimetre"]) > 1 and data["doc_type"] in ["CC", "PLU"]:
            error_msg = f"{data['doc_type']} est un document communal mais plusieurs communes font partie du périmètre de la procédure."

        other_topic_comment = data.get("otherTopicComment")
        if other_topic_comment and "other" not in data.get("topics"):
            error_msg = (
                "Un commentaire Autre ne peut être enregistré que pour l'objet Autre."
            )
        if "other" in data.get("topics") and not other_topic_comment:
            error_msg = (
                "Un commentaire est obligatoire car l'objet Autre a été sélectionné."
            )
        if error_msg:
            raise serializers.ValidationError(error_msg)
        return data

    class Meta:
        model = Procedure
        read_only_fields = [
            "id",
            "project_id",
        ]
        fields = [
            # "parent",
            *read_only_fields,
            "docType",
            "startedBeforeHuwartLaw",
            "topics",
            "otherTopicComment",
            "type",
            "numero",
            "name",
            "collectiviteCode",
            "perimetreCommunesCodes",
        ]


class ProcedureSerializer(BaseProcedureSerializer):
    # parent = BaseProcedureSerializer(source="parente", default="")

    class Meta:
        model = Procedure
        fields = [
            # "parente",
            *BaseProcedureSerializer.Meta.fields,
        ]
