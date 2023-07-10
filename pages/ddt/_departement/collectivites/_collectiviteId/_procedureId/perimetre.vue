<template>
  <v-container>
    <v-row>
      <v-col cols="12">
        <div class="text-h1">
          Liste des communes concernées
        </div>
      </v-col>
      <v-col cols="12">
        <div class="d-flex">
          <!-- <nuxt-link
            :to="{ name: `ddt-departement-collectivites-collectiviteId-${$sudocu.isEpci($route.params.collectiviteId) ? 'epci' : 'commune'}`, params: { departement: $route.params.departement, collectiviteId: $route.params.collectiviteId }}"
          >
            <v-icon small color="primary" class="mr-2">
              {{ icons.mdiArrowLeft }}
            </v-icon>
            <span>Revenir à mon tableau de bord</span>
          </nuxt-link> -->
        </div>
      </v-col>
    </v-row>
    <DashboardDdtInfosTabs />
    <v-row>
      <v-col cols="12">
        <div class="text-h2">
          Description
        </div>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
export default {
  name: 'InformationsGenerales',
  layout: 'ddt',
  data () {
    return {

    }
  },
  async mounted () {
    this.collectivite = await this.$sudocu.getCurrentCollectivite(this.$route.params.collectiviteId, 'commune')
  }
}
</script>
