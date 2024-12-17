
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
            <span class="primary--text font-weight-bold">{{ item.nb_validated }}</span> <span class="mention-grey--text"> / {{ item.nb_collectivites }}</span>
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
        { text: 'Restantes', align: 'start', value: 'restantes', sortable: true },
        { text: '% validées', align: 'start', value: 'percentage', sortable: true },
        { text: '', value: 'action' }
      ]
    }
  },
  async mounted () {
    const { data: collectivitesByDepts } = await axios('/json/collectivites_by_department_enriched.json')
    this.deptsItems = collectivitesByDepts
    const { data: nbValidationByDepts, error } = await this.$supabase.rpc('validated_collectivites_by_depts_2024')
    console.log('error: ', error)

    const validationsMap = new Map(
      nbValidationByDepts?.map(item => [item.departement, item.unique_collectivites_count]) || []
    )

    // Enrich deptsItems with nb_validated
    this.deptsItems = collectivitesByDepts.map((dept) => {
      const nbValidated = validationsMap.get(dept.departement_code) || 0
      return {
        ...dept,
        nb_validated: nbValidated,
        restantes: dept.nb_collectivites - nbValidated,
        percentage: Math.round((nbValidated / dept.nb_collectivites) * 100)
      }
    })
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
        if (sortBy[0] === 'collectivites') {
          return direction * (a.nb_validated - b.nb_validated)
        }
        if (sortBy[0] === 'restantes') {
          return direction * (a.restantes - b.restantes)
        }
        if (sortBy[0] === 'percentage') {
          return direction * (a.percentage - b.percentage)
        }
        // Add other sort cases if needed
        return 0
      })
    }
  }
}
</script>
