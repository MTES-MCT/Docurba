<template>
  <div v-if="collectivite">
    <v-container>
      <v-row>
        <v-col cols="12">
          <h1>{{ isEpci ? collectivite.label : collectivite.name }} </h1>
        </v-col>
      </v-row>
    </v-container>
    <nuxt-child
      :is-epci="isEpci"
      :collectivite="collectivite"
      :procedures="procedures"
      :communes="isEpci ? collectivite.towns : [collectivite]"
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
    this.collectivite = await this.$urbanisator.getCurrentCollectivite(this.$route.params.collectiviteId)
    this.procedures = await this.$sudocu.getProcedures(this.$route.params.collectiviteId)
  }
}
</script>
