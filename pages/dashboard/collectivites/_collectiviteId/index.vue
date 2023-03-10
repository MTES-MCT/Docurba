<template>
  <div v-if="collectivite">
    <v-container>
      <v-row>
        <v-col cols="12">
          <h1>{{ collectivite.name }}</h1>
        </v-col>
      </v-row>
    </v-container>
    <nuxt-child :is-epci="isEpci" :collectivite="collectivite" />
  </div>
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
    // this.loadCommuneEvents(this.collectivite)
  }
}
</script>
