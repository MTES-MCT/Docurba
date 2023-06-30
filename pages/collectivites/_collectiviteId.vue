<template>
  <div v-if="communes && collectivite && region">
    <v-container>
      <v-row>
        <v-col cols="12">
          <h1>{{ isEpci ? collectivite.label : collectivite.name }} </h1>
        </v-col>
      </v-row>
    </v-container>
    <nuxt-child :is-epci="isEpci" :collectivite="collectivite" :communes="communes" :region="region" @snackMessage="Object.assign(snackbar, {visible: true, message: arguments[0]})" />
    <v-snackbar v-model="snackbar.visible" top right color="success">
      {{ snackbar.message }}
    </v-snackbar>
  </div>
</template>

<script>
import axios from 'axios'
import regions from '@/assets/data/Regions.json'

export default {
  name: 'Collectivite',
  data () {
    return {
      snackbar: {
        visible: false,
        message: ''
      },
      regions,
      communes: null,
      collectivite: null
    }
  },
  computed: {
    isEpci () {
      return this.$route.query.isEpci === true || (this.$route.query.isEpci === 'true')
    },
    region () {
      return this.regions.find(e => e.code === this.communes[0].code_region.toString())
    }
  },
  async mounted () {
    const { data: collectivite } = await axios({
      url: `/api/${this.isEpci ? 'epci' : 'communes'}/${this.$route.params.collectiviteId}`,
      method: 'get'
    })

    collectivite.name = this.isEpci ? collectivite.label : collectivite.nom_commune
    collectivite.id = this.isEpci ? '' : collectivite.code_commune_INSEE.toString().padStart(5, '0')

    this.collectivite = collectivite
    if (this.isEpci) {
      this.communes = collectivite.towns
    } else {
      this.communes = [collectivite]
    }
  }
}
</script>
