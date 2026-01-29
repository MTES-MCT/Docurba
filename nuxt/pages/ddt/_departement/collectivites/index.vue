<template>
  <v-container>
    <v-row>
      <v-col
        cols="12"
        class="d-flex align-center justify-space-between"
      >
        <h1>Mes collectivités - {{ $route.params.departement }}</h1>
        <div>
          <v-btn
            outlined
            color="primary"
            class="mr-2"
            :loading="exportingCommunes"
            @click="exportCommunes"
          >
            Exporter les communes
          </v-btn>
          <v-btn
            outlined
            color="primary"
            class="mr-2"
            :loading="exportingSCoTs"
            @click="exportSCoTs"
          >
            Exporter les SCoTs
          </v-btn>
        </div>
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
              <div class="text-h5 text-weight-bold">
                Enquête annuelle
              </div>
              <div>
                L’enquête annuelle sur l’état d’avancement des documents d’urbanisme est disponible sur Docurba jusqu’au <span style="font-weight: bold;">13 février 2026</span>. <a href="https://docurba.crisp.help/fr/article/a-venir-conditions-de-lenquete-annuelle-2025-tout-ce-quil-faut-savoir-agents-de-ddtmdeal-13m8qu9/">Consignes et astuces dans notre FAQ</a>.
              </div>
              <div>
                <v-switch
                  v-model="hideValidatedCollectives"
                  color="primary"
                  dark
                  inset
                >
                  <template #label>
                    <span class="primary--text">
                      Voir seulement les collectivités à valider ({{ notValidatedCollectivites.length }} restantes)
                    </span>
                  </template>
                </v-switch>
              </div>
            </v-alert>
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
              <div v-for="(plan, index) in item.plans" :key="plan.id" class="mb-4">
                <template v-if="index < 2">
                  <div class="d-flex align-center">
                    <nuxt-link class="font-weight-bold text-decoration-none" :to="`/frise/${plan.id}`">
                      {{ $utils.formatProcedureName(plan, item) }}
                    </nuxt-link>
                    <v-chip
                      :class="{
                        'success-light': plan.inContextStatus === 'OPPOSABLE',
                        'success--text': plan.inContextStatus === 'OPPOSABLE',
                        'bf200': plan.inContextStatus === 'EN COURS',
                        'primary--text': plan.inContextStatus === 'EN COURS',
                        'text--lighten-2': plan.inContextStatus === 'EN COURS',

                      }"
                      class="font-weight-bold flex-shrink-0 ml-2"
                      small
                      label
                    >
                      {{ plan.inContextStatus }}
                    </v-chip>
                  </div>
                </template>
                <nuxt-link v-else-if="index === 2" class="font-weight-bold text-decoration-none" :to="`/ddt/${item.departementCode}/collectivites/${item.code}/${item.code.length > 5 ? 'epci' : 'commune'}`">
                  + {{ item.plans.length - 2 }} procédure{{ item.plans.length - 2 > 1 ? 's' : '' }}
                </nuxt-link>
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
                <div v-for="(scot, index) in item.scots" :key="scot.id" class="mb-4">
                  <template v-if="index < 2">
                    <div class="d-flex align-center">
                      <nuxt-link class="font-weight-bold text-decoration-none" :to="`/frise/${scot.id}`">
                        {{ $utils.formatProcedureName(scot, item) }}
                      </nuxt-link>
                      <v-chip
                        :class="{
                          'success-light': scot.inContextStatus === 'OPPOSABLE',
                          'success--text': scot.inContextStatus === 'OPPOSABLE',
                          'bf200': scot.inContextStatus === 'EN COURS',
                          'primary--text': scot.inContextStatus === 'EN COURS',
                          'text--lighten-2': scot.inContextStatus === 'EN COURS',

                        }"
                        class="font-weight-bold flex-shrink-0 ml-2"
                        small
                        label
                      >
                        {{ scot.inContextStatus }}
                      </v-chip>
                    </div>
                  </template>
                  <nuxt-link v-else-if="index === 2" class="font-weight-bold text-decoration-none" :to="`/ddt/${item.departementCode}/collectivites/${item.code}/${item.code.length > 5 ? 'epci' : 'commune'}`">
                    + {{ item.scots.length - 2 }} procédure{{ item.scots.length - 2 > 1 ? 's' : '' }}
                  </nuxt-link>
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
                        Collectivité validée le {{ formatDate(getValidatedInfosForCollectivite(item.code).created_at) }}
                        par {{ getValidatedInfosForCollectivite(item.code).email }}
                      </div>
                      <v-btn
                        v-if="getValidatedInfosForCollectivite(item.code).profile_id === $user.id || $user.profile.is_admin"
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
              Valider {{ selected.length }} collectivités
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
import axios from 'axios'
import dayjs from 'dayjs'
import { partition } from 'lodash'

