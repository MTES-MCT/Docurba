<template>
  <div v-if="collectivite">
    <v-container>
      <v-row>
        <v-col cols="12">
          <LayoutsBannerAlert />
        </v-col>
        <v-col cols="12">
          <h1>{{ collectivite.intitule }} ({{ collectivite.code }})</h1>
        </v-col>
      </v-row>
    </v-container>
    <nuxt-child
      v-if="loaded"
      :is-epci="isEpci"
      :collectivite="collectivite"
      :procedures="plans"
      :communes="communes"
      :schemas="schemas"
      @snackMessage="Object.assign(snackbar, {visible: true, message: arguments[0]})"
    />
    <VGlobalLoader v-else />
    <v-snackbar v-model="snackbar.visible" app top right color="success">
      {{ snackbar.message }}
    </v-snackbar>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'Collectivite',
  data () {
    return {
      snackbar: {
        visible: false,
        message: ''
      },
      collectivite: null,
      communes: [],
      plans: [],
      schemas: [],
      loaded: false,
      showTally: false
    }
  },
  computed: {
    isEpci () {
      return this.$urbanisator.isEpci(this.$route.params.collectiviteId)
    }
  },
  async mounted () {
    await this.getProcedures()
    this.loaded = true
  },
  methods: {
    async getProcedures () {
      // console.log('this.$route.params.collectiviteId: ', this.$route.params.collectiviteId)
      const { data: collectivite } = await axios({
        url: `/api/geo/collectivites/${this.$route.params.collectiviteId}`
      })

      this.collectivite = collectivite
      this.communes = this.isEpci ? this.collectivite.membres.filter(m => m.type.startsWith('COM')) : [this.collectivite]

      const { plans, schemas } = await this.$urbanisator.getProjects(this.$route.params.collectiviteId)
      this.schemas = schemas
      this.plans = plans

      // console.log('schemas: ', schemas, ' plans: ', plans)
    }
  }
}
</script>
