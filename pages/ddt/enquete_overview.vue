
<template>
  <v-container>
    <v-row>
      <v-col cols="12">
        <h1>Validation des procédures - Aperçu</h1>
      </v-col>
      <!-- <v-col v-if="!collectivites" cols="12">
        <v-skeleton-loader
          type="table"
        />
      </v-col> -->
      <v-col cols="12">
        <v-data-table
          :headers="headers"
          :items="deptsItems"
          :sort-by="['departement']"
          :sort-desc="[false]"
          :custom-sort="customSort"
          must-sort
        >
          <!-- eslint-disable-next-line -->
        <template #item.departement="{ item }">
            <div>{{ item.departement_code }} - {{ item.departement_intitule }}</div>
          </template>

          <!-- eslint-disable-next-line -->
        <template #item.collectivites="{ item }">
            <span class="primary--text font-weight-bold">{{ item.nb_validated }}</span> <span class="mention-grey--text"> / {{ item.nb_communes }}</span>
          </template>

          <!-- eslint-disable-next-line -->
        <template #item.action="{ item }">
            <v-btn
              text
              :to="`/ddt/${item.departement_code}/collectivites`"
              color="primary"
            >
              Consulter
              <v-icon right>
                {{ icons.mdiArrowRight }}
              </v-icon>
            </v-btn>
          </template>
        </v-data-table>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import axios from 'axios'
import { mdiArrowRight } from '@mdi/js'

export default {
  name: 'EnqueteOverview',
  layout: 'ddt',
  data () {
    return {
      icons: {
        mdiArrowRight
      },
      deptsItems: []
    }
  },
  computed: {
    headers () {
      return [
        {
          text: 'Département',
          align: 'start',
          value: 'departement'
        },
        { text: 'Collectivités', align: 'start', value: 'collectivites' },
        { text: 'Restantes', align: 'start', value: 'restantes' },
        { text: '% validées', align: 'start', value: 'percentage' },
        { text: 'Schémas', value: 'schemas' },
        { text: '', value: 'action' }
      ]
    }
  },
  async mounted () {
    // TODO: Need to add EPCI/SCOT to the count
    const { data: communesByDepts } = await axios('/json/communes_by_department_enriched.json')
    console.log('communesByDepts: ', communesByDepts)
    this.deptsItems = communesByDepts

    const { data: nbValidationByDepts, error } = await this.$supabase.rpc('validated_collectivites_by_depts_2024')
    console.log('error: ', error)
    console.log('nbValidationByDepts: ', nbValidationByDepts)

    const validationsMap = new Map(
      nbValidationByDepts?.map(item => [item.departement, item.unique_collectivites_count]) || []
    )

    // Enrich deptsItems with nb_validated
    this.deptsItems = communesByDepts.map(dept => ({
      ...dept,
      nb_validated: validationsMap.get(dept.departement_code) || 0
    }))
    console.log('this.deptsItems aftet: ', this.deptsItems)
  },
  methods: {
    customSort (items, sortBy, sortDesc) {
      if (sortBy.length === 0) { return items }

      const direction = sortDesc[0] ? -1 : 1

      return items.sort((a, b) => {
        if (sortBy[0] === 'departement') {
          const codeA = a.departement_code.padStart(2, '0')
          const codeB = b.departement_code.padStart(2, '0')
          return direction * codeA.localeCompare(codeB)
        }
        if (sortBy[0] === 'communes') {
          return direction * (a.nb_validated - b.nb_validated)
        }
        // Add other sort cases if needed
        return 0
      })
    }
  }
}
</script>
