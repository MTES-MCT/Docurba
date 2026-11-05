<script>
import { mdiArrowRight, mdiPlus, mdiSubdirectoryArrowRight } from '@mdi/js'
import { displayDate } from '~/plugins/utils'
import { isMunicipalityInseeCode } from '~/store/territorialAuthority'

export default {
  data() {
    return {
      icons: {
        mdiArrowRight,
        mdiPlus,
        mdiSubdirectoryArrowRight,
      },
      loadingProcedures: true,
      loadingTerritorialAuthorities: true,
      proceduresByTerritorialAuthorityCode: [],
      territorialAuthorities: [],
    }
  },
  computed: {
    departmentCode: {
      get() {
        return this.$route.params.code_departement || ''
      },
      set(value) {
        this.$router.push({
          params: {
            ...this.$route.params,
            code_departement: value,
          },
        })
      },
    },
    intermunicipalities() {
      return this.territorialAuthorities.filter(({ code }) =>
        !isMunicipalityInseeCode(code),
      )
    },
    intermunicipalityCode: {
      get() {
        return this.$route.query.epci || ''
      },
      set(value) {
        this.$router.push({
          query: {
            ...this.$route.query,
            epci: value || undefined,
          },
        })
      },
    },
    intermunicipalityOptions() {
      return [{
        label: 'Tous les EPCIs',
        value: '',
      }, ...this.intermunicipalities.map(({ code, name }) => ({
        label: name,
        value: code,
      }))]
    },
    items() {
      return this.municipalitiesPage.flatMap((municipality) => {
        const toMunicipality = {
          name: 'dsfr-collectivites-code_collectivite',
          params: {
            code_collectivite: municipality.code,
          },
        }
        const items = [{
          approvalDate: '',
          id: municipality.code,
          name: municipality.name,
          prescriptionDate: '',
          row: {
            municipality: true,
          },
          secondary: false,
          status: '',
          to: toMunicipality,
          type: municipality.type,
        }]
        const procedures = municipality.code in this.proceduresByTerritorialAuthorityCode
          ? this.proceduresByTerritorialAuthorityCode[municipality.code]
            .filter(({ parentId }) => !parentId)
          : []

        if (procedures.length) {
          const selectedProcedures = [
            procedures.find(({ docType }) => docType !== 'SCoT'),
            procedures.find(({ docType }) => docType === 'SCoT'),
          ].filter(Boolean)

          items.push(...selectedProcedures.map((procedure, index) => ({
            approvalDate: displayDate(procedure.approvalDate),
            id: procedure.id,
            name: procedure.name ?? '',
            prescriptionDate: displayDate(procedure.prescriptionDate),
            row: {
              procedure: true,
            },
            secondary: true,
            status: procedure.status,
            to: {
              name: 'dsfr-procedures-id_procedure',
              params: {
                id_procedure: procedure.id,
              },
            },
            type: procedure.docType,
          })))

          const expandCount = procedures.length - selectedProcedures.length

          if (expandCount) {
            items.push({
              approvalDate: '',
              id: `${municipality.code}--expand`,
              name: `${expandCount} procédure${expandCount === 1 ? '' : 's'}`,
              prescriptionDate: '',
              row: {
                expand: true,
              },
              secondary: true,
              to: toMunicipality,
              type: '',
            })
          }
        }

        return items
      })
    },
    loading() {
      return this.loadingProcedures || this.loadingTerritorialAuthorities
    },
    municipalities() {
      return this.territorialAuthorities.filter(({ code, groups, higherGroups }) =>
        isMunicipalityInseeCode(code) && (
          !this.intermunicipalityCode
          || groups.some(({ code }) => code === this.intermunicipalityCode)
          || higherGroups.some(({ code }) => code === this.intermunicipalityCode)
        ),
      )
    },
    municipalitiesPage() {
      return this.municipalities.slice(
        (this.page - 1) * this.pageSize,
        this.page * this.pageSize,
      )
    },
    page() {
      const pageNumber = Number(this.$route.query.page)

      return (!Number.isNaN(pageNumber) && pageNumber) || 1
    },
    pageSize() {
      const pageSizeNumber = Number(this.$route.query.taille_page)

      return (!Number.isNaN(pageSizeNumber) && pageSizeNumber) || 10
    },
    pagesCount() {
      return this.municipalities.length
        ? Math.ceil(this.municipalities.length / this.pageSize)
        : 0
    },
  },
  watch: {
    departmentCode: {
      async handler(value) {
        if (!value) return

        this.loadingTerritorialAuthorities = true
        this.territorialAuthorities = await this.$store.dispatch('territorialAuthority/list', {
          departmentCode: value,
          includeGroups: true,
          includeHigherGroups: true,
        }),
        this.loadingTerritorialAuthorities = false
      },
      immediate: true,
    },
    municipalitiesPage: {
      async handler(value) {
        if (!value.length || value[0].departmentCode !== this.departmentCode) return

        this.loadingProcedures = true
        this.proceduresByTerritorialAuthorityCode = await this.$store.dispatch('procedure/list', {
          territorialAuthorityCodes: value.map(({ code }) => code),
        })
        this.loadingProcedures = false
      },
      immediate: true,
    },
    intermunicipalityOptions: {
      handler(value) {
        if (
          !value.length
          || value.some((option) => option.value === this.intermunicipalityCode)
        ) return

        this.$router.replace({
          query: {
            ...this.$route.query,
            epci: undefined,
          },
        })
      },
      immediate: true,
    },
  },
  methods: {
    exportMunicipalities() {
      // TODO :: Implement this
    },
    exportSCoTs() {
      // TODO :: Implement this
    },
  },
}
</script>

