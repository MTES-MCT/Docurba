<template>
  <v-container v-if="collectivite">
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
        <div v-for="(dgdItem) in rawDetails" :key="'dgd_' + dgdItem.dgd_noseriedgd" class="d-flex">
          <div>
            <div>année</div>
            <div>
              {{ dgdItem.dgd_anneedgd }}
            </div>
          </div>
          <div class="ml-4">
            <div>cat.</div>
            <div>
              {{ dgdItem.dgd_categoriedgd }}
            </div>
          </div>
          <div class="ml-4">
            <div>commentaire</div>
            <div>
              {{ dgdItem.dgd_commentaire }}
            </div>
          </div>
          <div class="ml-4">
            <div>montant</div>
            <div>
              {{ dgdItem.dgd_montantdgd }}
            </div>
          </div>
        </div>
      </v-col>
    </v-row>
    <v-row>
      <v-col cols="12">
        <div>
          <p>Commentaire / Note</p>
          <p>Lorem ipsum dolor sit amet consectetur adipisicing elit. Enim magni necessitatibus corrupti! Vel sequi enim delectus deleniti est et quas, suscipit hic in molestiae minima placeat accusantium molestias esse ipsum!</p>
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
      collectivite: null,
      icons: {
        mdiArrowLeft
      },
      rawDetails: null,
      versements: [
        {
          done: true,
          year: 2019,
          category: 2,
          amount: 1000,
          amountAtDate: 500
        }
      ]
    }
  },
  async mounted () {
    this.collectivite = await this.$sudocu.getCurrentCollectivite(this.$route.params.collectiviteId, 'commune')
    this.rawDetails = await this.$sudocu.getProcedureInfosDgd(this.$route.params.procedureId)
    console.log('details: ', this.rawDetails)
  }
}
</script>
