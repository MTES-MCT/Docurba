<template>
  <v-container>
    <v-row>
      <v-col cols="12" class="d-flex align-center justify-space-between pb-0 pt-4">
        <h1>Mes Procédures</h1>
        <div>
          <v-btn :loading="loadingDownload" outlined color="primary" class="mr-2" @click="download">
            Exporter les procédures
          </v-btn>
          <v-btn depressed color="primary" :to="`/ddt/${$route.params.departement}/procedures/choix-collectivite`">
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
          :loading="!procedures"
          loading-text="Chargement des collectivités..."
        >
          <template #top>
            <div class="d-flex  align-center justify-space-between mb-6">
              <v-select
                v-model="selectedTypesFilter"
                flat
                background-color="alt-beige"
                hide-details
                solo
                multiple
                dense
                :items="typeFilterItems"
                style="max-width:250px"
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
                style="max-width:260px"
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
                style="max-width:180px"
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

              <v-spacer />
              <v-text-field
                v-model="search"
                outlined
                hide-details
                dense
                style="max-width:400px"
                label="Rechercher une procédure..."
              />
            </div>
          </template>

          <!-- eslint-disable-next-line -->
          <template #item.name="{ item }">
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

            <span class="mention-grey--text">{{ item.prescription?.date_iso ? item.prescription?.date_iso : '-' }}</span>
          </template>

          <!-- eslint-disable-next-line -->
          <template #item.last_event="{ item }">
            <span class="mention-grey--text">{{ item.last_event?.date_iso }} - {{ item.last_event?.type }}</span>
          </template>
        </v-data-table>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import dayjs from 'dayjs'
import axios from 'axios'
// import { AsyncParser } from '@json2csv/node'

export default {
  name: 'ProceduresDepartement',
  layout: 'ddt',
  data () {
    const documentTypes = ['CC', 'PLU', 'PLUi', 'PLUiH', 'PLUiHM', 'PLUiM', 'SCOT']
    return {
      loadingDownload: false,
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
      return [
        { text: 'Nom', align: 'start', value: 'name', filterable: true, width: '45%' },
        { text: 'Périmètre', align: 'start', value: 'perimetre', filterable: false, width: '150px' },
        { text: 'Prescription', value: 'prescription', filterable: false, width: '135px' },
        { text: 'Dernier évènement', value: 'last_event', filterable: false }
      ]
    },
    procedures () {
      const proceduresAndFilters = this.rawProcedures?.map((e) => {
        if (e.prescription?.date_iso) {
          e.prescription.date_iso = e.prescription.date_iso ? dayjs(e.prescription.date_iso).format('DD/MM/YY') : null
        }

        return e
      }).filter((e) => {
        return e.procedures.created_at &&
        this.selectedDocumentsFilter.includes(e.procedures.doc_type) &&
          ((this.selectedTypesFilter.includes('pp') && e.procedures.is_principale) ||
          (this.selectedTypesFilter.includes('ps') && !e.procedures.is_principale)) &&
          (((this.selectedStatusFilter.includes('opposable') && e.opposable) ||
          (this.selectedStatusFilter.includes('en_cours') && (!e.opposable && !(e.procedures.status === 'opposable'))) ||
          (this.selectedStatusFilter.includes('archived') && (!e.opposable && e.procedures.status === 'opposable'))))
      })
      return proceduresAndFilters
    }
  },
  async mounted () {
    try {
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

        return { ...e, procedureName }
      })
    } catch (error) {
      // eslint-disable-next-line no-console
      console.log('ERROR: ', error)
    }
  },
  methods: {
    async download () {
      const departementCode = this.$route.params.departement

      this.$analytics({
        category: 'exports dashboard',
        name: 'exports communes',
        value: 'departementCode'
      })

      this.loadingDownload = true
      const { data } = await axios(`/api/urba/exports/departements/${departementCode}?csv=true`)

      const a = document.createElement('a')
      const blob = new Blob([data], { type: 'text/csv' })
      a.href = window.URL.createObjectURL(blob)
      a.download = `docurba_procedures_${departementCode}.csv`
      a.click()

      this.loadingDownload = false
    },
    customFilter (value, search, item) {
      if (!search?.length) { return true }

      const normalizedValue = item.procedureName.toLocaleLowerCase().normalize('NFKD').replace(/\p{Diacritic}/gu, '')
      const normalizedSearch = search.toLocaleLowerCase().normalize('NFKD').replace(/\p{Diacritic}/gu, '')

      return normalizedValue.includes(normalizedSearch)
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
