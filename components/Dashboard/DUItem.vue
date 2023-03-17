<template>
  <v-card outlined class="mb-4">
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
            <v-chip>{{ status }}</v-chip>
          </div>
        </v-col>
        <v-col>
          <div class="text-caption g600--text">
            Type de procédure
          </div>
          <div>
            {{ procedure[0].typeProcedure }}
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
        <v-col cols="12">
          <span class="primary--text text-decoration-underline mr-4">
            Liste des communes concernées
          </span>
          <span class="primary--text text-decoration-underline mr-4">
            Feuille de route partagée
          </span>
          <span class="primary--text text-decoration-underline mr-4">
            PAC
          </span>
          <span class="primary--text text-decoration-underline">
            Note d'enjeux
          </span>
        </v-col>
      </v-row>
    </v-container>
  </v-card>
</template>
<script>
export default {
  props: {
    procedure: {
      type: Array,
      required: true
    }
  },
  data () {
    return {

    }
  },
  computed: {
    firstEvent () {
      return this.procedure[0]
    },
    status () {
      if (this.firstEvent.dateExecutoire) {
        return 'opposable'
      } else if (this.firstEvent.dateLancement || this.firstEvent.dateApprobation) {
        return 'en cours'
      } else {
        return 'abandonné'
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
