<template>
  <v-container>
    <v-row>
      <v-col cols="12" class="d-flex align-center justify-space-between pb-0 pt-4">
        <h1>Mes Procédures</h1>
        <div>
          <v-btn v-if="$user.canCreateProcedure({ departement: $route.params.departement })" depressed color="primary" :to="`/ddt/${$route.params.departement}/procedures/choix-collectivite`">
            Nouvelle procédure
          </v-btn>
        </div>
      </v-col>
      <v-col v-if="!procedures" cols="12">
        <v-skeleton-loader
          type="table"
        />
      </v-col>
      <v-col v-else cols="12">
        <v-data-table
          v-model="selected"
          :headers="headers"
          :items="proceduresToDisplay"
          :items-per-page="10"
          class="elevation-1 pa-8 procedures-dt"
          :custom-filter="customFilter"
          :search="search"
          :loading="!procedures"
          :show-select="hasValidationEnabled"
          selectable-key="validationNeededForSurvey"
          loading-text="Chargement des procédures..."
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
                  v-model="hideValidatedProceduresForSurvey"
                  color="primary"
                  dark
                  inset
                >
                  <template #label>
                    <span class="primary--text">
                      Voir seulement les collectivités à valider ({{ notValidatedProceduresForSurvey.length }} restantes)
                    </span>
                  </template>
                </v-switch>
              </div>
            </v-alert>
            <v-row>
              <v-col v-if="$user.canViewMultipleDepartements()" cols="8" class="p-0" order="first">
                <VDeptAutocomplete
                  :default-departement-code="$route.params.departement"
                  :departements-filter="$user.profile.departements"
                  :hide-details="true"
                  :dense="true"
                  :with-label="false"
                  @input="navigateToDepartement"
                />
              </v-col>
              <v-col cols="8" class="p-0 mb-6 d-flex justify-space-between" :order="$user.canViewMultipleDepartements() ? 'last' : 'first'">
                <v-select
                  v-model="selectedTypesFilter"
                  flat
                  background-color="alt-beige"
                  hide-details
                  solo
                  dense
                  multiple
                  :items="typeFilterItems"
                >
                  <template #selection="{item, index}">
                    <div v-if="selectedTypesFilter.length === typeFilterItems.length && index === 0">
                      Tout type de procédures
                    </div>
                    <span v-else-if="selectedTypesFilter.length !== typeFilterItems.length">{{ item.text }}</span>
                  </template>
                </v-select>

                <v-select
                  v-model="selectedDocumentsFilter"
                  class="ml-2"
                  flat
                  multiple
                  background-color="alt-beige"
                  hide-details
                  solo
                  dense
                  :items="documentFilterItems"
                >
                  <template #selection="{item, index}">
                    <div v-if="documentFilterItems.length === selectedDocumentsFilter.length && index === 0">
                      Tout type de document
                    </div>
                    <span v-else-if="documentFilterItems.length !== selectedDocumentsFilter.length">
                      {{ item.text }}<span v-if="index !== selectedDocumentsFilter.length - 1">,&nbsp;</span>
                    </span>
                  </template>
                </v-select>

                <v-select
                  v-model="selectedStatusFilter"
                  class="ml-2"
                  flat
                  multiple
                  background-color="alt-beige"
                  hide-details
                  solo
                  dense
                  :items="statusFilterItems"
                >
                  <template #selection="{item, index}">
                    <div v-if="statusFilterItems.length === selectedStatusFilter.length && index === 0">
                      Tous les statuts
                    </div>
                    <span v-else-if="statusFilterItems.length !== selectedStatusFilter.length">
                      {{ item.text }}<span v-if="index !== selectedStatusFilter.length - 1">,&nbsp;</span>
                    </span>
                  </template>
                </v-select>
              </v-col>
              <v-col cols="3" offset="1" align-self="start">
                <v-text-field
                  v-model="search"
                  outlined
                  hide-details
                  dense
                  label="Rechercher une procédure..."
                />
              </v-col>
            </v-row>
          </template>

          <!-- eslint-disable-next-line -->
          <template #item.procedureName="{ item }">
            <div class="d-flex align-center my-5">
              <nuxt-link class="font-weight-bold text-decoration-none" :to="`/frise/${item.procedure_id}`">
                {{ item.procedureName }}
              </nuxt-link>

              <div v-if="item.procedures.status === null" />
              <v-chip v-else-if="item.opposable" class="ml-2 flex-shrink-0 success--text font-weight-bold" small label color="success-light">
                OPPOSABLE
              </v-chip>
              <v-chip v-else-if="!item.opposable && item.procedures.status === 'opposable'" class="ml-2 flex-shrink-0 font-weight-bold" small label>
                ARCHIVÉ
              </v-chip>
              <v-chip v-else class="ml-2 flex-shrink-0 primary--text text--lighten-2 font-weight-bold" small label color="bf200">
                EN COURS
              </v-chip>
            </div>
          </template>

          <!-- eslint-disable-next-line -->
            <template #item.perimetre="{ item }">
            <DashboardPerimetreDialog :perimetre="item.perimetre" :doc-name="item.procedureName" />
          </template>

          <!-- eslint-disable-next-line -->
          <template #item.prescription="{ item }">
            <span class="mention-grey--text">{{ item.prescription?.date_iso_formattee ?? '-' }}</span>
          </template>

          <!-- eslint-disable-next-line -->
          <template #item.last_event="{ item }">
            <span class="mention-grey--text">{{ item.last_event?.date_iso_formattee }} - {{ item.last_event?.type }}</span>
          </template>

                    <!-- eslint-disable-next-line -->
          <template #item.data-table-select="{ item, isSelected, select}">
            <div class="d-flex align-end justify-end my-5">
              <v-tooltip v-if="item.validationNeededForSurvey" top>
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
                <span>Valider</span>
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
                      <!-- <div class="mb-2">
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
                      </v-btn> -->
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
            <v-btn class="ml-2" color="primary" depressed @click="validateSelectedProcedures">
              Valider {{ selected.length }} procédures
            </v-btn>
          </div>
        </div>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import { mdiWifiArrowDown } from '@mdi/js';
