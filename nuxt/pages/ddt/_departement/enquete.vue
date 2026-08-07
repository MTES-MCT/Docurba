<template>
  <v-container>
    <v-row>
      <v-col
        cols="12"
        class="d-flex align-center justify-space-between"
      >
        <h1>Enquête ZAN</h1>
      </v-col>
      <v-col v-if="!collectivites" cols="12">
        <v-skeleton-loader
          type="table"
        />
      </v-col>
      <v-col v-else cols="12">
        <v-data-table
          v-model="selected"
          :headers="headers"
          :items="collectivitesToDisplay"
          :items-per-page="10"
          item-key="code"
          sort-by="code"
          sort-desc
          must-sort
          class="elevation-1 pa-8 collectivites-dt"
          :custom-filter="customFilter"
          :search="search"
          :loading="!collectivites"
          loading-text="Chargement des collectivités..."
          :show-select="hasValidationEnabled"
          selectable-key="isNotValidated"
        >
          <template #top>
            <v-alert v-if="hasValidationEnabled" type="info" color="primary" text>
              <div>
                <p>
                  L’enquête nationale sur l'intégration du ZAN dans les documents d'urbanisme (SCoT, PLU(i), carte communale) est disponible sur Docurba jusqu’au 24 avril 2026.
                  <a
                    href="https://docs.numerique.gouv.fr/docs/bb198862-0573-453c-8eba-90569f3d7de9/"
                    target="_blank"
                    rel="noreferrer noopener"
                  >
                    Attendus de la DGALN et notice d’utilisation
                  </a>.
                </p>
                <p>
                  <!-- eslint-disable-next-line no-irregular-whitespace -->
                  ℹ️ Les règles d’affichage des procédures dans l’onglet « Enquête ZAN » diffèrent de votre onglet habituel « Mes collectivités », les procédures y sont affichées uniquement sur la ligne de la collectivité porteuse de la procédure.
                </p>
                <v-expansion-panels flat light>
                  <v-expansion-panel focusable>
                    <v-expansion-panel-header color="primary lighten-4" class="font-weight-bold">
                      Quelles sont les procédures affichées dans cet onglet ?
                    </v-expansion-panel-header>
                    <v-expansion-panel-content color="primary lighten-4">
                      <ul>
                        <li>
                          Toutes les procédures principales en cours ou opposables, exceptées celles où la date d'approbation ou d'arrêt est antérieure au 22 août 2021,
                        </li>
                        <li>
                          Les modifications simplifiées dont le 1er événement a eu lieu après le 22 août 2020,
                        </li>
                        <li>
                          Les modifications simplifiées n’ayant aucun événement, si elles ont été créées après le 22 août 2020.
                        </li>
                        <li>
                          Les procédures contenant déjà l'objet « trajectoire ZAN », qu'elles répondent aux conditions précédentes, ou non.
                        </li>
                      </ul>
                    </v-expansion-panel-content>
                  </v-expansion-panel>
                </v-expansion-panels>
              </div>
            </v-alert>
            <div>
              <v-switch
                v-model="hideValidatedCollectives"
                color="primary"
                light
                inset
              >
                <template #label>
                  <span class="primary--text">
                    Voir seulement les collectivités à valider ({{ notValidatedCollectivites.length }} restantes)
                  </span>
                </template>
              </v-switch>
            </div>
            <v-row>
              <v-col v-if="$user.canViewMultipleDepartements()" cols="6" class="p-0">
                <VDeptAutocomplete
                  :default-departement-code="$route.params.departement"
                  :departements-filter="$user.profile.departements"
                  :hide-details="true"
                  :dense="true"
                  :with-label="false"
                  @input="navigateToDepartement"
                />
              </v-col>

              <v-col cols="6" class="p-0 mb-6 d-flex justify-space-between" :order="$user.canViewMultipleDepartements() ? 'last' : 'first'">
                <v-select
                  v-model="selectedCollectiviteTypesFilter"
                  flat
                  background-color="alt-beige"
                  hide-details
                  dense
                  solo
                  multiple
                  :items="collectiviteTypeFilterItems"
                  class="col-6"
                >
                  <template #selection="{item, index}">
                    <div v-if="collectiviteTypeFilterItems.length === selectedCollectiviteTypesFilter.length && index === 0">
                      Tout type de collectivité
                    </div>
                    <span v-else-if="collectiviteTypeFilterItems.length !== selectedCollectiviteTypesFilter.length">
                      {{ item.text }}<span v-if="index !== selectedCollectiviteTypesFilter.length - 1">,&nbsp;</span>
                    </span>
                  </template>
                </v-select>
                <v-select
                  v-model="filterEpci"
                  class="ml-2 col-6"
                  :items="searchEpcisItems"
                  placeholder="Tous les EPCIs"
                  item-value="code"
                  item-text="intitule"
                  flat
                  dense
                  background-color="alt-beige"
                  hide-details
                  solo
                  clearable
                >
                  <template #prepend-item>
                    <v-list-item>
                      <v-text-field
                        v-model="searchEpcis"
                        dense
                        outlined
                        label="Rechercher un EPCI..."
                      />
                    </v-list-item>
                  </template>
                </v-select>
              </v-col>
              <v-col cols="3" align-self="start" offset="3">
                <v-text-field
                  v-model="search"
                  outlined
                  hide-details
                  dense
                  label="Rechercher une collectivité..."
                />
              </v-col>
            </v-row>
          </template>

          <!-- eslint-disable-next-line -->
          <template #item.code="{ item }">
            <div class="my-5">
              <nuxt-link :to="`/ddt/${item.departementCode}/collectivites/${item.code}/${item.code.length > 5 ? 'epci' : 'commune'}`" class="text-decoration-none font-weight-bold">
                {{ item.code }} {{ item.intitule }}
              </nuxt-link>
            </div>
          </template>
          <!-- eslint-disable-next-line -->
                 <template #item.type="{ item }">
            <div class="my-5">
              {{ item.type }}
            </div>
          </template>
          <!-- eslint-disable-next-line -->
            <template #item.procedures="{ item }">
            <div class="my-5">
              <div v-if="!item.plans || item.plans.length === 0">
                <v-chip v-if="item.type === 'COM'" class="ml-2 error--text font-weight-bold" small label color="error-light">
                  RNU
                </v-chip>
                <span v-else>-</span>
              </div>
              <div v-for="plan in item.plans" :key="plan.procedure_id" class="mb-4">
                <div class="d-flex align-center">
                  <nuxt-link class="font-weight-bold text-decoration-none" :to="`/frise/${plan.procedure_id}`">
                    {{ $utils.formatProcedureName(plan, plan.collectiviteForProcedureName) }}
                  </nuxt-link>
                  <v-chip-group
                    v-if="plan.status"
                    column
                  >
                    <v-chip
                      :class="{
                        'success-light success--text': plan.status === 'opposable',
                        'bf200': plan.status === 'en cours',
                        'primary--text text--lighten-2': plan.status === 'en cours',
                      }"
                      class="font-weight-bold flex-shrink-0 ml-2"
                      small
                      label
                    >
                      {{ ['en cours', 'opposable'].includes(plan.status) ? plan.status.toUpperCase() : 'ARCHIVÉ' }}
                    </v-chip>
                  </v-chip-group>
                  <v-chip-group column>
                    <span v-if="plan.topics">
                      <ProceduresTopicChips :topics="plan.topics" :small="true" />
                    </span>
                  </v-chip-group>
                </div>
              </div>
            </div>
          </template>
          <!-- eslint-disable-next-line -->
          <template #item.scots="{ item }">
            <div v-if="!item.scots || item.scots.length === 0" class="my-6">
              -
            </div>

            <div class="my-5">
              <div v-if="!item.scots || item.scots.length === 0">
                -
              </div>
              <div v-else>
                <div v-for="scot in item.scots" :key="scot.procedure_id" class="mb-4">
                  <div class="d-flex align-center">
                    <nuxt-link class="font-weight-bold text-decoration-none" :to="`/frise/${scot.procedure_id}`">
                      {{ $utils.formatProcedureName(scot, scot.collectiviteForProcedureName) }}
                    </nuxt-link>
                    <v-chip-group
                      v-if="scot.status"
                      column
                    >
                      <v-chip
                        :class="{
                          'success-light success--text': scot.status === 'opposable',
                          'bf200': scot.status === 'en cours',
                          'primary--text text--lighten-2': scot.status === 'en cours',
                        }"
                        class="font-weight-bold flex-shrink-0 ml-2"
                        small
                        label
                      >
                        {{ ['en cours', 'opposable'].includes(scot.status) ? scot.status.toUpperCase() : 'ARCHIVÉ' }}
                      </v-chip>
                    </v-chip-group>
                    <v-chip-group column>
                      <span v-if="scot.topics">
                        <ProceduresTopicChips :topics="scot.topics" :small="true" />
                      </span>
                    </v-chip-group>
                  </div>
                </div>
              </div>
            </div>
          </template>

          <!-- eslint-disable-next-line -->
          <template #header.data-table-select="{ props, on }">
            <div class="d-flex align-center justify-center">
              <div>Valider</div>
              <v-checkbox
                v-bind="props"
                @change="on.input"
              />
            </div>
          </template>

          <!-- eslint-disable-next-line -->
          <template #item.data-table-select="{ item, isSelected, select}">
            <div class="d-flex align-end justify-end my-5">
              <v-tooltip v-if="item.isNotValidated" top>
                <template #activator="{ on, attrs }">
                  <div
                    v-bind="attrs"
                    v-on="on"
                  >
                    <v-checkbox
                      :input-value="isSelected"
                      @change="select"
                    />
                    <div />
                  </div>
                </template>
                <span>Valider la situation de <br> {{ item.code }} {{ item.intitule }}</span>
              </v-tooltip>
              <div v-else>
                <v-menu
                  top
                  offset-y
                  :close-on-content-click="false"
                >
                  <template #activator="{ on, attrs }">
                    <v-chip
                      v-bind="attrs"
                      class="bf200 primary--text text--lighten-2 ml-2 font-weight-bold"
                      small
                      label
                      v-on="on"
                    >
                      VALIDÉE
                    </v-chip>
                  </template>
                  <v-card class="pa-2">
                    <div class="text-center">
                      <div class="mb-2">
                        Collectivité validée le {{ item.respondedAt }}
                        par {{ item.respondantEmail }}
                      </div>
                      <v-btn
                        v-if="item.respondantEmail === $user.email || $user.profile.is_admin"
                        small
                        color="error"
                        text
                        @click="cancelValidation(item.code)"
                      >
                        Annuler la validation
                      </v-btn>
                    </div>
                  </v-card>
                </v-menu>
              </div>
            </div>
          </template>
        </v-data-table>
        <div
          v-if="selected.length > 0 "
          class="pa-6 elevation-4 validation-toolbar"
        >
          <div class="d-flex">
            <v-spacer />
            <v-btn color="primary" outlined @click="selected = []">
              Tout déselectionner
            </v-btn>
            <v-btn class="ml-2" color="primary" depressed @click="validateSelectedCollectivites">
              Valider {{ selected.length }} {{ selected.length === 1 ? 'collectivité': 'collectivités' }}
            </v-btn>
          </div>
        </div>
      </v-col>
    </v-row>
    <v-snackbar
      v-model="snackbar"
      top
      :color="snackVal.type"
      outlined
      min-width="800"
      :timeout="5000"
    >
      {{ snackVal.text }}
    </v-snackbar>
  </v-container>
