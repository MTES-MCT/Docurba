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
import _ from 'lodash'

export default {
  name: 'SCOTsDepList',
  data () {
    return {
      scots: null
    }
  },
  computed: {
    opposables () {
      return this.scots.filter(e => e.status === 'opposable')
    },
    ongoing () {
      return this.scots.filter(e => e.status === 'en cours')
    },
    previous () {
      return this.scots.filter(e => e.status !== 'en cours' && e.status !== 'opposable')
    }
  },
  async mounted () {
    // je peux regarder les périmetres des SCoT, selectionner que ceux qui sont appliquer sur des code INSEE qui commence par le code département comme ca je peux les lister
    const { data } = await this.$supabase.from('temp_scots').select().eq('collectivite_departement_code', this.$route.params.departement)
    const scots = data.map(e => e.procedures).reduce((acc, curr) => [...acc, ...curr], [])
    console.log('SCoTs: ', scots)
    const distinctScots = _.uniqBy(scots, e => e.id)
    console.log('distinct SCoTs: ', distinctScots)
    this.scots = distinctScots
  }
}
</script>
