<template>
  <v-container>
    <v-row>
      <v-col cols="12" class="text-subtitle-1 font-weight-bold">
        <span v-if=" procedure.project.doc_type === 'SCOT'">
          {{ procedure.name }}
        </span>
        <div v-else>
          <span>{{ procedure.project.doc_type }}</span>
          <span> {{ procedure.perimetre.length === 1 ? procedure.perimetre[0].name + ' (' + procedure.perimetre[0].inseeCode + ')' : '' }}</span>
        </div>

        <br>
        id - {{ procedure.id }} - parent: {{ procedure.procedure_id }}
      </v-col>
    </v-row>
    <v-row class="mt-0">
      <v-col>
        <div class="text-caption g600--text">
          Statut
        </div>
        <div>
          <v-chip :color="status.color" small label class="text-uppercase mr-2">
            {{ status.text }}
          </v-chip>
        </div>
      </v-col>
      <v-col>
        <div class="text-caption g600--text">
          Type de procédure
        </div>
        <div>
          {{ procedure.type }}
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
        <p v-if="procedure.commentaireProcedure">
          {{ procedure.commentaireProcedure }}
        </p>
        <p v-if="procedure.commentaireDgd">
          {{ procedure.commentaireDgd }}
        </p>
      </v-col>
      <v-col cols="12" class="pb-0">
        <v-divider />
      </v-col>
      <v-col cols="12" class="pb-0">
        <DashboardDUModalPerimetre v-if="procedure.project.towns" :towns="procedure.project.towns" />
        <nuxt-link :to="{name: 'frise-procedureId', params: {procedureId: procedure.id}}">
          <span class="primary--text text-decoration-underline mr-4">
            Feuille de route partagée
          </span>
        </nuxt-link>
        <nuxt-link
          :to="{
            name: 'ddt-departement-collectivites-collectiviteId-procedureId-dgd',
            params: {
              departement: $route.params.departement,
              collectiviteId: $route.params.collectiviteId,
              procedureId: procedure.id
            }
          }"
        >
          <span class="primary--text text-decoration-underline mr-4 ">
            DGD
          </span>
        </nuxt-link>
        <nuxt-link
          :to="{
            name: 'ddt-departement-collectivites-collectiviteId-procedureId-infos',
            params: {
              departement: $route.params.departement,
              collectiviteId: $route.params.collectiviteId,
              procedureId: procedure.id
            }
          }"
        >
          <span class="primary--text text-decoration-underline mr-4 ">
            Info. générales
          </span>
        </nuxt-link>
        <span class="primary--text text-decoration-underline mr-4 text--disabled">
          PAC
        </span>
        <!-- <span class="primary--text text-decoration-underline text--disabled">
          Note d'enjeux
        </span> -->
      </v-col>
    </v-row>
    <v-row v-else>
      <v-col cols="12" class="pb-0">
        <v-divider />
      </v-col>
      <v-col cols="12" class="d-flex align-center justify-end pb-0">
        <DashboardDUModalPerimetre v-if="procedure.project.towns" :towns="procedure.project.towns" />
        <v-spacer />
        <v-btn text color="primary" :to="{name: 'frise-procedureId', params: {procedureId: procedure.id}}">
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
      return this.procedure.project.towns.length > 1
    },
    status () {
      if (this.procedure.abort_date) {
        return { text: 'abandonné', color: 'error' }
      }
      // si ce n'est pas un PLU
      if (!this.isPlui) {
        // TODO: managed approved in towns for docurba model ?
        if (this.procedure.approvedInTowns.includes(this.procedure.perimetre[0].inseeCode)) {
          return { text: 'opposable', color: 'success lighten-2' }
        } else if (this.procedure.ongoingInTowns.includes(this.procedure.perimetre[0].inseeCode)) {
          return { text: 'en cours', color: '' }
        } else {
          return { text: 'précédent', color: '' }
        }
      } else {
        // Si on est dans un cas de PLUi
        if ((this.procedure.enforceable_date || this.procedure.approval_date) && this.procedure.procedure_id) {
          return { text: 'opposable', color: 'success lighten-2' }
        } else if (this.procedure.enforceable_date && !this.procedure.procedure_id) {
          return { text: 'précédent', color: '' }
        }
        // implicite si date de lancement
        return { text: 'en cours', color: '' }
      }
    }
  }
}
</script>
