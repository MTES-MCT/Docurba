<script>
import { mdiArrowRight, mdiMagnify, mdiPlus, mdiSubdirectoryArrowRight } from '@mdi/js'
import { displayDate } from '~/plugins/utils'
import { accessDepartments } from '~/store/auth'
import { isMunicipalityInseeCode } from '~/store/territorialAuthority'

export default {
  data() {
    return {
      icons: {
        mdiArrowRight,
        mdiMagnify,
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
    accessDepartments() {
      return accessDepartments(this.$store.getters['auth/user'])
    },
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
    filteredMunicipalities() {
      const filterIntermunicipality = this.intermunicipalityCode
        ? ({ groups, higherGroups }) => (
          groups.some(({ code }) => code === this.intermunicipalityCode)
          || higherGroups.some(({ code }) => code === this.intermunicipalityCode)
        )
        : () => true
      const filterType = this.types.length
        ? ({ type }) => this.types.includes(type.toLowerCase())
        : () => true
      const searchableQuery = this.query
        ? this.query.toLowerCase().normalize('NFKD').replaceAll(/[^a-z0-9]/g, '')
        : ''
      const filterQuery = searchableQuery
        ? (index) => (
          this.searchableMunicipalities[index]
          && this.searchableMunicipalities[index].includes(searchableQuery)
        )
        : () => true

      return this.municipalities.filter((municipality, index) =>
        filterIntermunicipality(municipality)
        && filterQuery(index)
        && filterType(municipality)
      )
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
      return this.municipalitiesPage.map((municipality) => {
        const item = {
          code: municipality.code,
          expandProceduresCount: 0,
          expandScotsCount: 0,
          name: municipality.name,
          procedures: [],
          scots: [],
          type: municipality.type,
        }
        const procedures = municipality.code in this.proceduresByTerritorialAuthorityCode
            ? this.proceduresByTerritorialAuthorityCode[municipality.code]
              .filter(({ parentId }) => !parentId)
            : []
        procedures.forEach((procedure) => {
          const parsedProcedure = {
            approvalDate: displayDate(procedure.approvalDate),
            id: procedure.id,
            name: procedure.name ?? '',
            prescriptionDate: displayDate(procedure.prescriptionDate),
            status: procedure.status,
          }

          if (procedure.docType === 'SCoT') {
            if (item.scots.length < 2) {
              item.scots.push(parsedProcedure)
            } else {
              item.expandScotsCount += 1
            }
          } else {
            if (item.procedures.length < 2) {
              item.procedures.push(parsedProcedure)
            } else {
              item.expandProceduresCount += 1
            }
          }
        })

        return item
      })
    },
    loading() {
      return this.loadingProcedures || this.loadingTerritorialAuthorities
    },
    municipalities() {
      return this.territorialAuthorities.filter(({ code }) => isMunicipalityInseeCode(code))
    },
    municipalitiesPage() {
      return this.filteredMunicipalities.slice(
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
      return this.filteredMunicipalities.length
        ? Math.ceil(this.filteredMunicipalities.length / this.pageSize)
        : 0
    },
    query: {
      get() {
        return this.$route.query.r || ''
      },
      set(value) {
        this.$router.push({
          query: {
            ...this.$route.query,
            r: value || undefined,
          },
        })
      },
    },
    searchableMunicipalities() {
      return this.municipalities.map(({ name }) =>
        name.toLowerCase().normalize('NFKD').replaceAll(/[^a-z0-9]/g, '')
      )
    },
    typeOptions() {
      return [{
        label: 'Commune',
        value: 'com',
      }, {
        label: 'CA',
        value: 'ca',
      }, {
        label: 'CC',
        value: 'cc',
      }, {
        label: 'CU',
        value: 'cu',
      }, {
        label: 'EPT',
        value: 'ept',
      }, {
        label: 'METRO',
        value: 'metro',
      }, {
        label: 'PETR',
        value: 'petr',
      }, {
        label: 'SIVU',
        value: 'sivu',
      }, {
        label: 'SM',
        value: 'sm',
      }]
    },
    types: {
      get() {
        return this.$route.query.types
          ? this.$route.query.types.split(',')
          : []
      },
      set(value) {
        this.$router.push({
          query: {
            ...this.$route.query,
            types: value.length ? value.join(',') : undefined,
          },
        })
      },
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
}
</script>

<template>
  <FRGrid alt>
    <FRContainer>
      <FRGrid gap="md lg-xl"
              size="md lg-xl">
        <FRText h1
                tag="h1">
          Mes collectivités
        </FRText>
        <FRCard>
          <FRGrid gap="md lg-xl">
            <FRGrid gap="md lg-lg">
              <div v-if="accessDepartments"
                   class="fr-row">
                <div class="fr-col fr-col-md-4">
                  <DUFieldDepartment id="filter-department"
                                     placeholder="Département"
                                     v-model="departmentCode" />
                </div>
              </div>
              <div class="fr-row">
                <div class="fr-col fr-col-md-4">
                  <FRField :icon="icons.mdiMagnify"
                           id="filter-query"
                           placeholder="Rechercher une collectivité"
                           v-model="query" />
                </div>
                <div class="fr-col fr-col-md-3">
                  <FRFieldMultiselect id="filter-type"
                                      :options="typeOptions"
                                      placeholder="Tout type de collectivité"
                                      v-model="types" />
                </div>
                <div class="fr-col fr-col-md-3">
                  <FRFieldAutocomplete id="filter-intermunicipality"
                                       :options="intermunicipalityOptions"
                                       placeholder="Tous les EPCIs"
                                       v-model="intermunicipalityCode" />
                </div>
              </div>
            </FRGrid>
            <template v-if="!loading">
              <FRTable v-if="items.length"
                       cols="5 2 7 3 3 7">
                <template #header>
                  <FRTableCell>
                    Nom
                  </FRTableCell>
                  <FRTableCell>
                    Type
                  </FRTableCell>
                  <FRTableCell>
                    Procédures
                  </FRTableCell>
                  <FRTableCell>
                    Prescrit le
                  </FRTableCell>
                  <FRTableCell>
                    Approuvé le
                  </FRTableCell>
                  <FRTableCell>
                    SCoTs
                  </FRTableCell>
                </template>
                <template #default>
                  <FRTableRow v-for="item in items"
                              :key="item.code">
                    <FRTableGroup cols="5 2">
                      <FRTableRow :to="{
                                    name: 'dsfr-collectivites-code_collectivite',
                                    params: {
                                      code_collectivite: item.code,
                                    },
                                  }">
                        <FRTableCell link>
                          <strong>
                            {{ item.name }}
                          </strong>
                        </FRTableCell>
                        <FRTableCell>
                          <FRTag sm>
                            {{ item.type }}
                          </FRTag>
                        </FRTableCell>
                      </FRTableRow>
                    </FRTableGroup>
                    <FRTableGroup cols="7 3 3">
                      <FRTableRow v-for="procedure in item.procedures"
                                  :key="procedure.id"
                                  secondary
                                  :to="{
                                    name: 'dsfr-procedures-id_procedure',
                                    params: {
                                      id_procedure: procedure.id,
                                    },
                                  }">
                        <FRTableCell link>
                          <strong>
                            {{ procedure.name }}
                          </strong>
                          <DUProcedureStatus v-if="procedure.status"
                                             sm
                                             :value="procedure.status" />
                        </FRTableCell>
                        <FRTableCell>
                          {{ procedure.prescriptionDate }}
                        </FRTableCell>
                        <FRTableCell>
                          {{ procedure.approvalDate }}
                        </FRTableCell>
                      </FRTableRow>
                      <FRTableRow v-if="item.expandProceduresCount"
                                  secondary
                                  :to="{
                                    name: 'dsfr-collectivites-code_collectivite',
                                    params: {
                                      code_collectivite: item.code,
                                    },
                                  }">
                        <FRTableCell link>
                          <FRIcon :value="icons.mdiPlus" />
                          <strong>
                            {{ item.expandProceduresCount }} procédure{{ item.expandProceduresCount === 1 ? '' : 's' }}
                          </strong>
                        </FRTableCell>
                      </FRTableRow>
                    </FRTableGroup>
                    <FRTableGroup>
                      <FRTableRow v-for="procedure in item.scots"
                                  :key="procedure.id"
                                  secondary
                                  :to="{
                                    name: 'dsfr-procedures-id_procedure',
                                    params: {
                                      id_procedure: procedure.id,
                                    },
                                  }">
                        <FRTableCell link>
                          <strong>
                            {{ procedure.name }}
                          </strong>
                          <DUProcedureStatus v-if="procedure.status"
                                             sm
                                             :value="procedure.status" />
                        </FRTableCell>
                      </FRTableRow>
                      <FRTableRow v-if="item.expandScotsCount"
                                  secondary
                                  :to="{
                                    name: 'dsfr-collectivites-code_collectivite',
                                    params: {
                                      code_collectivite: item.code,
                                    },
                                  }">
                        <FRTableCell link>
                          <FRIcon :value="icons.mdiPlus" />
                          <strong>
                            {{ item.expandScotsCount }} SCoT{{ item.expandScotsCount === 1 ? '' : 's' }}
                          </strong>
                        </FRTableCell>
                      </FRTableRow>
                    </FRTableGroup>
                  </FRTableRow>
                </template>
              </FRTable>
              <FRText v-else
                      center>
                Aucune collectivité ne correspond à cette sélection
              </FRText>
              <FRPagination :value="pagesCount" />
            </template>
          </FRGrid>
        </FRCard>
      </FRGrid>
    </FRContainer>
  </FRGrid>
</template>
