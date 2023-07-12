<template>
  <v-container v-if="collectivite">
    <v-row>
      <v-col cols="12">
        <h1 class="text-h1">
          {{ collectivite.name }} ({{ collectivite.code_commune_INSEE }})
        </h1>
      </v-col>
      <v-col cols="12">
        <div v-if="linkedEpci" class="d-flex">
          <nuxt-link

            :to="{ name: 'ddt-departement-collectivites-collectiviteId-epci', params: { departement: $route.params.departement, collectiviteId: linkedEpci.EPCI }}"
          >
            <v-icon small color="primary" class="mr-2">
              {{ icons.mdiArrowLeft }}
            </v-icon>
            <span>Revenir à l'EPCI</span>
          </nuxt-link>
          <div class="ml-8">
            <span class="text-h5">Appartient à {{ linkedEpci.label }}</span>
          </div>
        </div>
      </v-col>
    </v-row>
    <v-row>
      <v-col cols="12">
        <p class="text-h2">
          Documents d'urbanisme
        </p>
        <p class="text-h6">
          Documents d’urbanisme disponibles pour la commune recherchée :
        </p>
      </v-col>
    </v-row>
    <DashboardDUItemsList :procedures="procedures" collectivite-type="commune" />
  </v-container>
</template>
<script>

import { mdiArrowLeft } from '@mdi/js'
import axios from 'axios'

export default {
  name: 'Collectivite',
  layout: 'ddt',
  data () {
    return {
      linkedEpci: null,
      tab: null,
      collectivite: null,
      procedures: null,
      icons: {
        mdiArrowLeft
      }
    }
  },
  async mounted () {
    this.collectivite = await this.$urbanisator.getCurrentCollectivite(this.$route.params.collectiviteId)
    this.procedures = await this.$sudocu.getProcedures(this.$route.params.collectiviteId)
    await this.getLinkedEpci(this.$route.params.collectiviteId)
  },
  methods: {
    async getLinkedEpci (communeId) {
      const { data: epci } = await axios({
        url: `/api/epci?communeId=${communeId}`,
        method: 'get'
      })
      this.linkedEpci = epci[0]
    }
  }
}
</script>

<style lang="scss">
.border-light{
  border: solid 1px var(--v-primary-lighten1) !important;
}
</style>
