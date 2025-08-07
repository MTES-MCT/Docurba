<template>
  <div v-if="collectivite">
    <v-container>
      <v-row>
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
export default {
  name: 'Collectivite',
  data () {
    return {
      snackbar: {
        visible: false,
        message: ''
      },
      collectivite: null,
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
      const response = await fetch(`/collectivite_json/${this.$route.params.collectiviteId}/`)
      const json = await response.json()
      this.collectivite = json.collectivite
      this.schemas = json.schemas
      this.plans = json.plans
    }
  }
}
</script>
