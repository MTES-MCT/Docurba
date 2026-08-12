# ruff: noqa: ARG002

import functools

from django.db.models import Q, QuerySet
from django.forms import MultipleChoiceField
from django_filters import rest_framework as filters

from docurba.core.models import (
    Collectivite,
    Commune,
    Departement,
    EventType,
    Procedure,
    ProcedureStatusChoices,
    Region,
    TypeCollectivite,
)


class DepartementRegionFilterSet(filters.FilterSet):
    departement = filters.ModelMultipleChoiceFilter(
        field_name="departement__code_insee",
        to_field_name="code_insee",
        queryset=Departement.objects.all(),
    )
    region = filters.ModelMultipleChoiceFilter(
        field_name="departement__region__code_insee",
        to_field_name="code_insee",
        queryset=Region.objects.all(),
    )
    fields = (
        "departement",
        "region",
    )


# NOTE(cms): we could use the english word "jurisdiction"
# that has the same meaning as "compétence" in French
# but "compétence" is widely used in the existing code.
# Let's bring everything in Django first so that we can quietly
# rename it lately.
COMPETENCES_CHOICES = (
    ("plan", "Plan"),
    ("schema", "Schéma"),
)


class NoValidationMultipleField(MultipleChoiceField):
    def validate(self, value: str) -> None:
        pass


class NoValidationMultipleFilter(filters.MultipleChoiceFilter):
    field_class = NoValidationMultipleField


class CollectiviteFilter(DepartementRegionFilterSet):
    type = filters.MultipleChoiceFilter(field_name="type", choices=TypeCollectivite)
    codes_siren = NoValidationMultipleFilter(
        label="Codes SIREN",
        field_name="code_insee_unique",
    )
    without_communes = filters.BooleanFilter(
        label="Sans les communes", method="_without_communes"
    )
    competence = filters.MultipleChoiceFilter(
        label="Compétence",
        method="_filter_competences",
        choices=COMPETENCES_CHOICES,
    )

    class Meta:
        model = Collectivite
        fields = (
            "type",
            "codes_siren",
            "competence",
            *DepartementRegionFilterSet.fields,
        )

    def _filter_competences(
        self, queryset: QuerySet, name: str, values: str
    ) -> QuerySet:
        if not values:
            return queryset
        queries = []
        for value in values:
            if value == "plan":
                queries.append(Q(competence_plan=True))
            if value == "schema":
                queries.append(Q(competence_schema=True))

        return queryset.filter(functools.reduce(Q.__or__, queries))

    def _without_communes(self, queryset: QuerySet, name: str, value: str) -> QuerySet:
        if not value:
            return queryset
        commune_types = TypeCollectivite.communes()
        return queryset.exclude(type__in=commune_types)


class CommuneFilter(DepartementRegionFilterSet):
    type = filters.MultipleChoiceFilter(
        field_name="type", choices=TypeCollectivite.communes()
    )
    code = NoValidationMultipleFilter(field_name="code_insee_unique")

    class Meta:
        model = Commune
        fields = ("type", "code", *DepartementRegionFilterSet.fields)


class EventTypeFilter(filters.FilterSet):
    class Meta:
        model = EventType
        fields = ("document_type",)


class ProcedureFilter(filters.FilterSet):
    communes_perimetre = NoValidationMultipleFilter(
        label="communes du périmètre", method="_communes_perimetre"
    )
    collectivites_porteuses = NoValidationMultipleFilter(
        label="collectivités porteuses", method="_collectivites_porteuses"
    )
    status = filters.MultipleChoiceFilter(
        label="Statut selon Nuxt",
        field_name="status",
        choices=ProcedureStatusChoices,
    )

    class Meta:
        model = Procedure
        fields = (
            "is_principale",
            "status",
            "communes_perimetre",
            "collectivites_porteuses",
        )

    def _collectivites_porteuses(
        self, queryset: QuerySet, name: str, sirens: list
    ) -> QuerySet:
        if not sirens:
            return queryset
        if not isinstance(sirens, list):
            raise ValueError(("%s should be a list.", sirens))  # noqa: TRY004
        return queryset.select_related("collectivite_porteuse__siren").filter(
            collectivite_porteuse__siren__in=sirens
        )

    def _communes_perimetre(
        self, queryset: QuerySet, name: str, codes_insee: str
    ) -> QuerySet:
        if not codes_insee:
            return queryset
        if not isinstance(codes_insee, list):
            raise ValueError(("%s should be a list.", codes_insee))  # noqa: TRY004
        # Should search in the JSON but we'd like to search several keys.
        # The actual search only works when there is only one element in the list.
        #     query = query.contains('current_perimetre', `[{ "inseeCode": "${this.collectivite.code}" }]`)
        return queryset.select_related("perimetre__code_insee").filter(
            perimetre__code_insee__in=codes_insee
        )

    # let query = this.$supabase.from('procedures').select('*, procedures_perimetres(*)').eq('is_principale', true).eq('status', 'opposable')

    #   if (this.collectivite.type !== 'COM') {
    #     query = query.eq('collectivite_porteuse_id', this.collectivite.code)
    #   } else {
    #     query = query.contains('current_perimetre', `[{ "inseeCode": "${this.collectivite.code}" }]`)
    #   }

    #   const { data: procedures, error } = await query

    #   if (error) {
    #     // eslint-disable-next-line no-console
    #     console.log('error getProcedures', error)
    #   }
    #   if (procedures.length === 0) {
    #     return []
    #   }

    #   const collectiviteCodes = new Set(procedures.flatMap(p => [
    #     p.collectivite_porteuse_id,
    #     ...p.procedures_perimetres.map(c => c.collectivite_code)
    #   ]))

    #   // TODO :: Migrate this to Django once `groupements` and `membres` are available in `/api-internes/collectivites/`
    #   const { data: collectivites } = await axios({
    #     url: '/api/geo/collectivites',
    #     params: new URLSearchParams(collectiviteCodes.map(code => ['codes', code]))
    #   })

    #   const enrichedProcedures = procedures.map((p) => {
    #     const comd = p.procedures_perimetres.find(c => c.collectivite_type === 'COMD')

    #     const collectivite = collectivites.find((c) => {
    #       if (comd) {
    #         return c.code === comd.collectivite_code && c.type === 'COMD'
    #       } else if (p.procedures_perimetres.length === 1) {
    #         return c.code === p.procedures_perimetres[0].collectivite_code
    #       } else { return c.code === p.collectivite_porteuse_id }
    #     })

    #     if (collectivite && comd) {
    #       collectivite.intitule += ' COMD'
    #     }

    #     return {
    #       porteuse: collectivites.find(c => c.code === p.collectivite_porteuse_id),
    #       collectivite,
    #       ...p
    #     }
    #   })

    #   if (this.collectivite.type !== 'COM') {
    #     return enrichedProcedures.filter(e =>
    #       e.current_perimetre && e.current_perimetre.length > 1
    #     )
    #   } else {
    #     return enrichedProcedures
    #   }
