<script>
import { mdiInformationOutline, mdiOpenInNew } from '@mdi/js'
import { uniq } from 'lodash'
import { displayDate } from '~/plugins/utils'

export default {
  data () {
    return {
      entries: [],
      icons: {
        mdiInformationOutline,
        mdiOpenInNew
      },
      intermunicipalities: [],
      loading: true
    }
  },
  computed: {
    departmentCode () {
      return this.$route.params.departement || null
    },
    displayedEndDate () {
      return displayDate(this.$survey.endDate.toJSON())
    },
    entriesByType () {
      const entriesByType = {
        Other: [],
        SCoT: []
      }

      this.entries.forEach((entry) => {
        entriesByType[
          entry.procedure.documentType === 'SCoT'
            ? 'SCoT'
            : 'Other'
        ].push(entry)
      })

      return entriesByType
    },
    filteredTerritorialAuthorities () {
      return this.validationRequiredOnly
        ? this.validationRequiredTerritorialAuthorities
        : this.intermunicipalityCode
          ? this.territorialAuthorities.filter(({ intermunicipalityCode }) =>
            intermunicipalityCode === this.intermunicipalityCode
          )
          : this.territorialAuthorities
    },
    intermunicipalityCode: {
      get () {
        return this.$route.query.epci || ''
      },
      set (value) {
        this.$router.push({
          query: {
            ...this.$route.query,
            a_valider: undefined,
            epci: value || undefined
          }
        })
      }
    },
    intermunicipalityOptions () {
      const intermunicipalityOptions = []
      const availableIntermunicipalityCodes = Object.fromEntries(
        this.territorialAuthorities.map(
          ({ intermunicipalityCode }) => [intermunicipalityCode, true]
        )
      )

      this.intermunicipalities.forEach(({ code, name }) => {
        if (availableIntermunicipalityCodes[code]) {
          intermunicipalityOptions.push({
            label: name,
            value: code
          })
        }
      })

      return intermunicipalityOptions
    },
    page () {
      const pageNumber = Number(this.$route.query.page)

      return !Number.isNaN(pageNumber) && pageNumber ? pageNumber : 1
    },
    pageSize () {
      return this.intermunicipalityCode || this.validationRequiredOnly ? 0 : 10
    },
    pages () {
      return this.searchedTerritorialAuthorities.length && this.pageSize
        ? Math.ceil(this.searchedTerritorialAuthorities.length / this.pageSize)
        : 1
    },
    query: {
      get () {
        return this.$route.query.r || ''
      },
      set (value) {
        this.$router.push({
          query: {
            ...this.$route.query,
            r: value || undefined
          }
        })
      }
    },
    searchedTerritorialAuthorities () {
      if (!this.query) {
        return this.filteredTerritorialAuthorities
      }

      const normalizedQuery = this.query.toLowerCase()
        .normalize('NFKD')
        .replace(/[^a-z0-9]/g, '')

      return normalizedQuery
        ? this.filteredTerritorialAuthorities.filter(({ search }) =>
          search.includes(normalizedQuery)
        )
        : this.filteredTerritorialAuthorities
    },
    tabs () {
      return [{
        active: !this.$route.query.type,
        label: 'Procédures principales (hors SCoT)',
        to: {
          query: {
            ...this.$route.query,
            type: undefined
          }
        }
      }, {
        active: this.$route.query.type === 'scot',
        label: 'SCoT',
        to: {
          query: {
            ...this.$route.query,
            type: 'scot'
          }
        }
      }]
    },
    territorialAuthorities () {
      const proceduresByTerritorialAuthorityCode = {}

      this.entriesByType[this.type].forEach(({ procedure }) => {
        if (!procedure.territorialAuthority) {
          return
        }

        const code = procedure.territorialAuthority.code

        if (code in proceduresByTerritorialAuthorityCode) {
          proceduresByTerritorialAuthorityCode[code].push(procedure)
        } else {
          proceduresByTerritorialAuthorityCode[code] = [procedure]
        }
      })

      return Object.keys(proceduresByTerritorialAuthorityCode).sort((a, b) => {
        const aNumber = Number(a)
        const bNumber = Number(b)

        return aNumber === bNumber ? 0 : aNumber > bNumber ? 1 : -1
      }).map((code) => {
        const procedures = proceduresByTerritorialAuthorityCode[code]
        const territorialAuthority = procedures[0].territorialAuthority

        return {
          code,
          intermunicipalityCode: territorialAuthority.intermunicipalityCode,
          name: territorialAuthority.name,
          procedures: procedures.map(procedure => ({
            approvalDate: displayDate(procedure.approvalDate),
            documentType: procedure.documentType,
            id: procedure.id,
            name: procedure.name,
            prescriptionDate: displayDate(procedure.prescriptionDate),
            status: procedure.status,
            topicDetails: procedure.topicDetails,
            topics: procedure.topics
          })),
          search: `${code}${
            territorialAuthority.name.toLowerCase()
              .normalize('NFKD')
              .replace(/[^a-z0-9]/g, '')
          }`,
          type: territorialAuthority.type
        }
      })
    },
    territorialAuthoritiesPage () {
      return this.pageSize
        ? this.searchedTerritorialAuthorities
          .slice((this.page - 1) * this.pageSize, this.page * this.pageSize)
        : this.searchedTerritorialAuthorities
    },
    type () {
      return this.$route.query.type === 'scot'
        ? 'SCoT'
        : 'Other'
    },
    validationByCodeByType () {
      const validationByCodeByType = {
        Other: {},
        SCoT: {}
      }

      this.entries.forEach((entry) => {
        if (!entry.procedure.territorialAuthority) {
          return
        }

        const code = entry.procedure.territorialAuthority.code
        const type = entry.procedure.documentType === 'SCoT'
          ? 'SCoT'
          : 'Other'

        if (!(code in validationByCodeByType[type]) || (
          validationByCodeByType[type][code].validated &&
          !entry.validated
        )) {
          validationByCodeByType[type][code] = {
            respondant: entry.respondant,
            validated: entry.validated
          }
        }
      })

      return validationByCodeByType
    },
    validationRequiredCount () {
      return this.validationRequiredTerritorialAuthorities.length
    },
    validationRequiredOnly: {
      get () {
        return !!this.$route.query.a_valider
      },
      set (value) {
        this.$router.push({
          query: {
            ...this.$route.query,
            a_valider: value ? 'oui' : undefined,
            epci: undefined
          }
        })
      }
    },
    validationRequiredTerritorialAuthorities () {
      return this.territorialAuthorities.filter(({ code }) =>
        !this.validationByCodeByType[this.type][code] ||
        !this.validationByCodeByType[this.type][code].validated
      )
    }
  },
  watch: {
    departmentCode: {
      async handler (value) {
        if (!value) {
          return
        }

        this.loading = true
        this.entries = await this.$survey.getEntries({
          departmentCode: value
        })
        this.intermunicipalities = await this.$territorialAuthorityApi.list({
          codes: uniq(this.entries.map(entry =>
            entry.procedure.territorialAuthority?.intermunicipalityCode
          ).filter(Boolean))
        })
        this.loading = false
      },
      immediate: true
    }
  },
  created () {
    if (!this.$user.canViewProcedureSurvey()) {
      return this.$nuxt.context.redirect(302, '/')
    }
  },
  methods: {
    async toggleEntries (entries, validate) {
      const updatedEntries = await this.$survey.toggleEntries(
        entries.filter(({ validated }) => validated !== validate),
        validate
      )
      this.entries = this.entries.map(entry =>
        updatedEntries.find(({ id }) => id === entry.id) || entry
      )
    },
    toggleTerritorialAuthority (code, validate) {
      return this.toggleEntries(
        this.entries.filter(({ procedure }) =>
          procedure.territorialAuthority?.code === code
        ),
        validate
      )
    },
    validatePage () {
      const codes = this.territorialAuthoritiesPage.map(({ code }) => code)

      return this.toggleEntries(
        this.entries.filter(({ procedure }) =>
          codes.includes(procedure.territorialAuthority?.code)
        ),
        true
      )
    }
  }
}
</script>

