<template>
  <v-container v-if="scots">
    <v-row>
      <v-col>
        <v-expansion-panels :value="0">
          <v-expansion-panel>
            <v-expansion-panel-header class="font-weight-black">
              Opposables ({{ opposables.length }})
            </v-expansion-panel-header>
            <v-expansion-panel-content>
              <DashboardDUItem
                v-for="(procedure,i) in opposables"
                :key="'du_' + i"
                :procedure="procedure"
              />
            </v-expansion-panel-content>
          </v-expansion-panel>
          <v-expansion-panel>
            <v-expansion-panel-header class="font-weight-black">
              En cours ({{ ongoing.length }})
            </v-expansion-panel-header>
            <v-expansion-panel-content>
              <DashboardDUItem
                v-for="(procedure,i) in ongoing"
                :key="'du_' + i"
                :procedure="procedure"
              />
            </v-expansion-panel-content>
          </v-expansion-panel>
          <v-expansion-panel>
            <v-expansion-panel-header class="font-weight-black">
              Précédents et annulés ({{ previous.length }})
            </v-expansion-panel-header>
            <v-expansion-panel-content>
              <DashboardDUItem
                v-for="(procedure,i) in previous"
                :key="'du_' + i"
                :procedure="procedure"
              />
            </v-expansion-panel-content>
          </v-expansion-panel>
        </v-expansion-panels>
      </v-col>
    </v-row>
  </v-container>
  <v-container v-else>
    <VGlobalLoader />
  </v-container>
</template>

<script>
import { groupBy } from 'lodash'

export default {
  name: 'SCOTsDepList',
  props: {
    search: {
      type: String,
      default: ''
    }
  },
  data () {
    return {
      scots: null
    }
  },
  computed: {
    searchedScots () {
      const normalizedSearch = this.search.toLocaleLowerCase().normalize('NFKD').replace(/\p{Diacritic}/gu, '')

      return this.scots.filter((scot) => {
        // This current perimetre usage is to bypass an import anomalie
        const name = scot.name || scot.current_perimetre[0].name
        const normalizedValue = name.toLocaleLowerCase().normalize('NFKD').replace(/\p{Diacritic}/gu, '')
        return normalizedValue.includes(normalizedSearch)
      })
    },
    opposables () {
      return this.searchedScots.filter(e => e.status === 'opposable')
    },
    ongoing () {
      return this.searchedScots.filter(e => e.status === 'en cours')
    },
    previous () {
      return this.searchedScots.filter(e => e.status !== 'en cours' && e.status !== 'opposable')
    }
  },
  async mounted () {
    // je peux regarder les périmetres des SCoT, selectionner que ceux qui sont appliquer sur des code INSEE qui commence par le code département comme ca je peux les lister
    const { data: procedures } = await this.$supabase.from('procedures').select().is('is_scot', true).contains('departements', [this.$route.params.departement])
    // console.log('DATA SCOT: ', data)

    const secondaryProcedures = groupBy(procedures, p => p.secondary_procedure_of)
    const principalsProcedures = procedures.filter(p => p.is_principale)

    principalsProcedures.forEach((p) => {
      p.procSecs = secondaryProcedures[p.id]
    })

    this.scots = principalsProcedures
  }
}
</script>
