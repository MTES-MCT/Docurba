<template>
  <v-container v-if="procedures">
    <v-row>
      <v-col cols="12" class="d-flex align-center justify-space-between pb-0 pt-4">
        <h1>Mes Procédures</h1>
        <div>
          <v-btn outlined color="primary" class="mr-2">
            Exporter les procédures
          </v-btn>
          <v-btn depressed color="primary">
            Nouvelle procédure
          </v-btn>
        </div>
      </v-col>
      <v-col cols="12">
        <v-data-table
          :headers="headers"
          :items="procedures"
          :items-per-page="10"
          class="elevation-1 pa-8"
          :custom-filter="customFilter"
          :search="search"
          :loading="!procedures"
          loading-text="Chargement des collectivités..."
        >
          <template #top>
            <div class="d-flex  align-center justify-space-between">
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
                    Tous type de procédures
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
                    Tous types de documents
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
                    Tous les status
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
            <span>{{ item.procedures_duplicate.doc_type }} {{ item.procedures_duplicate.id }}</span>
          </template>

          <!-- eslint-disable-next-line -->
            <template #item.perimetre="{ item }">
            <div>
              {{ item.perimetre?.length }} communes
            </div>
          </template>

          <!-- eslint-disable-next-line -->
          <template #item.prescription="{ item }">
            <span>{{ item.prescription?.date_iso }}</span>
          </template>

          <!-- eslint-disable-next-line -->
          <template #item.last_event="{ item }">
            <span>{{ item.last_event?.date_iso }} - {{ item.last_event?.type }}</span>
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
    return {
      referentiel: null,
      selectedTypesFilter: ['pp', 'ps'],
      typeFilterItems: [{ text: 'Procédures principales', value: 'pp' }, { text: 'Procédures secondaires', value: 'ps' }],
      selectedDocumentsFilter: ['CC', 'PLU', 'SCOT'],
      documentFilterItems: [{ text: 'CC', value: 'CC' }, { text: 'PLU', value: 'PLU' }, { text: 'SCOT', value: 'SCOT' }],
      selectedStatusFilter: ['en_cours', 'opposable', 'archived'],
      statusFilterItems: [{ text: 'En cours', value: 'en_cours' }, { text: 'Opposable', value: 'opposable' }, { text: 'Archivée', value: 'archived' }],
      rawProcedures: null,
      search: this.$route.query.search || ''

    }
  },
  computed: {
    headers () {
      return [
        { text: 'Nom', align: 'start', value: 'name', filterable: true, width: '40%' },
        { text: 'Périmetre', align: 'start', value: 'perimetre', filterable: false },
        { text: 'Prescription', value: 'prescription', filterable: false },
        { text: 'Dernier évènement', value: 'last_event', filterable: false }
      ]
    },
    procedures () {
      return this.rawProcedures?.filter(e => this.selectedDocumentsFilter.includes(e.procedures_duplicate.doc_type))
    }
  },
  async mounted () {
    // TODO: Générer un nom pour toutes les procédures dans le field name pour ne pas avoir a fetch le referentiel tous le temps
    this.rawProcedures = await this.$urbanisator.getProceduresForDept(this.$route.params.departement)
  },
  methods: {
    customFilter (value, search, item) {
      if (!search?.length || !value?.length) { return true }

      const normalizedValue = value.toLocaleLowerCase().normalize('NFKD').replace(/\p{Diacritic}/gu, '')
      const normalizedSearch = search.toLocaleLowerCase().normalize('NFKD').replace(/\p{Diacritic}/gu, '')

      return normalizedValue.includes(normalizedSearch)
    }
  }
}
</script>
<style lang="scss">
.competence-tag-sudocu{
  background: #FEECC2;
  border-radius: 4px;
  text-transform: uppercase;
  color: #716043;
  font-family: 'Marianne';
  font-style: normal;
  font-weight: 700;
  font-size: 14px;
  line-height: 24px;
  padding: 0px 8px;
}

.competence-tag-banatic{
  background: var(--v-primary-base);
  border-radius: 4px;
  text-transform: uppercase;
  color: var(--v-primary-lighten1);
  font-family: 'Marianne';
  font-style: normal;
  font-weight: 700;
  font-size: 14px;
  line-height: 24px;
  padding: 0px 8px;
}

</style>
