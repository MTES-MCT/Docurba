# ruff: noqa: N815, RUF012
from django.db import models
from rest_framework import serializers

from docurba.core.enums import CommuneType, ProcedureType, TypeDocument
from docurba.core.models import (
    Collectivite,
    Commune,
    CommuneProcedure,
    EventType,
    Procedure,
    ProcedureTopic,
    Project,
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
        if not Collectivite.objects.filter(
            models.Q(siren=value) | models.Q(code_insee=value)
        ).exists():
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
                doc_type=principal_procedure.doc_type,
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
    # Read only fields
    id = serializers.CharField(read_only=True)
    collectivite_porteuse = CollectiviteSerializer(read_only=True)
    topics = TopicSerializer(read_only=True, many=True)
    perimetre = CommuneSerializer(read_only=True, many=True)
    name = serializers.CharField(read_only=True, source="computed_name")
    approval_date = serializers.DateField(read_only=True, source="date_approbation")
    projectId = serializers.CharField(read_only=True, source="project_id")
    # Write only fields
    perimetreCodes = serializers.ListField(
        write_only=True,
        required=False,
        child=serializers.CharField(required=False, allow_blank=True),
    )
    collectiviteCode = serializers.CharField(
        write_only=True,
        allow_blank=True,
        required=False,
    )
    topicsList = serializers.ListField(
        write_only=True, child=serializers.CharField(), allow_empty=True
    )
    otherTopicComment = serializers.CharField(
        required=False, allow_blank=True, write_only=True
    )
    nameComplement = serializers.CharField(
        required=False, allow_blank=True, write_only=True, source="name_complement"
    )
    # Both
    parentId = serializers.UUIDField(
        source="parente_id", required=False, allow_null=True
    )
    docType = serializers.ChoiceField(
        choices=TypeDocument,
        source="type_document",
        required=False,
        allow_blank=True,
    )
    startedBeforeHuwartLaw = serializers.BooleanField(
        source="started_before_huwart_law", default=False
    )
    number = serializers.CharField(required=False, allow_blank=True, source="numero")

    def create(self, validated_data: dict) -> Procedure:
        owner_id = self.context["request"].user.username
        # Remove these keys from `validated_data` because they are not Procedure attributes.
        topics_list = validated_data.pop("topicsList")
        other_topic_comment = validated_data.pop("otherTopicComment")
        principal_procedure = validated_data.get("parente_id")
        if validated_data["type"] in ProcedureType.principal():
            doc_type = validated_data.pop("type_document")
            collectivite_code = validated_data.pop("collectiviteCode")
            perimetre_codes = validated_data.pop("perimetreCodes")
            collectivite = (
                Collectivite.objects.filter_by_code(collectivite_code)
                .exclude(type__in=[CommuneType.COMA, CommuneType.COMD])
                .get()
            )
            collectivite_porteuse = Procedure.get_collectivite_porteuse(
                collectivite=collectivite, doc_type=doc_type
            )
            instance_data = validated_data | {
                "doc_type": doc_type,
                "testing": True,
                "owner_id": owner_id,
                "collectivite_porteuse": collectivite_porteuse,
            }
        else:
            principal_procedure = Procedure.objects.get(pk=validated_data["parente_id"])
            instance_data = {
                "type": validated_data["type"],
                "started_before_huwart_law": validated_data.get(
                    "started_before_huwart_law", False
                ),
                "parente": principal_procedure,
                "doc_type": principal_procedure.doc_type,
                "collectivite_porteuse": principal_procedure.collectivite_porteuse,
                "testing": True,
                "owner_id": owner_id,
                "name_complement": validated_data.get("name_complement"),
                "numero": validated_data.get("numero", ""),
            }

        instance = super().create(validated_data=instance_data)

        if validated_data["type"] in ProcedureType.principal():
            perimetre = Commune.objects.filter(code_insee__in=perimetre_codes)
        else:
            perimetre = principal_procedure.perimetre.all()
        communes_procedures = [
            CommuneProcedure(
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
            for commune in perimetre
        ]
        CommuneProcedure.objects.bulk_create(communes_procedures)
        instance.update_perimetre_denormalized_fields(save=False)

        if validated_data["type"] in ProcedureType.principal():
            project_collectivite = collectivite_porteuse
            if (
                collectivite.type in CommuneType
                and collectivite.commune.intercommunalite
            ):
                project_collectivite = collectivite.commune.intercommunalite

            # The test column will be deleted during the big refactoring.
            project = Project.objects.create(
                name=f"{validated_data['type']} {doc_type}",
                doc_type=doc_type,
                region=collectivite.departement.region.code_insee,
                collectivite_id=project_collectivite.siren
                or project_collectivite.code_insee,
                collectivite_porteuse_id=collectivite_porteuse.siren
                or collectivite_porteuse.code_insee,
                test=True,
                owner_id=owner_id,
                current_perimetre=instance.current_perimetre,
            )
        else:
            project = principal_procedure.project
        instance.project_id = project.pk

        topics_by_name = {
            topic["name"]: topic["id"] for topic in Topic.objects.values("name", "id")
        }

        procedure_topics = [
            ProcedureTopic(
                procedure_id=instance.pk,
                topic_id=topics_by_name[topic],
                comment=other_topic_comment if topic == "other" else "",
            )
            for topic in topics_list
        ]
        ProcedureTopic.objects.bulk_create(procedure_topics)
        # The selected doc type does not include the S information and is sometimes wrong.
        # Setting it in the instance.save method would make the code
        # really complicated and would had unexpected side effects.
        # Until we clean every procedure.doc_type, and remove the
        # Procedure.type_document method, set the doc_type here.
        instance.doc_type = instance.type_document
        instance.save()
        return instance

    def validate_collectiviteCode(self, value: str) -> str:  # noqa: N802
        if value and (
            not Collectivite.objects.filter_by_code(value)
            .exclude(type__in=[CommuneType.COMA, CommuneType.COMD])
            .exists()
        ):
            raise serializers.ValidationError("Collectivité not found")  # noqa:EM101,TRY003
        return value

    def validate_parentId(self, value: str) -> str:  # noqa: N802
        if value and (not Procedure.objects.filter(pk=value).exists()):
            raise serializers.ValidationError("Principal procedure not found.")  # noqa:EM101,TRY003
        return value

    def validate_perimetreCodes(self, values: str) -> str:  # noqa: N802
        values = [value for value in values if value != ""]
        if values:
            found_communes = Commune.objects.filter(code_insee__in=values).values_list(
                "code_insee", flat=True
            )
            not_found = [code for code in values if code not in found_communes]
            if not_found:
                raise serializers.ValidationError(
                    (f"Following communes have not been found: {not_found}.",),
                )
        return values

    def validate(self, data: dict) -> dict:
        error_msg = None
        if len(data["perimetreCodes"]) == 1 and data["type_document"] in [
            "PLUi",
            "PLUiH",
            "PLUiM",
            "PLUiHM",
            "SCOT",
        ]:
            error_msg = f"{data['type_document']} is an intermunicipality document but only one town has been selected."

        if len(data["perimetreCodes"]) > 1 and data["type_document"] in [
            "CC",
            "PLU",
        ]:
            error_msg = f"{data['type_document']} is a municipality document but many towns have been selected."

        other_topic_comment = data.get("otherTopicComment")
        if other_topic_comment and "other" not in data.get("topicsList", []):
            error_msg = (
                "Un commentaire Autre ne peut être enregistré que pour l'objet Autre."
            )
        if "other" in data.get("topicsList", []) and not other_topic_comment:
            error_msg = (
                "Un commentaire est obligatoire car l'objet Autre a été sélectionné."
            )
        principal_procedure_required_fields = [
            "collectiviteCode",
            "perimetreCodes",
            "type_document",
        ]
        if not data.get("parente_id") and not all(
            field in data for field in principal_procedure_required_fields
        ):
            raise serializers.ValidationError(
                (
                    f"Missing principal procedure required field. Mandatory fields are: {principal_procedure_required_fields}",
                ),
            )

        if error_msg:
            raise serializers.ValidationError(error_msg)
        return data

    class Meta:
        model = Procedure
        read_only_fields = [
            "id",
            "collectivite_porteuse",
            "topics",
            "perimetre",
            "name",
            "approval_date",
            "projectId",
            "status",  # Nuxt one
        ]
        write_only_fields = [
            "perimetreCodes",
            "collectiviteCode",
            "topicsList",
            "otherTopicComment",
            "nameComplement",
        ]
        fields = [
            *read_only_fields,
            *write_only_fields,
            "parentId",
            "docType",
            "startedBeforeHuwartLaw",
            "type",
            "number",
        ]
        depth = 4