<template>
  <FRGrid>
    <FRHighlight>
      <FRContainer>
        <FRGrid gap="md lg-lg"
                size="md lg-xl">
          <FRText h1
                  tag="h1">
            Mes collectivités ({{ departmentCode }})
          </FRText>
          <FRGrid between
                  gap="md lg-lg">
            <FRButtons>
              <DUFieldDepartment id="filter-department"
                                 v-model="departmentCode" />
              <FRFieldAutocomplete id="filter-group"
                                   :options="intermunicipalityOptions"
                                   placeholder="Tous les EPCIs"
                                   v-model="intermunicipalityCode" />
            </FRButtons>
            <FRButtons>
              <FRButton tertiary
                        @actuated="exportMunicipalities()">
                Exporter les communes
              </FRButton>
              <FRButton tertiary
                        @actuated="exportSCoTs()">
                Exporter les SCoTs
              </FRButton>
            </FRButtons>
          </FRGrid>
        </FRGrid>
      </FRContainer>
    </FRHighlight>
    <FRContainer>
      <FRGrid v-if="!loading"
              gap="md lg-lg"
              size="md lg-lg">
        <FRTable v-if="items.length"
                 cols="14 5 5 5 fixed">
          <template #header>
            <FRTableCell>
              Nom
            </FRTableCell>
            <FRTableCell>
              Type
            </FRTableCell>
            <FRTableCell>
              Prescrit le
            </FRTableCell>
            <FRTableCell>
              Approuvé le
            </FRTableCell>
            <FRTableCell />
          </template>
          <template #default>
            <template >
              <FRTableRow v-for="item in items"
                          :key="item.id"
                          :secondary="item.secondary"
                          :title="item.name"
                          :to="item.to">
                <FRTableCell :link="item.row.expand">
                  <FRIcon v-if="!item.row.municipality"
                          :value="item.row.expand ? icons.mdiPlus : icons.mdiSubdirectoryArrowRight" />
                  <component :is="item.row.municipality ? 'strong' : 'span'">
                    {{ item.name }}
                  </component>
                  <DUProcedureStatus v-if="item.status"
                                     sm
                                     :value="item.status" />
                </FRTableCell>
                <FRTableCell>
                  <FRTag v-if="item.type"
                         actionable-child
                         sm>
                    {{ item.type }}
                  </FRTag>
                </FRTableCell>
                <FRTableCell>
                  {{ item.prescriptionDate }}
                </FRTableCell>
                <FRTableCell>
                  {{ item.approvalDate }}
                </FRTableCell>
                <FRTableCell link>
                  <FRIcon :value="icons.mdiArrowRight" />
                </FRTableCell>
              </FRTableRow>
            </template>
          </template>
        </FRTable>
        <FRText v-else
                center>
          Aucune collectivité ne correspond à cette sélection
        </FRText>
        <FRPagination :value="pagesCount" />
      </FRGrid>
    </FRContainer>
  </FRGrid>
</template>
