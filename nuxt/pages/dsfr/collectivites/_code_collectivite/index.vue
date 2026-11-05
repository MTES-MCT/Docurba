<script>
import {
  mdiFormatListBulleted,
  mdiMessageAlertOutline,
  mdiPlus,
  mdiViewColumnOutline,
} from '@mdi/js'
import { keyBy, orderBy, uniq } from 'lodash'
import { getSortableText } from '~/plugins/utils'
import { UserScope } from '~/store/auth'
import { displayTerritorialAuthorityCode } from '~/store/territorialAuthority'

export default {
  props: {
    breadcrumbRoot: {
      default: () => [],
      type: Array,
    },
    territorialAuthority: {
      default: null,
      type: Object,
    },
  },
  data() {
    return {
      icons: {
        mdiFormatListBulleted,
        mdiMessageAlertOutline,
        mdiPlus,
        mdiViewColumnOutline,
      },
      procedures: [],
    }
  },
  computed: {
    accessProcedureCreation() {
      return this.$store.getters['auth/accessProcedureCreation']({
        departmentCode: this.territorialAuthority.departmentCode,
        intercommunalityCode: this.territorialAuthority.intercommunalityCode,
        territorialAuthorityCode: this.territorialAuthority.code,
      })
    },
    displayedCode() {
      return displayTerritorialAuthorityCode(this.territorialAuthority)
    },
    favoriteView() {
      return this.signedIn && this.$store.getters['auth/user'].scope === UserScope.State
        ? 'tableau'
        : 'liste'
    },
    membersActive: {
      get() {
        return !!this.$route.query.membres
      },
      set(value) {
        this.$router.push({
          query: {
            ...this.$route.query,
            membres: value || undefined,
          },
        })
      },
    },
    menu() {
      const menu = []

      for (const [label, selection] of [
        ['PLUi', 'plui'],
        ['DU communaux', 'plu'],
        ['SCoT', 'scot'],
      ]) {
        if (!this.proceduresBySelection[selection].length) continue

        menu.push({
          active: this.selection === selection,
          label,
          to: {
            query: {
              ...this.$route.query,
              details: undefined,
              page: undefined,
              secondaires: undefined,
              selection,
            },
          },
        })
      }

      return menu
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
      return this.selection && this.selectedProcedures.length
        ? Math.ceil(this.selectedProcedures.length / this.pageSize)
        : 0
    },
    proceduresBySelection() {
      const proceduresBySelection = {
        'plu': [],
        'plui': [],
        'scot': [],
      }

      this.procedures.forEach((procedure) => {
        proceduresBySelection[
          ['SCoT', 'SD'].includes(procedure.docType)
            ? 'scot'
            : `plu${procedure.townCodes.length > 1 ? 'i' : ''}`
        ].push(procedure)
      })

      return proceduresBySelection
    },
    proceduresLabel() {
      switch (this.selection) {
        case 'plu':
          return 'Documents d\'urbanisme communaux'
        case 'plui':
          return 'Plans locaux d\'urbanisme intercommunaux'
        case 'scot':
          return 'Schémas de cohérence territoriale'
        default:
          return ''
      }
    },
    proceduresPage() {
      return this.selection
        ? this.selectedProcedures.slice(
          (this.page - 1) * this.pageSize,
          this.page * this.pageSize,
        )
        : []
    },
    selectedProcedures() {
      return this.selection in this.proceduresBySelection
        ? this.proceduresBySelection[this.selection]
        : []
    },
    selection() {
      return this.$route.query.selection || null
    },
    signedIn() {
      return this.$store.getters['auth/signedIn']
    },
    territorialAuthorityCode() {
      return this.territorialAuthority.code
    },
    view() {
      return this.$route.query.vue || null
    },
  },
  watch: {
    favoriteView: {
      handler() {
        if (this.view) return

        this.setDefaultValues()
      },
      immediate: true,
    },
    selectedProcedures: {
      handler(value) {
        if (value.length) return

        this.setDefaultValues()
      },
      immediate: true,
    },
    territorialAuthorityCode: {
      async handler(value) {
        if (!value) return

        let procedures = []

        try {
          procedures = await this.$store.dispatch('procedure/list', {
            territorialAuthorityCode: value,
          })
        } catch {
          return this.$store.dispatch(
            'alert/sendError',
            'La récupération de la liste des procédures a échoué.',
          )
        }

        const territorialAuthorityByCode = keyBy(await this.$store.dispatch('territorialAuthority/list', {
          codes: uniq(procedures.flatMap(({ territorialAuthorityCode, townCodes }) =>
            territorialAuthorityCode
              ? [territorialAuthorityCode, ...townCodes]
              : townCodes,
          )),
        }), 'code')
        const primaryProcedures = []
        const proceduresByParentId = {}

        procedures.forEach((procedure) => {
          const extendedProcedure = {
            ...procedure,
            territorialAuthority: (
              procedure.territorialAuthorityCode
              && territorialAuthorityByCode[procedure.territorialAuthorityCode]
            ) || null,
            towns: procedure.townCodes.map((townCode) =>
              territorialAuthorityByCode[townCode],
            ),
          }

          if (procedure.parentId) {
            if (procedure.parentId in proceduresByParentId) {
              proceduresByParentId[procedure.parentId].push(extendedProcedure)
            } else {
              proceduresByParentId[procedure.parentId] = [extendedProcedure]
            }
          } else {
            primaryProcedures.push(extendedProcedure)
          }
        })

        this.procedures = orderBy(primaryProcedures.map((procedure) => ({
          ...procedure,
          procedures: procedure.id in proceduresByParentId
            ? orderBy(proceduresByParentId[procedure.id], [
              ({ prescriptionDate }) => prescriptionDate || '0000-00-00',
              ({ lastUpdateDate }) => lastUpdateDate || '0000-00-00',
              ({ approvalDate }) => approvalDate || '0000-00-00',
            ], ['desc', 'desc', 'desc'])
            : [],
        })), [
          ({ territorialAuthority }) => getSortableText(
            territorialAuthority && territorialAuthority.name || ''
          ),
          ({ status }) => {
            switch (status) {
              case 'En cours':
                return 1
              case 'Opposable':
                return 2
              default:
                return 3
            }
          },
          ({ prescriptionDate }) => prescriptionDate || '0000-00-00',
          ({ lastUpdateDate }) => lastUpdateDate || '0000-00-00',
          ({ approvalDate }) => approvalDate || '0000-00-00',
        ], ['asc', 'asc', 'desc', 'desc', 'desc'])
      },
      immediate: true,
    },
  },
  methods: {
    setDefaultValues() {
      const patch = []

      if (this.favoriteView && !this.view) {
        patch.push(['vue', this.favoriteView])
      }
      if (!this.selectedProcedures.length) {
        const selection = ['plu', 'plui', 'scot'].find((selection) =>
          this.proceduresBySelection[selection].length
        )

        if (selection) {
          patch.push(['selection', selection])
        }
      }
      if (patch.every(([key, value]) => this.$route.query[key] === value)) return

      this.$router.replace({
        query: {
          ...this.$route.query,
          ...Object.fromEntries(patch),
        },
      })
    },
    openIssueReportPopup() {
      if (!this.signedIn) return

      const user = this.$store.getters['auth/user']

      window.Tally.openPopup('3qjW27', {
        hiddenFields: {
          collectivite_id: user.territorialAuthorityCode,
          departement: user.departmentCode,
          email: user.email,
          side: user.scope === UserScope.TerritorialAuthority
            ? 'collectivite'
            : 'etat',
        },
        hideTitle: true,
        width: 500,
      })
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
          <FRGrid gap="md">
            <FRBreadcrumb :value="breadcrumbRoot">
              {{ territorialAuthority.name }}
            </FRBreadcrumb>
            <FRText h1
                    tag="h1">
              {{ territorialAuthority.name }}
            </FRText>
          </FRGrid>
          <FRGrid between
                  gap="md lg-lg">
            <FRDottedList>
              <li>
                {{ displayedCode }}
              </li>
              <li v-if="territorialAuthority.members.length > 1">
                <FRLink :to="{
                          query: {
                            ...$route.query,
                            membres: true,
                          },
                        }">
                  Périmètre&nbsp;: {{ territorialAuthority.members.length }} membre{{ territorialAuthority.members.length === 1 ? '' : 's' }}
                </FRLink>
                <FRModal v-if="membersActive"
                        @closed="membersActive = false">
                  <FRGrid gap="xxs">
                    <FRText h4
                            light
                            tag="h4">
                      {{ territorialAuthority.name }}
                    </FRText>
                    <FRText h4>
                      Périmètre&nbsp;: {{ territorialAuthority.members.length }} commune{{ territorialAuthority.members.length === 1 ? '' : 's' }}
                    </FRText>
                  </FRGrid>
                  <FRGrid gap="xs"
                          horizontal>
                    <FRLink v-for="member in territorialAuthority.members"
                            :to="{
                              name: 'dsfr-collectivites-code_collectivite',
                              params: {
                                code_collectivite: member.code,
                              },
                              query: {
                                vue: $route.query.vue,
                              },
                            }">
                      {{ member.name }} ({{ member.code }})
                    </FRLink>
                  </FRGrid>
                </FRModal>
              </li>
              <li>
                <FRLink :to="{
                          name: 'dsfr-collectivites-code_collectivite-informations',
                          params: {
                            code_collectivite: this.territorialAuthority.code,
                          },
                        }">
                  Plus d'informations
                </FRLink>
              </li>
            </FRDottedList>
            <FRButtons v-if="signedIn">
              <FRButton tertiary
                        @actuated="openIssueReportPopup()">
                <FRIcon :value="icons.mdiMessageAlertOutline" />
                Signaler un problème
              </FRButton>
              <FRButton :to="{
                          name: 'dsfr-collectivites-code_collectivite-procedures-creation',
                          params: {
                            code_collectivite: territorialAuthority.code,
                          },
                        }">
                <FRIcon :value="icons.mdiPlus" />
                Ajouter une procédure
              </FRButton>
            </FRButtons>
          </FRGrid>
        </FRGrid>
      </FRContainer>
    </FRHighlight>
    <FRContainer>
      <FRGrid aside
              gap="md lg-lg"
              size="md lg-lg">
        <FRSidemenu :value="menu" />
        <FRGrid v-if="procedures.length"
                gap="md lg-lg">
          <FRGrid gap="md lg-lg">
            <FRGrid gap="md">
              <FRText h2
                      tag="h2">
                {{ proceduresLabel }}
              </FRText>
              <FRText mention
                      sm>
                Date du dernier import Sudocuh&nbsp;: 16/12/2025
              </FRText>
            </FRGrid>
            <FRGrid start>
              <FRTabs>
                <template #default="{ activeClass }">
                  <FRActionable :class="{ [activeClass]: view === 'liste' }"
                                :to="{
                                  query: {
                                    ...$route.query,
                                    vue: 'liste',
                                  },
                                }">
                    <FRIcon :value="icons.mdiFormatListBulleted" />
                    Liste
                  </FRActionable>
                  <FRActionable :class="{ [activeClass]: view === 'tableau' }"
                                :to="{
                                  query: {
                                    ...$route.query,
                                    details: undefined,
                                    secondaires: undefined,
                                    vue: 'tableau',
                                  },
                                }">
                    <FRIcon :value="icons.mdiViewColumnOutline" />
                    Tableau
                  </FRActionable>
                </template>
              </FRTabs>
            </FRGrid>
            <PageDsfrTerritorialAuthorityProceduresList v-if="view === 'liste'"
                                                        :value="proceduresPage" />
            <PageDsfrTerritorialAuthorityProceduresTable v-else
                                                         :value="proceduresPage" />
            <FRPagination :value="pagesCount" />
          </FRGrid>
        </FRGrid>
        <FRText v-else
                center>
          Aucun document n'est disponible
        </FRText>
      </FRGrid>
    </FRContainer>
  </FRGrid>
</template>
