<template>
  <v-container v-if="collectivite">
    <v-row>
      <v-col cols="12">
        <h1>{{ collectivite.name }}</h1>
      </v-col>
      <v-col cols="12">
        <v-expansion-panels v-if="isEpci" flat>
          <v-expansion-panel class="beige">
            <v-expansion-panel-header>
              <h3>{{ collectivite.towns.length }} communes dans votre EPCI</h3>
            </v-expansion-panel-header>
            <v-expansion-panel-content>
              <v-container>
                <v-row>
                  <v-col
                    v-for="town in collectivite.towns"
                    :key="town.code_commune_INSEE"
                    cols="4"
                    class="pt-0 pl-0"
                  >
                    <nuxt-link :to="{ name: 'dashboard-departement-collectivites-collectiviteId', params: { departement: $route.params.departement, collectiviteId: town.code_commune_INSEE }, query: { isEpci: false } }">
                      {{ town.nom_commune }}
                    </nuxt-link>
                    <v-divider class="mt-3" />
                  </v-col>
                </v-row>
              </v-container>
            </v-expansion-panel-content>
          </v-expansion-panel>
        </v-expansion-panels>
      </v-col>
    </v-row>
    <v-row>
      <v-col cols="12">
        <h2>Documents d'urbanisme</h2>
        <p>
          Documents d’urbanismes disponibles pour la commune recherchée :
        </p>
      </v-col>
      <v-col cols="12">
        <DashboardDUItem
          v-for="(item,i) in 5"
          :key="'du_' + i"
        />
      </v-col>
    </v-row>
  </v-container>
</template>
<script>
import axios from 'axios'

export default {
  data () {
    return {
      collectivite: null
    }
  },
  computed: {
    isEpci () {
      return this.$route.query.isEpci === true || (this.$route.query.isEpci === 'true')
    }
  },
  async mounted () {
    const { data: collectivite } = await axios({
      url: `/api/${this.isEpci ? 'epci' : 'communes'}/${this.$route.params.collectiviteId}`,
      method: 'get'
    })
    collectivite.name = this.isEpci ? collectivite.label : collectivite.nom_commune
    this.collectivite = collectivite
    console.log('collectivite: ', this.collectivite)
  }
}
</script>
