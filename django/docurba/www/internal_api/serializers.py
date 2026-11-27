# ruff: noqa: N815, RUF012


from django.db import models
from rest_framework import serializers

from docurba.core.enums import (
    CommuneType,
    ProcedureType,
    TypeDocument,
    VisibilityType,
)
from docurba.core.models import (
    Collectivite,
    Commune,
    Event,
    EventType,
    Procedure,
    Topic,
)
from docurba.users.enums import ProfileSideType
from docurba.users.models import Profile


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
    scopeList = serializers.JSONField(source="scope_list")
    scopeSugg = serializers.JSONField(source="scope_sugg")

    class Meta:
        model = EventType
        fields = [
            "id",
            "documentType",
            "name",
            "scopeList",
            "scopeSugg",
            "isStructuring",
        ]
        read_only_fields = fields


class ProfileSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(source="user_id", read_only=True)

    class Meta:
        model = Profile
        read_only_fields = [
            "id",
        ]
        fields = [
            *read_only_fields,
            "firstname",
            "lastname",
            "email",
            "side",
        ]


class EventAttachementSerializer(serializers.Serializer):
    id = serializers.CharField(required=True)
    name = serializers.CharField(required=True)
    type = serializers.ChoiceField(required=False, choices=["file", "link"])


class EventAttachementMixin:
    def to_representation(self, value: str) -> dict:
        result = super().to_representation(value)
        if result["attachements"]:
            for attachement in result["attachements"]:
                attachement["path"] = value.get_attachement_path(attachement["id"])
        return result


class PublicEventSerializer(EventAttachementMixin, serializers.ModelSerializer):
    # Read only fields
    name = serializers.CharField(read_only=True)
    isPublic = serializers.BooleanField(source="is_public", read_only=True)
    isSudocuh = serializers.BooleanField(source="is_sudocuh", read_only=True)
    isValid = serializers.BooleanField(source="is_valid", read_only=True)
    isSystem = serializers.BooleanField(source="is_system", read_only=True)
    eventType = EventTypeSerializer(source="event_type", read_only=True)
    procedureId = serializers.PrimaryKeyRelatedField(source="procedure", read_only=True)
    dateEvenement = serializers.DateTimeField(source="date_evenement")
    otherName = serializers.CharField(
        source="type", allow_blank=True, required=False, default=""
    )
    attachements = EventAttachementSerializer(many=True, required=False, default=list)

    class Meta:
        model = Event
        read_only_fields = [
            "id",
            "name",
            "isPublic",
            "isValid",
            "isSystem",
            "isSudocuh",
            "eventType",
            "procedureId",
            "otherName",
            "dateEvenement",
            "attachements",
        ]
        fields = [*read_only_fields]


def can_profile_edit_event(profile: Profile, event: Event) -> bool:
    # TODO: Add corresponding permissions and move elsewhere when restructuring permissions  # noqa: FIX002
    if event.is_sudocuh:
        return False
    return bool(
        profile.user_id == event.profile_id or profile.side == ProfileSideType.ETAT
    )


class EventSerializer(EventAttachementMixin, serializers.ModelSerializer):
    # Read only fields
    name = serializers.CharField(read_only=True)
    isPublic = serializers.BooleanField(source="is_public", read_only=True)
    isSudocuh = serializers.BooleanField(source="is_sudocuh", read_only=True)
    isValid = serializers.BooleanField(source="is_valid", read_only=True)
    isSystem = serializers.BooleanField(source="is_system", read_only=True)
    eventType = EventTypeSerializer(source="event_type", read_only=True)
    profile = ProfileSerializer(read_only=True)
    editable = serializers.SerializerMethodField()

    def get_editable(self, event: Event) -> bool:
        if "request" in self.context:
            profile = self.context["request"].user.profile
            if profile:
                return can_profile_edit_event(profile, event)
        return False

    # Write only fields
    eventTypeId = serializers.PrimaryKeyRelatedField(
        queryset=EventType.objects.all(),
        source="event_type",
        allow_null=True,
        write_only=True,
    )

    # Write on create - Read on update (see get_fields())
    procedureId = serializers.PrimaryKeyRelatedField(source="procedure", read_only=True)

    # Read / write fields
    dateEvenement = serializers.DateTimeField(source="date_evenement")
    visibility = serializers.ChoiceField(choices=VisibilityType)
    otherName = serializers.CharField(
        source="type", allow_blank=True, required=False, default=""
    )
    attachements = EventAttachementSerializer(many=True, required=False, default=list)

    class Meta:
        model = Event
        read_only_fields = [
            "id",
            "name",
            "isPublic",
            "isValid",
            "isSudocuh",
            "isSystem",
            "eventType",
            "profile",
            "editable",
        ]
        fields = [
            *read_only_fields,
            "procedureId",
            "eventTypeId",
            "otherName",
            "dateEvenement",
            "visibility",
            "description",
            "attachements",  # TODO: Use specific endpoint for attachements # noqa: FIX002
        ]

    def get_fields(self, *args, **kwargs):  # noqa: ANN002, ANN003, ANN201
        fields = super().get_fields(*args, **kwargs)
        action = self.context["view"].action
        if action == "create":
            fields["procedureId"].read_only = False
            fields["procedureId"].queryset = Procedure.objects.all()
        return fields


class TopicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Topic
        fields = ["name"]
        read_only_fields = fields


class ProcedureNameSerializer(serializers.ModelSerializer):
    parentId = serializers.UUIDField(required=False, source="parente_id")
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

    def validate_collectiviteCode(self, value: str) -> str:  # noqa: N802
        if (
            not Collectivite.objects.filter(
                models.Q(siren=value) | models.Q(code_insee=value)
            )
            .exclude(type__in=[CommuneType.COMD, CommuneType.COMA])
            .exists()
        ):
            raise serializers.ValidationError(
                ('The "collectivité porteuse" has not been found.',),
            )
        return value

    def validate_perimetreCodes(self, values: list) -> list:  # noqa: N802
        found_communes = Commune.objects.filter(code_insee__in=values).values_list(
            "code_insee", flat=True
        )
        not_found = [code for code in values if code not in found_communes]
        if not_found:
            raise serializers.ValidationError(
                (f"Following communes have not been found: {not_found}.",),
            )
        return values

    def validate_parentId(self, value: str) -> str:  # noqa: N802
        if not Procedure.objects.filter(pk=value).exists():
            raise serializers.ValidationError(
                ("The principal procedure has not been found.",),
            )
        return value

    def validate(self, data: dict) -> dict:
        principal_procedure_required_fields = [
            "collectiviteCode",
            "perimetreCodes",
            "doc_type",
        ]
        if not data.get("parente_id") and not all(
            field in data for field in principal_procedure_required_fields
        ):
            raise serializers.ValidationError(
                (
                    f"Missing principal procedure required field. Mandatory fields are: {principal_procedure_required_fields}",
                ),
            )

        return data

    def to_representation(self, value: str) -> dict:  # noqa: ARG002
        parente_id = self.validated_data.pop("parente_id", None)
        if parente_id:
            principal_procedure = Procedure.objects.prefetch_related(
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
                    pk=principal_procedure.collectivite_porteuse.pk
                )
            )
            instance = Procedure(
                cached_perimetre=principal_procedure.perimetre.all(),
                collectivite_porteuse=collectivite_porteuse,
                base_doc_type=principal_procedure.base_doc_type,
                vaut_PDM=principal_procedure.vaut_PDM,
                vaut_PLH=principal_procedure.vaut_PLH,
                type=self.validated_data["type"],
                name_complement=self.validated_data.get("name_complement"),
                numero=self.validated_data.get("numero"),
            )

        else:
            collectivite_code = self.validated_data.pop("collectiviteCode")
            perimetre_codes = self.validated_data.pop("perimetreCodes")
            doc_type = self.validated_data.pop("doc_type")
            base_doc_type = Procedure.dynamic_doc_type_to_base_doc_type(doc_type)
            vaut_PLH = doc_type in TypeDocument.plh_variations()  # noqa: N806
            vaut_PDM = doc_type in TypeDocument.pdm_variations()  # noqa: N806
            perimetre = Commune.objects.filter(
                code_insee__in=perimetre_codes,
                type=CommuneType.COM,
            )
            collectivite = (
                Collectivite.objects.filter(
                    models.Q(siren=collectivite_code)
                    | models.Q(code_insee=collectivite_code)
                )
                .exclude(type__in=[CommuneType.COMD, CommuneType.COMA])
                .with_communes_adherentes_count()
                .get()
            )
            instance = Procedure(
                cached_perimetre=perimetre,
                collectivite_porteuse=collectivite,
                base_doc_type=base_doc_type,
                vaut_PLH=vaut_PLH,
                vaut_PDM=vaut_PDM,
                **self.validated_data,
            )
        return {"name": instance.computed_name}


class ProcedureSerializer(serializers.ModelSerializer):
    id = serializers.CharField()
    parentId = serializers.UUIDField(source="parente_id")
    collectivite_porteuse = CollectiviteSerializer()
    docType = serializers.ChoiceField(choices=TypeDocument, source="dynamic_doc_type")
    startedBeforeHuwartLaw = serializers.BooleanField(
        source="started_before_huwart_law", default=False
    )
    topics = TopicSerializer(many=True)
    perimetre = CommuneSerializer(many=True)
    name = serializers.CharField(source="computed_name")
    approval_date = serializers.DateTimeField(source="date_approbation")

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