</template>

<script>
import dayjs from 'dayjs'
import { partition } from 'lodash'

const docVersion = '1.0'

const SCOT_LIKE = ['SCOT', 'SD']

export default {
  name: 'CollectiviteDU',
  layout: 'ddt',
  data () {
    return {
      selected: [],
      searchEpcis: '',
      groupements: [],
      filterEpci: null,
      hasValidationEnabled: this.$user.canViewProcedureSurvey({ departement: this.$route.params.departement }),
      hideValidatedCollectives: false,
      snackbar: false,
      snackVal: { text: '', type: 'success' },
      validatedCollectivites: [],
      selectedCollectiviteTypesFilter: ['COM', 'CA', 'CC', 'EPT', 'SM', 'SIVU', 'PETR', 'CU', 'METRO'],
      collectiviteTypeFilterItems: [
        { text: 'Communes', value: 'COM' },
        { text: 'CA', value: 'CA' },
        { text: 'CC', value: 'CC' },
        { text: 'METRO', value: 'METRO' },
        { text: 'CU', value: 'CU' },
        { text: 'EPT', value: 'EPT' },
        { text: 'SM', value: 'SM' },
        { text: 'SIVU', value: 'SIVU' },
        { text: 'PETR', value: 'PETR' }
      ],
      search: this.$route.query.search || '',
      referentiel: null,
      clickedOnDocLink: true
    }
  },
  computed: {
    searchEpcisItems () {
      if (!this.searchEpcis) {
        return this.groupements
      }

      return this.groupements.filter((groupement) => {
        const normalizedGroupementIntitule = groupement.intitule.toLocaleLowerCase().normalize('NFKD').replace(/\p{Diacritic}/gu, '')
        const normalizedSearch = this.searchEpcis.toLocaleLowerCase().normalize('NFKD').replace(/\p{Diacritic}/gu, '')

        return normalizedGroupementIntitule.includes(normalizedSearch)
      })
    },
    headers () {
      const headers = [
        { text: 'Nom', align: 'start', value: 'code', filterable: true, width: '30%', sort (a, b) { return b.localeCompare(a) } },
        { text: 'Type', align: 'start', value: 'type', filterable: false, width: '10%' },
        { text: 'Procédures', value: 'procedures', filterable: false, sortable: false, width: '30%' },
        { text: 'SCOTs', value: 'scots', filterable: false, sortable: false, width: '30%' }
      ]
      if (this.hasValidationEnabled) {
        headers.push({ text: 'Valider', value: 'data-table-select' })
      }
      return headers
    },
    collectivites () {
      const selectedCode = this.filterEpci
      return this.referentiel?.filter((collectivite) => {
        return !!this.selectedCollectiviteTypesFilter.find(type => collectivite.type.includes(type))
      }).filter((collectivite) => {
        return (
          !selectedCode ||
          selectedCode === collectivite.code ||
          collectivite.groupements.some(c => c.code === selectedCode)
        )
      })
    },
    notValidatedCollectivites () {
      return this.collectivites.filter(collectivite => collectivite.isNotValidated)
    },
    collectivitesToDisplay () {
      if (this.hideValidatedCollectives) {
        return this.notValidatedCollectivites
      }
      return this.collectivites
    }
  },
  async mounted () {
    if (!this.$user.canViewProcedureSurvey({ departement: this.$route.params.departement })) {
      // eslint-disable-next-line no-console
      console.warn('User is not allowed to view this page.')
      this.$nuxt.context.redirect(302, '/')
    }

    const promCommunes = this.$djangoApi.get('/communes/', {
      departement: this.$route.params.departement
    })
    const promGroupements = this.$djangoApi.get('/collectivites/', {
      departement: this.$route.params.departement,
    })

    const [communes, groupements] = await Promise.all([promCommunes, promGroupements])

    // const collectivites = await this.$nuxt3api(`/api/geo/collectivites?departementCode=${this.$route.params.departement}`)
    // const communes = []
    // const groupements = []

    // collectivites.forEach((c) => {
    //   if (c.type === 'COM') {
    //     communes.push(c)
    //   }

    //   if (c.code.length > 5) {
    //     groupements.push(c)
    //   }
    // })
    this.groupements = groupements

    const { data: surveyProcedures } = await this.$zanSurvey.getProcedures(this.$route.params.departement)
    for (const surveyProcedure of surveyProcedures) {
      const perimetre = surveyProcedure.procedures_perimetres.filter(c => c.collectivite_type === 'COM')
      if (perimetre.length === 1) {
        surveyProcedure.collectiviteForProcedureName = communes.find(e => e.code === perimetre[0].collectivite_code)
      } else {
        surveyProcedure.collectiviteForProcedureName = groupements.find(e => e.code === surveyProcedure.collectivite_code)
      }
    }
    const enrichedCommunes = this.parseCommunes(communes, surveyProcedures)
    const enrichedGroups = this.parseGroupements(groupements, surveyProcedures)

    this.referentiel = [...enrichedGroups, ...enrichedCommunes].map((e) => {
      const procedures = [...e.plans, ...e.scots]
      const isNotValidated = procedures.some(e => e.is_validated === false)
      const respondantEmail = procedures.find(e => e.respondant_email !== null)?.respondant_email
      const respondedAt = procedures.find(e => e.responded_at !== null)?.responded_at
      return {
        isNotValidated,
        respondantEmail,
        respondedAt: this.formatDate(respondedAt),
        ...e
      }
    })
  },
  methods: {
    formatDate (date) {
      return dayjs(date).format('DD/MM/YYYY')
    },
    async cancelValidation (collectiviteCode) {
      const { success, error } = await this.$zanSurvey.cancelCollectiviteValidation(collectiviteCode)
      if (!success) {
        this.snackbar = true
        this.snackVal = { text: `ERREUR: ${error}`, type: 'error' }
      }
      for (const collectivite of this.referentiel) {
        if (collectivite.code === collectiviteCode) {
          collectivite.isNotValidated = true
          collectivite.respondantEmail = null
          collectivite.respondedAt = null
        }
      }
    },
    async validateSelectedCollectivites () {
      const collectivitesCodes = this.selected.map(e => e.code)
      const { success, error } = await this.$zanSurvey.validateCollectivites(collectivitesCodes)
      if (!success) {
        this.snackbar = true
        this.snackVal = { text: `ERREUR: ${error}`, type: 'error' }
      }
      const today = new Date().toISOString()
      for (const collectivite of this.referentiel) {
        if (collectivite.isNotValidated === true) {
          collectivite.isNotValidated = !collectivitesCodes.includes(collectivite.code)
          collectivite.respondantEmail = this.$user.email
          collectivite.respondedAt = this.formatDate(today)
        }
      }
      this.selected = []
    },
    parseCommunes (communes, surveyProcedures) {
      const communeCodes = surveyProcedures.filter(e => e.collectivite_code.length <= 5).map(e => e.collectivite_code)
      return communes.filter(e => communeCodes.includes(e.code)).map((commune) => {
        const communeProcedures = surveyProcedures.filter((surveyProcedure) => {
          return surveyProcedure.collectivite_code === commune.code
        })
        const [scots, plans] = partition(communeProcedures, p => SCOT_LIKE.includes(p.doc_type))
        return {
          ...commune,
          plans,
          scots
        }
      })
    },
    findCommunes (membres, groupements) {
      const communes = []

      membres.forEach((m) => {
        if (m.code.length > 5) {
          const group = groupements.find(g => g.code === m.code)
          if (group && group.membres) {
            communes.push(...this.findCommunes(group.membres, groupements))
          }
        } else {
          communes.push(m)
        }
      })

      return communes
    },
    parseGroupements (groupements, surveyProcedures) {
      const groupementsCodes = surveyProcedures.filter(e => e.collectivite_code.length > 5).map(e => e.collectivite_code)
      return groupements.filter(e => groupementsCodes.includes(e.code)).map((groupement) => {
      // return groupements.map((groupement) => {
        const groupementProcedures = surveyProcedures.filter((surveyProcedure) => {
          return surveyProcedure.collectivite_code === groupement.code ||
          groupement.membres.some(c => c.code === surveyProcedure.collectivite_code && c.type === 'COM')
        })
        const [scots, plans] = partition(groupementProcedures, p => SCOT_LIKE.includes(p.doc_type))
        return {
          ...groupement,
          plans: plans.filter(p => p.collectivite_code.length > 5),
          scots
        }
      })
    },
    customFilter (value, search, item) {
      if (!search?.length) { return true }
      const itemValue = item.intitule + item.code
      const normalizedValue = itemValue.toLocaleLowerCase().normalize('NFKD').replace(/\p{Diacritic}/gu, '')
      const normalizedSearch = search.toLocaleLowerCase().normalize('NFKD').replace(/\p{Diacritic}/gu, '')

      return normalizedValue.includes(normalizedSearch)
    },
    showClose () {
      this.clickedOnDocLink = true
      localStorage.setItem('docVersion', docVersion)
    },
    navigateToDepartement (departementObject) {
      if (!departementObject) {
        return
      }
      let departement = departementObject.code_departement.toString()
      departement = departement.padStart('2', '0')
      this.$router.push({ params: { departement } })
    }
  }
}
</script>

<style lang="scss">
.collectivites-dt {
  tr th{
    font-size: 14px !important;
    color: #000 !important;
  }
   tbody tr td{
    vertical-align: top !important;
   }
}

.tooltip-action-validate{
  background: red;
  opacity: 1;
}

.validation-toolbar{
  position: sticky;
  bottom:20px;
  width:95%;
  margin:auto;
  background:var(--v-primary-lighten4);
  border: 1px solid  var(--v-primary-base) !important;
  border-radius: 4px;
}

.v-item-group.v-expansion-panels, .v-item-group.v-expansion-panels .v-expansion-panel, .v-item-group.v-expansion-panels .v-expansion-panel-header, .v-item-group.v-expansion-panels .v-expansion-panel-content {
  transition: 0.3s min-height cubic-bezier(0.25, 0.8, 0.5, 1) !important;
}
</style>
