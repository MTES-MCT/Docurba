<template>
  <v-container v-if="collectivite">
    <v-row>
      <v-col cols="12">
        <h1 class="text-h1">
          {{ collectivite.intitule }} ({{ collectivite.code }})
        </h1>
      </v-col>
      <v-col cols="12">
        <div class="d-flex">
          <nuxt-link
            :to="{ name: `ddt-departement-collectivites-collectiviteId-${$urbanisator.isEpci($route.params.collectiviteId) ? 'epci' : 'commune'}`, params: { departement: $route.params.departement, collectiviteId: $route.params.collectiviteId }}"
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
        <div v-for="(dgdItem) in dgdItems" :key="'dgd_' + dgdItem.dgd_noseriedgd" class="d-flex  border-light rounded mb-4 pa-4 white-bg">
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
          <p v-if="commentaire">
            {{ commentaire }}
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
      commentaire: null,
      dgdItems: null,
      icons: {
        mdiArrowLeft
      },
      rawDetails: null
    }
  },
  async mounted () {
    const { commentaire, dgdItems, collectivite } = (await this.$sudocu.getProcedureInfosDgd(this.$route.params.procedureId))
    console.log('DGD: ', commentaire, dgdItems, collectivite)
    this.commentaire = commentaire
    this.collectivite = collectivite
    this.dgdItems = dgdItems.sort((a, b) => b.dgd_anneedgd - a.dgd_anneedgd)
  }
}
</script>

<style lang="scss">
.white-bg{
  background: white !important;
}
</style>
