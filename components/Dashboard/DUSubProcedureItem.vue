<template>
  <v-container>
    <v-row>
      <v-col cols="12" class="text-subtitle-1 font-weight-bold">
        <v-chip :color="status.color" label class="text-uppercase mr-2">
          {{ status.text }}
        </v-chip>
        {{ procedure.typeProcedure }}
        - {{ procedure.idProcedure }} - parent: {{ procedure.idProcedurePrincipal }}
      </v-col>
    </v-row>
    <v-row class="mt-0">
      <!-- <v-col>
        <div class="text-caption g600--text">
          Statut
        </div>
        <div>
          <v-chip :color="status.color">
            {{ status.text }}
          </v-chip>
        </div>
      </v-col> -->
      <v-col>
        <div class="text-caption g600--text">
          Type de procédure
        </div>
        <div>
          {{ procedure.typeProcedure }}
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
        <div v-if="procedure.commentaireProcedure || procedure.commentaireDgd">
          <p>{{ procedure.commentaireProcedure }} </p>
          <p>{{ procedure.commentaireDgd }} </p>
        </div>
        <div v-else class="text--disabled">
          Pas de commentaire
        </div>
      </v-col>
      <v-col cols="12" class="pb-0">
        <v-divider />
      </v-col>
      <v-col cols="12">
        <DashboardDUModalPerimetre v-if="procedure.perimetre" :towns="procedure.perimetre" />
        <nuxt-link :to="{name: 'ddt-departement-collectivites-collectiviteId-frise-procedureId', params: {departement: $route.params.departement, collectiviteId: $route.params.collectiviteId, procedureId: procedure.idProcedure}}">
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
      <v-col cols="12" class="d-flex align-center justify-end ">
        <DashboardDUModalPerimetre v-if="procedure.perimetre" :towns="procedure.perimetre" />
        <v-spacer />
        <v-btn text color="primary" :to="{name: 'ddt-departement-collectivites-collectiviteId-frise-procedureId', params: {departement: $route.params.departement ,collectiviteId: $route.params.collectiviteId, procedureId: procedure.idProcedure}}">
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
  }
}
</script>
