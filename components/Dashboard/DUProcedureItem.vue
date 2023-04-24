<template>
  <v-container>
    <v-row>
      <v-col cols="12" class="text-subtitle-1 font-weight-bold">
        {{ firstEvent.docType }} - {{ firstEvent.idProcedure }} - parent: {{ firstEvent.idProcedurePrincipal }}
      </v-col>
    </v-row>
    <v-row class="mt-0">
      <v-col>
        <div class="text-caption g600--text">
          Statut
        </div>
        <div>
          <v-chip :color="status.color">
            {{ status.text }}
          </v-chip>
        </div>
      </v-col>
      <v-col>
        <div class="text-caption g600--text">
          Type de procédure
        </div>
        <div>
          {{ firstEvent.typeProcedure }}
        </div>
      </v-col>
      <v-col>
        <div class="text-caption g600--text">
          Etape de la procédure
        </div>
        <div>
          {{ step }}
        </div>
      </v-col>
    </v-row>
    <v-row>
      <v-col cols="12" class="pb-0">
        <v-divider />
      </v-col>
      <v-col cols="12" class="pb-0">
        <p class="font-weight-bold">
          Commentaire / Note
        </p>
        <p>{{ firstEvent.commentaireProcedure }} </p>
        <p>{{ firstEvent.commentaireDgd }} </p>
      </v-col>
      <v-col cols="12" class="pb-0">
        <v-divider />
      </v-col>
      <v-col cols="12" class="pb-0">
        <span class="primary--text text-decoration-underline mr-4">
          Liste des communes concernées
        </span>
        <nuxt-link :to="{name: 'ddt-departement-collectivites-collectiviteId-frise-duId', params: {collectiviteId: $route.params.collectiviteId, duId: firstEvent.idProcedure}}">
          <span class="primary--text text-decoration-underline mr-4">
            Feuille de route partagée
          </span>
        </nuxt-link>
        <span class="primary--text text-decoration-underline mr-4">
          PAC
        </span>
        <span class="primary--text text-decoration-underline">
          Note d'enjeux
        </span>
      </v-col>
    </v-row>
  </v-container>
</template>
<script>
export default {
  props: {
    procedure: {
      type: Object,
      required: true
    }
  },
  data () {
    return {

    }
  },
  computed: {
    firstEvent () {
      return this.procedure.events[0]
    },
    status () {
      // TODO: Attention, il faut surement comparer les précédents pour ne pas mettre précédent sur les procédure principales opposable qui n'ont pas eu de révision
      if (this.firstEvent.dateExecutoire && this.firstEvent.idProcedurePrincipal) {
        return { text: 'opposable', color: 'success lighten-2' }
      } else if (this.firstEvent.dateExecutoire && !this.firstEvent.idProcedurePrincipal) {
        return { text: 'précédent', color: '' }
      } else if (this.firstEvent.dateLancement || this.firstEvent.dateApprobation) {
        return { text: 'en cours', color: '' }
      } else {
        return { text: 'abandonné', color: 'error' }
      }
    },
    step () {
      if (this.firstEvent.dateAbandon) {
        return `Abandon (${this.firstEvent.dateAbandon})`
      } else if (this.firstEvent.dateExecutoire) {
        return `Executoire (${this.firstEvent.dateExecutoire})`
      } else if (this.firstEvent.dateApprobation) {
        return `Approbation (${this.firstEvent.dateApprobation})`
      } else if (this.firstEvent.dateLancement) {
        return `Lancement (${this.firstEvent.dateLancement})`
      }
      return '-'
    }
  }
}
</script>
