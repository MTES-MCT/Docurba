<script>
import { mdiFormatListBulleted, mdiMessageAlertOutline, mdiPlus, mdiViewColumnOutline } from '@mdi/js'
import { orderBy } from 'lodash'
import { displayProcedure } from '~/plugins/procedure'
import { displaySirenCode } from '~/plugins/territorial-authority'
import { getSortableText } from '~/plugins/utils'

export default {
  data () {
    return {
      icons: {
        mdiMessageAlertOutline,
        mdiPlus,
        mdiFormatListBulleted,
        mdiViewColumnOutline
      },
      intermunicipality: null,
      pageSize: 10,
      procedures: [],
      proceduresLoading: false,
      territorialAuthority: null
    }
  },
  computed: {
    breadcrumb () {
      if (!this.departmentCode) {
        return []
      }

      const breadcrumb = []

      if (this.$user.canViewSectionCollectivites({ departement: this.departmentCode })) {
        breadcrumb.push({
          label: `Mes collectivités (${this.departmentCode})`,
          value: `/ddt/${this.departmentCode}/collectivites`
        })
      }
      if (this.intermunicipality) {
        breadcrumb.push({
          label: this.intermunicipality.name,
          value: {
            params: {
              code_collectivite: this.intermunicipalityCode
            },
            query: {
              vue: this.$route.query.vue
            }
          }
        })
      }

      return breadcrumb
    },
    departmentCode () {
      return this.territorialAuthority?.departmentCode || null
    },
    displayedCode () {
      return this.territorialAuthority
        ? this.territorialAuthority.inseeCode
          ? `Code INSEE ${this.territorialAuthority.inseeCode}`
          : `SIREN ${displaySirenCode(this.territorialAuthority.sirenCode)}`
        : ''
    },
    displayedProcedures () {
      if (!(this.selection in this.proceduresBySelection)) {
        return []
      }

      const displayedProcedures = this.proceduresBySelection[this.selection]
        .map(displayProcedure)

      return this.intermunicipalityCode || this.selection !== 'plu'
        ? displayedProcedures
        : orderBy(displayedProcedures, [
          ({ townName }) => townName ? 1 : 2,
          ({ townName }) => getSortableText(townName)
        ], ['asc', 'asc'])
    },
    intermunicipalityCode () {
      return this.territorialAuthority?.intermunicipalityCode || null
    },
    label () {
      return this.territorialAuthority?.name || ''
    },
    membersActive: {
      get () {
        return this.$route.query.perimetre === this.territorialAuthorityCode
      },
      set (newValue) {
        this.$router.push({
          query: {
            ...this.$route.query,
            perimetre: newValue ? this.territorialAuthorityCode : undefined
          }
        })
      }
    },
    menu () {
      const menu = []

      for (const [label, selection] of [
        ['PLUi', 'plui'],
        ['DU communaux', 'plu'],
        ['SCoT', 'scot']
      ]) {
        if (this.proceduresBySelection[selection]?.length) {
          menu.push({
            active: this.selection === selection,
            label,
            to: {
              query: {
                ...this.$route.query,
                details_procedures: undefined,
                page: undefined,
                procedures_secondaires: undefined,
                selection
              }
            }
          })
        }
      }

      return menu
    },
    page () {
      const pageNumber = Number(this.$route.query.page)

      return !Number.isNaN(pageNumber) && pageNumber ? pageNumber : 1
    },
    pages () {
      return this.displayedProcedures.length
        ? Math.ceil(this.displayedProcedures.length / this.pageSize)
        : 1
    },
    procedureCreationAvailable () {
      return this.$user.canCreateProcedure({
        collectivite: {
          code: this.territorialAuthorityCode,
          departementCode: this.departmentCode,
          intercommunaliteCode: this.intermunicipalityCode
        }
      })
    },
    proceduresBySelection () {
      const proceduresBySelection = {}

      this.procedures.forEach((procedure) => {
        const procedureSelection = ['SCoT', 'SD'].includes(procedure.documentType)
          ? 'scot'
          : `plu${procedure.towns.length > 1 ? 'i' : ''}`

        if (procedureSelection in proceduresBySelection) {
          proceduresBySelection[procedureSelection].push(procedure)
        } else {
          proceduresBySelection[procedureSelection] = [procedure]
        }
      })

      return proceduresBySelection
    },
    proceduresLabel () {
      switch (this.selection) {
        case 'plu':
          return 'Documents d\'urbanisme communaux'
        case 'plui':
          return 'Plans locaux d’urbanisme intercommunaux'
        case 'scot':
          return 'Schémas de cohérence territoriale'
        default:
          return ''
      }
    },
    proceduresPage () {
      return this.displayedProcedures
        .slice((this.page - 1) * this.pageSize, this.page * this.pageSize)
    },
    selection () {
      return this.$route.query.selection || null
    },
    territorialAuthorityCode () {
      return this.$route.params.code_collectivite || null
    }
  },
  watch: {
    intermunicipalityCode: {
      async handler (value) {
        if (!process.client) {
          return
        }

        this.intermunicipality = value
          ? await this.$territorialAuthorityApi.get(value)
          : null
      },
      immediate: true
    },
    proceduresBySelection: {
      handler (value) {
        if (
          !this.procedures.length ||
          (this.selection && value[this.selection]?.length)
        ) {
          return
        }
        for (const selection of ['plui', 'plu', 'scot']) {
          if (value[selection]?.length) {
            return this.$router.replace({
              query: {
                ...this.$route.query,
                selection
              }
            })
          }
        }
      },
      immediate: true
    },
    territorialAuthorityCode: {
      async handler (value) {
        if (!process.client) {
          return
        }

        this.territorialAuthority = value
          ? await this.$territorialAuthorityApi.get(value, { includeMembers: true })
          : null

        if (this.territorialAuthority) {
          const codes = []
          const existingCodes = {}

          for (const { code, type } of [
            this.territorialAuthority,
            ...this.territorialAuthority.members
          ]) {
            if (type === 'COM' && !existingCodes[code]) {
              existingCodes[code] = true
              codes.push(code)
            }
          }

          this.proceduresLoading = true
          this.procedures = await this.$procedureApi.listForTerritorialAuthorities(codes)
          this.proceduresLoading = false
        } else {
          this.procedures = []
        }
      },
      immediate: true
    }
  },
  methods: {
    openIssueReportPopup () {
      if (!this.$user.id) {
        return
      }

      window.Tally.openPopup('3qjW27', {
        hiddenFields: {
          collectivite_id: this.$user.profile.collectivite_id,
          departement: this.$user.profile.departement,
          email: this.$user.email,
          side: this.$user.profile.side
        },
        hideTitle: true,
        width: 500
      })
    }
  }
}
</script>