import dayjs from 'dayjs'
// import { AsyncParser } from '@json2csv/node'

export default {
  name: 'ProceduresDepartement',
  layout: 'ddt',
  data () {
    const documentTypes = ['CC', 'PLU', 'PLUi', 'PLUiH', 'PLUiHM', 'PLUiM', 'SCOT']
    return {
      selected: [],
      hideValidatedProceduresForSurvey: false,
      hasValidationEnabled: this.$user.canViewProcedureSurvey({ departement: this.$route.params.departement }),
      referentiel: null,
      selectedTypesFilter: ['pp', 'ps'],
      typeFilterItems: [{ text: 'Procédures principales', value: 'pp' }, { text: 'Procédures secondaires', value: 'ps' }],
      selectedDocumentsFilter: documentTypes,
      documentFilterItems: documentTypes.map(documentType => ({ text: documentType, value: documentType })),
      selectedStatusFilter: ['en_cours', 'opposable', 'archived'],
      statusFilterItems: [{ text: 'En cours', value: 'en_cours' }, { text: 'Opposable', value: 'opposable' }, { text: 'Archivée', value: 'archived' }],
      rawProcedures: null,
      search: this.$route.query.search || ''

    }
  },
  computed: {
    headers () {
    const headers = [
        { text: 'Nom', align: 'start', value: 'procedureName', filterable: true, width: '45%' },
        { text: 'Périmètre', align: 'start', value: 'perimetre', filterable: false, width: '150px' },
        { text: 'Prescription', value: 'prescription', filterable: false, width: '135px', sort: this.sortByDateIso },
        { text: 'Dernier évènement', value: 'last_event', filterable: false, sort: this.sortByDateIso }
      ]
      if (this.hasValidationEnabled) {
        headers.push({ text: 'Valider', value: 'data-table-select' })
      }
      return headers
    },
    procedures () {
      const proceduresAndFilters = this.rawProcedures?.filter((e) => {
        return e.procedures.created_at &&
        this.selectedDocumentsFilter.includes(e.procedures.doc_type) &&
        ((this.selectedTypesFilter.includes('pp') && e.procedures.is_principale) ||
        (this.selectedTypesFilter.includes('ps') && !e.procedures.is_principale)) &&
        (((this.selectedStatusFilter.includes('opposable') && e.opposable) ||
        (this.selectedStatusFilter.includes('en_cours') && (!e.opposable && !(e.procedures.status === 'opposable'))) ||
        (this.selectedStatusFilter.includes('archived') && (!e.opposable && e.procedures.status === 'opposable'))))
      })
      return proceduresAndFilters
    },
    notValidatedProceduresForSurvey () {
      return this.procedures.filter(procedure => procedure.validationNeededForSurvey)
    },
    proceduresToDisplay () {
      if (this.hideValidatedProceduresForSurvey) {
        return this.notValidatedProceduresForSurvey
      }
      return this.procedures
    }

  },
  async mounted () {
    try {
      if (!this.$user.canViewSectionProcedures({ departement: this.$route.params.departement })) {
        console.warn('User is not allowed to view this page.')
        this.$nuxt.context.redirect(302, '/')
      }
      const promProcedures = await this.$urbanisator.getProceduresForDept(this.$route.params.departement)
      const rawReferentiel = fetch(`/api/geo/collectivites?departements=${this.$route.params.departement}`)

      const [rawProcedures, referentiel] = await Promise.all([promProcedures, rawReferentiel])
      const { communes, groupements } = await referentiel.json()
      this.rawProcedures = rawProcedures.map((e) => {
        let collectivitePorteuse
        if (e.perimetre.length > 1) {
          collectivitePorteuse = groupements.find(grp => grp.code === e.procedures.collectivite_porteuse_id)
        } else {
          collectivitePorteuse = communes.find(com => com.code === e.perimetre[0].collectivite_code)
        }

        const procedureName = this.$utils.formatProcedureName({ ...e.procedures, procedures_perimetres: e.perimetre }, collectivitePorteuse)
        if (e.prescription?.date_iso) {
          e.prescription.date_iso_formattee = dayjs(e.prescription.date_iso).format('DD/MM/YYYY')
        }
        if (e.last_event?.date_iso) {
          e.last_event.date_iso_formattee = dayjs(e.last_event.date_iso).format('DD/MM/YYYY')
        }

        return { ...e, procedureName }
      })
    } catch (error) {
      // eslint-disable-next-line no-console
      console.log('ERROR: ', error)
    }
    if (this.hasValidationEnabled) {
      this.rawProcedures = await this.addValidationNeededToProcedure(this.rawProcedures)
    }
  },
  methods: {
    customFilter (value, search, item) {
      if (!search?.length) { return true }

      const normalizedValue = item.procedureName.toLocaleLowerCase().normalize('NFKD').replace(/\p{Diacritic}/gu, '')
      const normalizedSearch = search.toLocaleLowerCase().normalize('NFKD').replace(/\p{Diacritic}/gu, '')

      return normalizedValue.includes(normalizedSearch)
    },
    navigateToDepartement (departementObject) {
      if (!departementObject) {
        return
      }
      let departement = departementObject.code_departement.toString()
      departement = departement.padStart('2', '0')
      this.$router.push({ params: { departement } })
    },
    sortByDateIso (a, b) {
      return dayjs(a?.date_iso || 0) - dayjs(b?.date_iso || 0)
    },
    async addValidationNeededToProcedure (procedures) {
      console.log("before")
      const { success, error, data } = await this.$zanSurvey.getProceduresToValidate(this.$route.params.departement)
      // const filteredProcedures = this.procedures.filter(e => data.map(d => d.procedures.id).includes(e.procedures.id))
      return procedures.map(e => ({...e,
        validationNeededForSurvey: data.map(d => d.procedures.id).includes(e.procedures.id)
      }))
      // this.rawProcedures = procedures
      // window.procedures = rawProcedures
      // console.log("procedures", this.procedures)
      // OK:
      // window.procedures.filter(e =>
      //   window.data.map(d => d.procedures.id).includes('4630c7d0-6626-4aae-a57d-9666311f617a')
      // )

      // const validatedCodes = this.validatedCollectivites.map(c => c.collectivite_code)
      // for (const collectivite of this.referentiel) {
      //   collectivite.isNotValidated = !validatedCodes.includes(collectivite.code)
      // }
      // if (!success) {
      //   this.snackbar = true

      //   this.snackVal = { text: `ERREUR: ${error}`, type: 'error' }
      // }
    },
    // cancelValidation: where procedureId in selectedIds and profile_id==user.id
    // async cancelValidation (codeCollec) {
    //   const { success, error, data } = await this.$enquete.deleteValidationForCollectivite(codeCollec)
    //   console.log('data valid 2024: ', data)
    //   if (!success) {
    //     this.snackbar = true
    //     this.snackVal = { text: `ERREUR: ${error}`, type: 'error' }
    //   }
    //   await this.fetchValidation()
    // },
    // getValidatedInfosForCollectivite (collectiviteCode) {
    //   return this.validatedCollectivites.find(e => e.collectivite_code === collectiviteCode)
    // },
    // async validateSelectedCollectivites () {
    //   const { success, error } = await this.$enquete.validateCollectivites(this.selected)
    //   if (!success) {
    //     this.snackbar = true
    //     this.snackVal = { text: `ERREUR: ${error}`, type: 'error' }
    //   }
    //   await this.fetchValidation()
    //   this.selected = []
    // },
  }
}
</script>
<style lang="scss">
.procedures-dt {
  tr td{
    border-bottom: none !important;
  }
  tr th{
    font-size: 14px !important;
    color: #000 !important;
  }
}
</style>