const docVersion = '1.0'

const statusMap = {
  opposable: 'OPPOSABLE',
  'en cours': 'EN COURS'
}

const SCOT_LIKE = ['SCOT', 'SD']

export default {
  name: 'CollectiviteDU',
  layout: 'ddt',
  // https://v2.nuxt.com/docs/components-glossary/watchquery/#the-watchquery-property
  // watchQuery: ['search'],
  data () {
    return {
      exportingCommunes: false,
      exportingSCoTs: false,

      selected: [],
      searchEpcis: '',
      groupements: [],
      filterEpci: null,
      // env.DDT_ENQUETE_ENABLED permet de ne garder l'enquête ouverte que pour des DDT retardataires
      hasValidationEnabled: this.$user.canViewEnquete() || process.env.DDT_ENQUETE_ENABLED.includes(
        this.$route.params.departement
      ),
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
  watch: {
    search (new_val, old_val) {
      this.$utils.UpdateQueryParams({ search: new_val })
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
      return this.referentiel?.filter((collectivite) => {
        return !!this.selectedCollectiviteTypesFilter.find(type => collectivite.type.includes(type))
      }).filter((collectivite) => {
        return (
          !this.filterEpci ||
          this.filterEpci === collectivite.code ||
          collectivite.groupements.some(c => c.code === this.filterEpci)
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
    const collectivites = await this.$nuxt3api(`/api/geo/collectivites?departementCode=${this.$route.params.departement}`)
    const communes = []
    const groupements = []

    collectivites.forEach((c) => {
      if (c.type === 'COM') {
        communes.push(c)
      }

      if (c.code.length > 5) {
        groupements.push(c)
      }
    })
    this.groupements = groupements

    const procedures = await this.$urbanisator.getCollectivitesProcedures(communes.map(c => c.code))

    const enrichedCommunes = this.parseCommunes(communes, procedures)
    const enrichedGroups = this.parseGroupements(groupements, procedures)

    this.referentiel = [...enrichedGroups, ...enrichedCommunes]
    await this.fetchValidation()
  },
  methods: {
    formatDate (date) {
      return dayjs(date).format('DD/MM/YYYY')
    },
    async fetchValidation () {
      const { success, error, data } = await this.$enquete.getValidatedCollectivitesForDepartement(this.$route.params.departement)
      console.log('data valid 2024: ', data)
      this.validatedCollectivites = data
      const validatedCodes = this.validatedCollectivites.map(c => c.collectivite_code)
      for (const collectivite of this.referentiel) {
        collectivite.isNotValidated = !validatedCodes.includes(collectivite.code)
      }
      if (!success) {
        this.snackbar = true

        this.snackVal = { text: `ERREUR: ${error}`, type: 'error' }
      }
    },
    async cancelValidation (codeCollec) {
      const { success, error, data } = await this.$enquete.deleteValidationForCollectivite(codeCollec)
      console.log('data valid 2024: ', data)
      if (!success) {
        this.snackbar = true
        this.snackVal = { text: `ERREUR: ${error}`, type: 'error' }
      }
      await this.fetchValidation()
    },
    getValidatedInfosForCollectivite (collectiviteCode) {
      return this.validatedCollectivites.find(e => e.collectivite_code === collectiviteCode)
    },
    async validateSelectedCollectivites () {
      const { success, error } = await this.$enquete.validateCollectivites(this.selected)
      if (!success) {
        this.snackbar = true
        this.snackVal = { text: `ERREUR: ${error}`, type: 'error' }
      }
      await this.fetchValidation()
      this.selected = []
    },
    parseCommunes (communes, procedures) {
      return communes.map((commune) => {
        const communeProcedures = procedures.filter((procedure) => {
          return !!procedure.procedures_perimetres.find((p) => {
            return p.collectivite_code === commune.code
          })
        })

        const inContextProcedures = communeProcedures.map((procedure) => {
          const isOpposableInContext = procedure.procedures_perimetres.find((p) => {
            return p.collectivite_code === commune.code && p.opposable
          })

          let status = procedure.status

          if (status === 'opposable' && !isOpposableInContext) {
            status = 'precedent'
          }

          return Object.assign({}, procedure, {
            status,
            inContextStatus: statusMap[status] || 'ARCHIVÉ'
          })
        }).sort((a, b) => {
          if (a.inContextStatus < b.inContextStatus) { return -1 }
          if (a.inContextStatus > b.inContextStatus) { return 1 }
          return 0
        }).reverse()

        const [scots, plans] = partition(inContextProcedures, p => SCOT_LIKE.includes(p.doc_type))

        return {
          ...commune,
          isNotValidated: true,
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
    parseGroupements (groupements, procedures) {
      return groupements.map((groupement) => {
        const communesCodes = this.findCommunes(groupement.membres, groupements).map(m => m.code)

        const collectivitesSet = new Set(communesCodes)
        const groupementProcedures = procedures.filter((procedure) => {
          return procedure.procedures_perimetres.map(p => p.collectivite_code).some((code) => {
            return collectivitesSet.has(code)
          })
        })

        const inContextProcedures = groupementProcedures.map((procedure) => {
          return Object.assign({}, procedure, {
            inContextStatus: statusMap[procedure.status] || 'ARCHIVÉ'
          })
        }).sort((a, b) => {
          if (a.inContextStatus < b.inContextStatus) { return -1 }
          if (a.inContextStatus > b.inContextStatus) { return 1 }
          return 0
        }).reverse()

        const [scots, plans] = partition(inContextProcedures, p => SCOT_LIKE.includes(p.doc_type))

        return {
          ...groupement,
          isNotValidated: true,
          plans: plans.filter(p => p.procedures_perimetres.length > 1),
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
    async exportCommunes () {
      const departementCode = this.$route.params.departement

      this.$analytics({
        category: 'exports dashboard',
        name: 'exports communes',
        value: 'departementCode'
      })

      this.exportingCommunes = true
      const { data } = await axios(`/api/communes?departement=${departementCode}`)

      const a = document.createElement('a')
      const blob = new Blob([data], { type: 'text/csv' })
      a.href = window.URL.createObjectURL(blob)
      a.download = `docurba_communes_${departementCode}.csv`
      a.click()

      this.exportingCommunes = false
    },
    async exportSCoTs () {
      const departementCode = this.$route.params.departement

      this.$analytics({
        category: 'exports dashboard',
        name: 'exports scots',
        value: 'departementCode'
      })

      this.exportingSCoTs = true
      const { data } = await axios(`/api/scots?departement=${departementCode}`)

      const a = document.createElement('a')
      const blob = new Blob([data], { type: 'text/csv' })
      a.href = window.URL.createObjectURL(blob)
      a.download = `docurba_scots_${departementCode}.csv`
      a.click()

      this.exportingSCoTs = false
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
</style>
