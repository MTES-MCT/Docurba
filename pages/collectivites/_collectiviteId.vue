<template>
  <div v-if="collectivite">
    <v-container>
      <v-row>
        <v-col cols="12">
          <h1>{{ collectivite.intituleComplet }} </h1>
        </v-col>
      </v-row>
    </v-container>
    <nuxt-child
      :is-epci="isEpci"
      :collectivite="collectivite"
      :procedures="procedures"
      :communes="isEpci ? collectivite.communes : [collectivite]"
      :schemas="schemas"
      @snackMessage="Object.assign(snackbar, {visible: true, message: arguments[0]})"
    />
    <v-snackbar v-model="snackbar.visible" top right color="success">
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
      procedures: [],
      schemas: []
    }
  },
  computed: {
    isEpci () {
      return this.$urbanisator.isEpci(this.$route.params.collectiviteId)
    }
  },
  async mounted () {
    const { collectivite, schemas, procedures } = (await axios({ url: `/api/urba/collectivites/${this.$route.params.collectiviteId}`, method: 'get' })).data

    this.collectivite = collectivite
    this.schemas = schemas
    this.procedures = procedures
  }
}
</script>
