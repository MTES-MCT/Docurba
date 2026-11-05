<script>
import { mdiMagnify, mdiPlus } from '@mdi/js'
import { uniq } from 'lodash'
import { displayDate } from '~/plugins/utils'
import { accessDepartments, accessProcedureCreation } from '~/store/auth'
import { ProcedureStatus } from '~/store/procedure'

export default {
  data() {
    return {
      eventTypeNameById: {},
      icons: {
        mdiMagnify,
        mdiPlus,
      },
      loadingEventTypes: true,
      loadingProcedures: true,
      loadingTerritorialAuthorities: true,
      procedures: [],
      territorialAuthorities: [],
    }
  },
  computed: {
    accessDepartments() {
      return accessDepartments(this.$store.getters['auth/user'])
    },
    accessProcedureCreation() {
      return accessProcedureCreation(this.$store.getters['auth/user'], {
        departmentCode: this.departmentCode,
      })
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
    docTypeOptions() {
      return [{
        label: 'CC',
        value: 'cc',
      }, {
        label: 'PLU',
        value: 'plu',
      }, {
        label: 'PLUi',
        value: 'plui',
      }, {
        label: 'PLUiH',
        value: 'pluih',
      }, {
        label: 'PLUiHM',
        value: 'pluihm',
      }, {
        label: 'PLUiM',
        value: 'pluim',
      }, {
        label: 'SCoT',
        value: 'scot',
      }]
    },
    docTypes: {
      get() {
        return this.$route.query.type_documents
          ? this.$route.query.type_documents.split(',')
          : []
      },
      set(value) {
        this.$router.push({
          query: {
            ...this.$route.query,
            type_documents: value.length ? value.join(',') : undefined,
          },
        })
      },
    },
    filteredProcedures() {
      // TODO :: Implement this
      return this.procedures
    },
    items() {
      return this.proceduresPage.map((procedure) => ({
        approvalDate: displayDate(procedure.approvalDate),
        id: procedure.id,
        lastEvent: procedure.lastEvent
          ? {
            date: displayDate(procedure.lastEvent),
            typeName: this.eventTypeNameById[procedure.lastEvent.typeId] || '',
          }
          : null,
        name: procedure.name,
        prescriptionDate: displayDate(procedure.prescriptionDate),
        status: procedure.status,
        towns: procedure.townCodes.map((code) =>
          this.territorialAuthorities.find((territorialAuthority) =>
            territorialAuthority.code === code
          )
        ),
      }))
    },
    loading() {
      return (
        this.loadingEventTypes
        || this.loadingProcedures
        || this.loadingTerritorialAuthorities
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
      return this.filteredProcedures.length
        ? Math.ceil(this.filteredProcedures.length / this.pageSize)
        : 0
    },
    perimeterId() {
      return this.$route.query.perimetre || null
    },
    proceduresPage() {
      return this.filteredProcedures.slice(
        (this.page - 1) * this.pageSize,
        this.page * this.pageSize,
      )
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
    searchableProcedures() {
      return this.procedures.map(({ name }) =>
        name.toLowerCase().normalize('NFKD').replaceAll(/[^a-z0-9]/g, '')
      )
    },
    statuses: {
      get() {
        return this.$route.query.statuts
          ? this.$route.query.statuts.split(',').map((status) => {
            switch (status) {
              case 'abandonne':
                return ProcedureStatus.Abandoned
              case 'abroge':
                return ProcedureStatus.Repealed
              case 'annule':
                return ProcedureStatus.Canceled
              case 'approuve':
                return ProcedureStatus.Approved
              case 'caduc':
                return ProcedureStatus.Obsolete
              case 'en-cours':
                return ProcedureStatus.InProgress
              case 'en-projet':
                return ProcedureStatus.InPlanning
              case 'opposable':
                return ProcedureStatus.Opposable
              case 'precedent':
                return ProcedureStatus.Previous
              default:
                return null
            }
          })
          : []
      },
      set(value) {
        this.$router.push({
          query: {
            ...this.$route.query,
            statuts: value.length
              ? value.map((status) => {
                switch (status) {
                  case ProcedureStatus.Abandoned:
                    return 'abandonne'
                  case ProcedureStatus.Approved:
                    return 'approuve'
                  case ProcedureStatus.Canceled:
                    return 'annule'
                  case ProcedureStatus.InPlanning:
                    return 'en-projet'
                  case ProcedureStatus.InProgress:
                    return 'en-cours'
                  case ProcedureStatus.Obsolete:
                    return 'caduc'
                  case ProcedureStatus.Opposable:
                    return 'opposable'
                  case ProcedureStatus.Previous:
                    return 'precedent'
                  case ProcedureStatus.Repealed:
                    return 'abroge'
                  default:
                    return ''
                }
              }).join(',')
              : undefined,
          },
        })
      },
    },
    typeOptions() {
      return [{
        label: 'Principale',
        value: 'principale',
      }, {
        label: 'Secondaire',
        value: 'secondaire',
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

        this.loadingProcedures = true
        this.procedures = await this.$store.dispatch('procedure/list', {
          departmentCode: value,
        })
        this.loadingProcedures = false
      },
      immediate: true,
    },
    proceduresPage: {
      async handler(value) {
        if (!value.length || value[0].departmentCode !== this.departmentCode) return

        this.loadingEventTypes = true
        this.loadingTerritorialAuthorities = true
        const [eventTypes, territorialAuthorities] = await Promise.all([
          this.$store.dispatch('eventType/list', {
            ids: uniq(
              value.map(({ lastEvent }) => !!lastEvent && lastEvent.typeId)
                .filter(Boolean)
            ),
          }),
          this.$store.dispatch('territorialAuthority/list', {
            codes: uniq(value.flatMap(({ townCodes }) => townCodes)),
          }),
        ])
        this.eventTypeNameById = Object.fromEntries(eventTypes.map(({ id, name }) => [
          id,
          name,
        ]))
        this.loadingEventTypes = false
        this.territorialAuthorities = territorialAuthorities
        this.loadingTerritorialAuthorities = false
      },
      immediate: true,
    },
  },
  methods: {
    closePerimeter() {
      this.$router.push({
        query: {
          ...this.$route.query,
          perimetre: undefined,
        },
      })
    },
  },
}
</script>

<template>
  <FRGrid alt>
    <FRContainer>
      <FRGrid gap="md lg-xl"
              size="md lg-xl">
        <FRGrid gap="md lg-xl"
                x-between
                y-end>
          <FRText h1
                  tag="h1">
            Mes procédures
          </FRText>
          <FRButton v-if="accessProcedureCreation"
                    :to="{
                      name: 'dsfr-departements-code_departement-procedures-creation',
                      params: {
                        code_departement: departmentCode,
                      },
                    }">
            <FRIcon :value="icons.mdiPlus" />
            Ajouter une procédure
          </FRButton>
        </FRGrid>
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
                           placeholder="Rechercher une procédure"
                           v-model="query" />
                </div>
                <div class="fr-col fr-col-md-3">
                  <FRFieldMultiselect id="filter-type"
                                      :options="typeOptions"
                                      placeholder="Tout type de procédure"
                                      v-model="types" />
                </div>
                <div class="fr-col fr-col-md-3">
                  <FRFieldMultiselect id="filter-doc-type"
                                      :options="docTypeOptions"
                                      placeholder="Tout type de document"
                                      v-model="docTypes" />
                </div>
                <div class="fr-col fr-col-md-2">
                  <DUFieldProcedureStatus id="filter-status"
                                          v-model="statuses" />
                </div>
              </div>
            </FRGrid>
            <template v-if="!loading">
              <FRTable v-if="items.length"
                       borderless
                       cols="7 3 3 3 5">
                <template #header>
                  <FRTableCell>
                    Nom
                  </FRTableCell>
                  <FRTableCell>
                    Nombre de communes
                  </FRTableCell>
                  <FRTableCell>
                    Prescrit le
                  </FRTableCell>
                  <FRTableCell>
                    Approuvé le
                  </FRTableCell>
                  <FRTableCell>
                    Dernier événement
                  </FRTableCell>
                </template>
                <template #default>
                  <template v-for="procedure in items">
                    <FRTableRow :key="procedure.id"
                                @actuated="$router.push({
                                  name: 'dsfr-procedures-id_procedure',
                                  params: {
                                    id_procedure: procedure.id,
                                  },
                                })">
                      <FRTableCell link>
                        <strong>
                          {{ procedure.name }}
                        </strong>
                        <DUProcedureStatus v-if="procedure.status"
                                           sm
                                           :value="procedure.status" />
                      </FRTableCell>
                      <FRTableCell>
                        <FRLink sm
                                :to="{
                                  query: {
                                    ...$route.query,
                                    perimetre: procedure.id,
                                  },
                                }"
                                @click.native.stop>
                          {{ procedure.towns.length }}
                        </FRLink>
                      </FRTableCell>
                      <FRTableCell>
                        {{ procedure.prescriptionDate }}
                      </FRTableCell>
                      <FRTableCell>
                        {{ procedure.approvalDate }}
                      </FRTableCell>
                      <FRTableCell v-if="procedure.lastEvent">
                        {{ procedure.lastEvent.date }}
                        -
                        {{ procedure.lastEvent.type }}
                      </FRTableCell>
                    </FRTableRow>
                    <FRModal v-if="procedure.id === perimeterId"
                             :key="`${procedure.id}--perimeter`"
                             @closed="closePerimeter()">
                      <FRGrid gap="xxs">
                        <FRText h4
                                light
                                tag="h4">
                          {{ procedure.name }}
                        </FRText>
                        <FRText h4>
                          Périmètre de la procédure&nbsp;: {{ procedure.towns.length }} commune{{ procedure.towns.length === 1 ? '' : 's' }}
                        </FRText>
                      </FRGrid>
                      <FRGrid gap="xs"
                              horizontal>
                        <FRLink v-for="town in procedure.towns"
                                :to="{
                                  name: 'dsfr-collectivites-code_collectivite',
                                  params: {
                                    code_collectivite: town.code,
                                  },
                                  query: {
                                    vue: $route.query.vue,
                                  },
                                }">
                          {{ town.name }} ({{ town.code }})
                        </FRLink>
                      </FRGrid>
                    </FRModal>
                  </template>
                </template>
              </FRTable>
              <FRText v-else
                      center>
                Aucune procédure ne correspond à cette sélection
              </FRText>
              <FRPagination :value="pagesCount" />
            </template>
          </FRGrid>
        </FRCard>
      </FRGrid>
    </FRContainer>
  </FRGrid>
</template>