<template>
  <LayoutMain
    v-if="territorialAuthority"
    :breadcrumb="breadcrumb"
    :label="label"
    :menu="menu"
    top="94px"
  >
    <template #infos>
      <li>{{ displayedCode }}</li>
      <li v-if="territorialAuthority.members.length">
        <PageDepartementsCollectivitesTowns
          v-model="membersActive"
          :label="label"
          :towns="territorialAuthority.members"
        >
          Périmètre&nbsp;: {{ territorialAuthority.members.length }} membre{{ territorialAuthority.members.length === 1 ? '' : 's' }}
        </PageDepartementsCollectivitesTowns>
      </li>
      <li>
        <DULink :to="`/collectivites/${territorialAuthorityCode}/informations`">
          Plus d'informations
        </DULink>
      </li>
    </template>
    <template
      v-if="$user.id"
      #actions
    >
      <DUButton
        tertiary
        @actuated="openIssueReportPopup()"
      >
        <VIcon small>
          {{ icons.mdiMessageAlertOutline }}
        </VIcon>
        Signaler un problème
      </DUButton>
      <DUButton
        v-if="procedureCreationAvailable"
        primary
        :to="`/ddt/${departmentCode}/collectivites/${territorialAuthorityCode}/procedures/add`"
      >
        <VIcon small>
          {{ icons.mdiPlus }}
        </VIcon>
        Ajouter une procédure
      </DUButton>
    </template>
    <template
      v-if="proceduresPage.length"
      #default
    >
      <DUHeading>{{ proceduresLabel }}</DUHeading>
      <DUText>Date du dernier import Sudocuh&nbsp;: 16/12/2025</DUText>
      <DUGroup start>
        <DUTabs>
          <template #default="{ activeClass }">
            <NuxtLink
              :class="{ [activeClass]: !$route.query.vue }"
              :to="{
                query: {
                  ...$route.query,
                  vue: undefined
                }
              }"
            >
              <VIcon small>
                {{ icons.mdiFormatListBulleted }}
              </VIcon>
              Liste
            </NuxtLink>
            <NuxtLink
              :class="{ [activeClass]: $route.query.vue === 'tableau' }"
              :to="{
                query: {
                  ...$route.query,
                  details_procedures: undefined,
                  procedures_secondaires: undefined,
                  vue: 'tableau'
                }
              }"
            >
              <VIcon small>
                {{ icons.mdiViewColumnOutline }}
              </VIcon>
              Tableau
            </NuxtLink>
          </template>
        </DUTabs>
      </DUGroup>
      <PageDepartementsCollectivitesProceduresTable
        v-if="$route.query.vue === 'tableau'"
        :value="proceduresPage"
      />
      <template v-else>
        <PageDepartementsCollectivitesProcedure
          v-for="procedure in proceduresPage"
          :key="procedure.id"
          :value="procedure"
        />
      </template>
      <DUGroup
        :end="pages > 1"
        lg
        :start="pages === 1"
      >
        <LayoutPagination :size="pages" />
        <LayoutScrollTop />
      </DUGroup>
    </template>
    <template
      v-else-if="!proceduresLoading"
      #default
    >
      <DUHeading>Documents d'urbanisme</DUHeading>
      <DUText>Cette collectivité n'a pas de documents d'urbanisme sous sa compétence</DUText>
    </template>
  </LayoutMain>
</template>