<template>
  <LayoutMain highlighted>
    <DUGroup xs>
      <DUGroup
        lg
        pad-lg
      >
        <DUHeading :level="1">
          Enquête annuelle {{ $survey.year }}
        </DUHeading>
        <DUGroup
          start
          xs
        >
          <DUText>
            L’enquête annuelle sur l’état d’avancement des documents d’urbanisme est disponible sur Docurba jusqu’au {{ displayedEndDate }}
          </DUText>
          <DULink to="https://docurba.crisp.help/fr/article/1d1qw5l/">
            Consignes et astuces dans notre FAQ
            <VIcon small>
              {{ icons.mdiOpenInNew }}
            </VIcon>
          </DULink>
        </DUGroup>
      </DUGroup>
      <DUTabs :value="tabs">
        <DUGroup xl>
          <DUGroup
            between
            md
          >
            <DUGroup
              v-if="validationRequiredCount"
              horizontal
              md
            >
              <DUField
                id="filter-all"
                v-model="validationRequiredOnly"
                type="checkbox"
              >
                Afficher toutes les collectivités à valider ({{ validationRequiredCount }} restante{{ validationRequiredCount === 1 ? '' : 's' }})
              </DUField>
              <DUGroup
                v-if="intermunicipalityOptions.length"
                horizontal
                xs
              >
                <VAutocomplete
                  v-model="intermunicipalityCode"
                  clearable
                  dense
                  filled
                  hide-details
                  :items="intermunicipalityOptions"
                  item-text="label"
                  item-value="value"
                  placeholder="Tous les EPCIs"
                />
                <VIcon
                  class="du-page-survey__info"
                  title="Le filtre EPCI se base sur la géographie et non sur la compétence"
                >
                  {{ icons.mdiInformationOutline }}
                </VIcon>
              </DUGroup>
            </DUGroup>
            <DUAlert
              v-else
              sm
              success
            >
              {{ type === 'SCoT' ? 'Tous vos SCoT sont validés' : 'Toutes vos procédures (hors SCoT) sont validées' }}, félicitations !
            </DUAlert>
            <VTextField
              v-model="query"
              dense
              filled
              hide-details
              placeholder="Rechercher une collectivité"
            />
          </DUGroup>
          <DUGroup
            v-if="territorialAuthoritiesPage.length"
            md
          >
            <DUTable
              cols="5 2 5 3 3 3 3 9"
              top="142px"
            >
              <template #header>
                <DUTableCell>
                  {{ type === 'SCoT' ? 'Collectivité porteuse' : 'Nom' }}
                </DUTableCell>
                <DUTableCell>
                  Type
                </DUTableCell>
                <DUTableCell>
                  {{ type === 'SCoT' ? 'SCoT' : 'Procédures' }}
                </DUTableCell>
                <DUTableCell>
                  Statut
                </DUTableCell>
                <DUTableCell>
                  Prescrit le
                </DUTableCell>
                <DUTableCell>
                  Approuvé le
                </DUTableCell>
                <DUTableCell>
                  Objet
                </DUTableCell>
                <DUTableCell>
                  Enquête {{ $survey.year }}
                  <VIcon
                    small
                    title="Pour chaque collectivité, contrôlez les dates de prescription et d’approbation des procédures principales. Si tout est en ordre, validez l'état de la collectivité."
                  >
                    {{ icons.mdiInformationOutline }}
                  </VIcon>
                  <DUButton
                    v-if="validationRequiredCount"
                    sm
                    tertiary
                    @actuated="validatePage()"
                  >
                    Valider toute la page
                  </DUButton>
                </DUTableCell>
              </template>
              <template #default>
                <DUTableRow
                  v-for="territorialAuthority in territorialAuthoritiesPage"
                  :key="territorialAuthority.code"
                >
                  <DUTableCell :to="`/collectivites/${territorialAuthority.code}`">
                    <strong>
                      {{ territorialAuthority.code }} {{ territorialAuthority.name }}
                    </strong>
                  </DUTableCell>
                  <DUTableCell>
                    {{ territorialAuthority.type }}
                  </DUTableCell>
                  <DUTableGroup cols="5 3 3 3 3">
                    <DUTableRow
                      v-for="procedure in territorialAuthority.procedures"
                      :key="procedure.id"
                      secondary
                      :title="procedure.name"
                      :to="`/frise/${procedure.id}`"
                    >
                      <DUTableCell link>
                        <DUEllipsis tag="strong">
                          {{ procedure.name }}
                        </DUEllipsis>
                      </DUTableCell>
                      <DUTableCell>
                        <ProcedureStatus
                          v-if="procedure.status"
                          :value="procedure.status"
                        />
                      </DUTableCell>
                      <DUTableCell>
                        {{ procedure.prescriptionDate }}
                      </DUTableCell>
                      <DUTableCell>
                        {{ procedure.approvalDate }}
                      </DUTableCell>
                      <DUTableCell vertical>
                        <DUTag
                          v-for="topic in procedure.topics"
                          :key="topic"
                          sm
                          :title="topic === 'Autre' ? procedure.topicDetails : undefined"
                        >
                          {{ topic }}
                        </DUTag>
                      </DUTableCell>
                    </DUTableRow>
                  </DUTableGroup>
                  <DUTableCell>
                    <PageDepartementsEnqueteValidation
                      v-if="validationByCodeByType[type][territorialAuthority.code]"
                      :id="`validation--${territorialAuthority.code}`"
                      :procedures-count="territorialAuthority.procedures.length"
                      :respondant="validationByCodeByType[type][territorialAuthority.code].respondant"
                      :value="validationByCodeByType[type][territorialAuthority.code].validated"
                      @input="toggleTerritorialAuthority(
                        territorialAuthority.code,
                        !validationByCodeByType[type][territorialAuthority.code].validated
                      )"
                    />
                  </DUTableCell>
                </DUTableRow>
              </template>
            </DUTable>
            <LayoutPagination :size="pages" />
          </DUGroup>
          <DUText v-else-if="!loading">
            Aucune collectivité ne correspond à ces critères
          </DUText>
        </DUGroup>
      </DUTabs>
    </DUGroup>
  </LayoutMain>
</template>

<style>
.du-page-survey__info {
  color: #000091 !important;
}
</style>
