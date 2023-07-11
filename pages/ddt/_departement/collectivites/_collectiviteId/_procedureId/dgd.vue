<template>
  <v-container v-if="collectivite && procedure">
    <v-row>
      <v-col cols="12">
        <h1 class="text-h1">
          {{ collectivite.name }} <span v-if="collectivite.code_commune_INSEE">({{ collectivite.code_commune_INSEE }})</span>
        </h1>
      </v-col>
      <v-col cols="12">
        <div class="d-flex">
          <nuxt-link
            :to="{ name: `ddt-departement-collectivites-collectiviteId-${$sudocu.isEpci($route.params.collectiviteId) ? 'epci' : 'commune'}`, params: { departement: $route.params.departement, collectiviteId: $route.params.collectiviteId }}"
          >
            <v-icon small color="primary" class="mr-2">
              {{ icons.mdiArrowLeft }}
            </v-icon>
            <span>Revenir à mon tableau de bord</span>
          </nuxt-link>
        </div>
      </v-col>
    </v-row>
    <v-row>
      <v-col cols="12">
        <h1 class="text-h2">
          DGD
        </h1>
      </v-col>
    </v-row>
    <v-row>
      <v-col cols="12">
        <div v-for="(dgdItem) in rawDetails" :key="'dgd_' + dgdItem.dgd_noseriedgd" class="d-flex  border-light rounded mb-4 pa-4 white-bg">
          <div class="mr-8">
            <div class="text-caption g600--text">
              Année
            </div>
            <div>
              {{ dgdItem.dgd_anneedgd }}
            </div>
          </div>
          <div class="ml-4 mr-8">
            <div class="text-caption g600--text">
              Catégorie
            </div>
            <div>
              {{ dgdItem.dgd_categoriedgd }}
            </div>
          </div>
          <!-- <div class="ml-4">
            <div>commentaire</div>
            <div>
              {{ dgdItem.dgd_commentaire }}
            </div>
          </div> -->
          <div class="ml-4">
            <div class="text-caption g600--text">
              Montant versé à ce jour (€)
            </div>
            <div>
              {{ dgdItem.dgd_montantdgd }}
            </div>
          </div>
        </div>
      </v-col>
    </v-row>
    <v-row>
      <v-col cols="12">
        <div class="border-light rounded mb-4 pa-4 white-bg">
          <p class="font-weight-black">
            Commentaire / Note
          </p>
          <p v-if="procedure.commentaireDgd">
            {{ procedure.commentaireDgd }}
          </p>
          <p v-else class="text--secondary font-italic">
            Pas de commentaire
          </p>
        </div>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import { mdiArrowLeft } from '@mdi/js'

export default {
  name: 'Dgd',
  layout: 'ddt',
  data () {
    return {
      procedure: null,
      collectivite: null,
      icons: {
        mdiArrowLeft
      },
      rawDetails: null
    }
  },
  async mounted () {
    this.collectivite = await this.$sudocu.getCurrentCollectivite(this.$route.params.collectiviteId, 'commune')
    this.rawDetails = (await this.$sudocu.getProcedureInfosDgd(this.$route.params.procedureId)).sort((a, b) => b.dgd_anneedgd - a.dgd_anneedgd)
    this.procedure = await this.$sudocu.getProcedures(this.$route.params.collectiviteId)
    console.log('details: ', this.rawDetails)
  }
}
</script>

<style lang="scss">
.white-bg{
  background: white !important;
}
</style>
