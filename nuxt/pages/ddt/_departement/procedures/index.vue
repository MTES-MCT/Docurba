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
          :headers="headers"
          :items="procedures"
          :items-per-page="10"
          class="elevation-1 pa-8 procedures-dt"
          :custom-filter="customFilter"
          :search="search"
          sort-by="last_event.date_iso"
          sort-desc="true"
        >
          <template #top>
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

              <v-chip v-if="item.statut_libelle === 'opposable'" class="ml-2 flex-shrink-0 success--text font-weight-bold" small label color="success-light">
                OPPOSABLE
              </v-chip>
              <v-chip v-else-if="item.statut_libelle === 'archive'" class="ml-2 flex-shrink-0 font-weight-bold" small label>
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
          <template #item.date_prescription="{ item }">

            <span class="mention-grey--text">{{ item.date_prescription ?? '-' }}</span>
          </template>

          <!-- eslint-disable-next-line -->
          <template #item.last_event.date_iso="{ item }">
            <span class="mention-grey--text">{{ item.last_event?.date_iso }} - {{ item.last_event?.type }}</span>
          </template>
        </v-data-table>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
export default {
  name: 'ProceduresDepartement',
  layout: 'ddt',
  data () {
    const documentTypes = ['CC', 'PLU', 'PLUi', 'PLUiH', 'PLUiHM', 'PLUiM', 'SCOT']
    return {
      referentiel: null,
      selectedTypesFilter: ['pp', 'ps'],
      typeFilterItems: [{ text: 'Procédures principales', value: 'pp' }, { text: 'Procédures secondaires', value: 'ps' }],
      selectedDocumentsFilter: documentTypes,
      documentFilterItems: documentTypes.map(documentType => ({ text: documentType, value: documentType })),
      selectedStatusFilter: ['en cours', 'opposable', 'archive'],
      statusFilterItems: [{ text: 'En cours', value: 'en cours' }, { text: 'Opposable', value: 'opposable' }, { text: 'Archivée', value: 'archive' }],
      rawProcedures: null,
      search: this.$route.query.search || ''

    }
  },
  computed: {
    headers () {
      return [
        { text: 'Nom', align: 'start', value: 'procedureName', filterable: true, width: '45%' },
        { text: 'Périmètre', align: 'start', value: 'perimetre', filterable: false, width: '150px' },
        { text: 'Prescription', value: 'date_prescription', filterable: false, width: '135px' },
        { text: 'Dernier évènement', value: 'last_event.date_iso', filterable: false }
      ]
    },
    procedures () {
      const proceduresAndFilters = this.rawProcedures?.filter((e) => {
        return (
          this.selectedDocumentsFilter.includes(e.type_document) &&
          ((this.selectedTypesFilter.includes('pp') && e.is_principale) ||
            (this.selectedTypesFilter.includes('ps') && !e.is_principale)) &&
          ((this.selectedStatusFilter.includes('opposable') && e.statut_libelle === 'opposable') ||
            (this.selectedStatusFilter.includes('en cours') && e.statut_libelle === 'en cours') ||
            (this.selectedStatusFilter.includes('archive') && e.statut_libelle === 'archive'))
        )
      })
      return proceduresAndFilters
    }
  },
  async mounted () {
    if (!this.$user.canViewSectionProcedures({ departement: this.$route.params.departement })) {
      console.warn('User is not allowed to view this page.')
      this.$nuxt.context.redirect(302, '/')
    }

    const response = await fetch(`/pour_nuxt/procedures/${this.$route.params.departement}/`)
    const json = await response.json()
    this.rawProcedures = json.results
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
    }
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
