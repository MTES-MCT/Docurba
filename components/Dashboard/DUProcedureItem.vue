<template>
  <v-container>
    <v-row>
      <v-col cols="12" class="text-subtitle-1 font-weight-bold">
        <span v-if="firstEvent.docType === 'PLU'">{{ isPlui ? 'PLUi' : 'PLU' }}</span>
        <span v-else>{{ firstEvent.docType }}</span>
        <span> {{ procedure.perimetre.length === 1 ? procedure.perimetre[0].name + ' (' + procedure.perimetre[0].inseeCode + ')' : '' }}</span>
        <br>
        id - {{ firstEvent.idProcedure }} - parent: {{ firstEvent.idProcedurePrincipal }}
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
    <v-row v-if="!censored">
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
        <DashboardDUModalPerimetre v-if="procedure.perimetre" :towns="procedure.perimetre" />
        <nuxt-link :to="{name: 'ddt-departement-collectivites-collectiviteId-frise-procedureId', params: {departement: $route.params.departement ,collectiviteId: $route.params.collectiviteId, procedureId: firstEvent.idProcedure}, query: $route.query}">
          <span class="primary--text text-decoration-underline mr-4">
            Feuille de route partagée
          </span>
        </nuxt-link>
        <span class="primary--text text-decoration-underline mr-4 text--disabled">
          PAC
        </span>
        <span class="primary--text text-decoration-underline text--disabled">
          Note d'enjeux
        </span>
      </v-col>
    </v-row>
    <v-row v-else>
      <v-col cols="12" class="pb-0">
        <v-divider />
      </v-col>
      <v-col cols="12" class="d-flex align-end justify-end pb-0">
        <v-btn text color="primary" :to="{name: 'ddt-departement-collectivites-collectiviteId-frise-procedureId', params: {departement: $route.params.departement ,collectiviteId: $route.params.collectiviteId, procedureId: firstEvent.idProcedure}, query: $route.query}">
          <v-icon small color="primary" class="mr-2">
            {{ icons.mdiArrowRight }}
          </v-icon>
          Feuille de route publique
        </v-btn>
      </v-col>
    </v-row>
  </v-container>
</template>
<script>
import { mdiArrowRight } from '@mdi/js'
import BaseDUProcedureItem from '@/mixins/BaseDUProcedureItem.js'

export default {
  mixins: [BaseDUProcedureItem],
  props: {
    procedure: {
      type: Object,
      required: true
    },
    censored: {
      type: Boolean,
      default: () => false
    }
  },
  data () {
    return {
      icons: {
        mdiArrowRight
      }
    }
  },
  computed: {
    isPlui () {
      return this.procedure.perimetre.length > 1
    },
    status () {
      if (this.firstEvent.dateAbandon) {
        return { text: 'abandonné', color: 'error' }
      }
      // si ce n'est pas un PLU
      if (!this.isPlui) {
        if (this.procedure.approvedInTowns.includes(this.procedure.perimetre[0].inseeCode)) {
          return { text: 'opposable', color: 'success lighten-2' }
        } else if (this.procedure.ongoingInTowns.includes(this.procedure.perimetre[0].inseeCode)) {
          return { text: 'en cours', color: '' }
        } else {
          return { text: 'précédent', color: '' }
        }
      } else {
        // Si on est dans un cas de PLUi
        if ((this.firstEvent.dateExecutoire || this.firstEvent.dateApprobation) && this.firstEvent.idProcedurePrincipal) {
          return { text: 'opposable', color: 'success lighten-2' }
        } else if (this.firstEvent.dateExecutoire && !this.firstEvent.idProcedurePrincipal) {
          return { text: 'précédent', color: '' }
        }
        // implicite si date de lancement
        return { text: 'en cours', color: '' }
      }
    }
  }
}
</script>
