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
      membersDialogVisible: false,
      pageSize: 10,
      procedures: [],
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
          value: {
            name: 'departements-code_departement-collectivites',
            params: {
              code_departement: this.departmentCode
            }
          }
        })
      }
      if (this.intermunicipality) {
        breadcrumb.push({
          label: this.intermunicipality.name,
          value: {
            params: {
              code_collectivite: this.intermunicipalityCode,
              code_departement: this.departmentCode
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
      return this.$route.params.code_departement?.padStart(2, '0') || null
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

          this.procedures = await this.$procedureApi.listForTerritorialAuthorities(codes)
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
      <PageDepartementsCollectivitesMembers
        v-if="territorialAuthority.members.length"
        :label="label"
        :value="territorialAuthority.members"
      />
      <li>
        <DULink
          :to="{
            name: 'departements-code_departement-collectivites-code_collectivite-informations',
            params: {
              code_collectivite: territorialAuthorityCode,
              code_departement: departmentCode
            }
          }"
        >
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
        :to="{
          name: 'departements-code_departement-collectivites-code_collectivite-procedures-ajout',
          params: {
            code_collectivite: territorialAuthorityCode,
            code_departement: departmentCode
          }
        }"
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
      <DUGroup start>
        <DUTabs>
          <template #default="{ activeClass }">
            <NuxtLink
              :class="{ [activeClass]: !$route.query.vue }"
              :to="{
                query: {
                  ...$route.query,
                  details_procedures: undefined,
                  procedures_secondaires: undefined,
                  vue: undefined
                }
              }"
            >
              <VIcon small>
                {{ icons.mdiViewColumnOutline }}
              </VIcon>
              Tableau
            </NuxtLink>
            <NuxtLink
              :class="{ [activeClass]: $route.query.vue === 'liste' }"
              :to="{
                query: {
                  ...$route.query,
                  vue: 'liste'
                }
              }"
            >
              <VIcon small>
                {{ icons.mdiFormatListBulleted }}
              </VIcon>
              Liste
            </NuxtLink>
          </template>
        </DUTabs>
      </DUGroup>
      <template v-if="$route.query.vue === 'liste'">
        <PageDepartementsCollectivitesProcedure
          v-for="procedure in proceduresPage"
          :key="procedure.id"
          :value="procedure"
        />
      </template>
      <PageDepartementsCollectivitesProceduresTable
        v-else
        :value="proceduresPage"
      />
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
      v-else
      #default
    >
      <DUHeading>Documents d'urbanisme</DUHeading>
      <DUText>Cette collectivité n'a pas de documents d'urbanisme sous sa compétence</DUText>
    </template>
  </LayoutMain>
</template>
