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
      @snackMessage="Object.assign(snackbar, {visible: true, message: arguments[0]})"
    />
    <v-snackbar v-model="snackbar.visible" top right color="success">
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
      procedures: null
    }
  },
  computed: {
    isEpci () {
      return this.$urbanisator.isEpci(this.$route.params.collectiviteId)
    }
  },
  async mounted () {
    const collectiviteProcedures = await this.$sudocu.getProceduresCollectivite(this.$route.params.collectiviteId)
    this.collectivite = collectiviteProcedures.collectivite
    const { procedures } = await this.isPublic ? this.$urbanisator.getProjectsProcedures(this.collectivite.id) : { projects: [], procedures: [] }
    this.procedures = [...collectiviteProcedures.procedures, ...procedures]
  }
}
</script>
