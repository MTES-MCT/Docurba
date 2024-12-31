
<template>
  <v-container>
    <v-row>
      <v-col cols="12">
        <h1>Validation des procédures - Aperçu</h1>
      </v-col>
      <v-col cols="12">
        <v-data-table
          :headers="headers"
          :items="deptsItems"
          :items-per-page="-1"
          :sort-by="['departement_code']"
          :sort-desc="[false]"
          must-sort
          style="font-variant-numeric: tabular-nums;"
        >
          <!-- eslint-disable-next-line -->
        <template #item.departement_code="{ item }">
            <div>{{ item.departement_code }} - {{ item.departement_intitule }}</div>
          </template>

          <!-- eslint-disable-next-line -->
        <template #item.nb_validated="{ item }">
            <span class="primary--text font-weight-bold">{{ item.nb_validated }}</span>
            <span class="mention-grey--text"> / {{ item.nb_collectivites.toString().padStart(3,'0') }}</span>
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
        { text: 'Département', align: 'start', value: 'departement_code' },
        { text: 'Collectivités', align: 'end', value: 'nb_validated' },
        { text: 'Restantes', align: 'end', value: 'restantes' },
        { text: '% validées', align: 'end', value: 'percentage' },
        { text: '', value: 'action' }
      ]
    }
  },
  async mounted () {
    if (!this.$user.profile.is_admin) {
      return
    }

    const response = await fetch('/json/nb_collectivites_par_departement.json')
    const nbCollectivitesParDepartement = await response.json()

    const { data: nbValidationByDepts } = await this.$supabase.rpc('validated_collectivites_by_depts_2024').throwOnError()

    const nbValidationByDeptsMap = new Map(
      nbValidationByDepts?.map(item => [item.departement, item.unique_collectivites_count]) || []
    )

    // Enrich deptsItems with nb_validated
    this.deptsItems = nbCollectivitesParDepartement.map((departement) => {
      const nbValidated = nbValidationByDeptsMap.get(departement.departement_code) || 0
      return {
        ...departement,
        nb_validated: nbValidated,
        restantes: departement.nb_collectivites - nbValidated,
        percentage: Math.round((nbValidated / departement.nb_collectivites) * 100)
      }
    })
  }
}
</script>
