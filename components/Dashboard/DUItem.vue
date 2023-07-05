<template>
  <div class="mb-4">
    <v-card outlined class="no-border-radius-bottom">
      <v-container>
        <DashboardDUProcedureItem :procedure="procedure" :censored="censored" />
      </v-container>
    </v-card>
    <v-container v-if="procedure.procSecs?.length > 0">
      <v-row>
        <v-col cols="11" offset="1" class="sub-procedure">
          <v-expansion-panels flat>
            <v-expansion-panel>
              <v-expansion-panel-header class="primary lighten-4">
                <span class="font-weight-bold">Procédures secondaires</span>
              </v-expansion-panel-header>
              <v-expansion-panel-content class="primary lighten-4">
                <DashboardDUSubProcedureItem
                  v-for="procSec in procedure.procSecs"
                  :key="'procSec_' +procSec.idProcedure"
                  class="grey-border mb-8"
                  :procedure="procSec"
                  :censored="censored"
                />
              </v-expansion-panel-content>
            </v-expansion-panel>
          </v-expansion-panels>
        </v-col>
      </v-row>
    </v-container>
  </div>
</template>
<script>
export default {
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

    }
  },
  computed: {
    status () {
      if (this.procedure.dateExecutoire && !this.procedure.idProcedurePrincipal) {
        return 'opposable'
      } else if (this.procedure.dateExecutoire && this.procedure.idProcedurePrincipal) {
        return 'précédent'
      } else if (this.procedure.dateLancement || this.procedure.dateApprobation) {
        return 'en cours'
      } else {
        return 'abandonné'
      }
    },
    step () {
      if (this.procedure.dateAbandon) {
        return `Abandon (${this.procedure.dateAbandon})`
      } else if (this.procedure.dateExecutoire) {
        return `Executoire (${this.procedure.dateExecutoire})`
      } else if (this.procedure.dateApprobation) {
        return `Approbation (${this.procedure.dateApprobation})`
      } else if (this.procedure.dateLancement) {
        return `Lancement (${this.procedure.dateLancement})`
      }
      return '-'
    }
  }
}
</script>

<style lang="scss">
.sub-procedure{
  border-left: 1px solid #DDDDDD !important;
  border-right: 1px solid #DDDDDD !important;
  border-bottom: 1px solid #DDDDDD !important;
  border-bottom-left-radius: 4px;
  border-bottom-right-radius: 4px;
  background-color: var(--v-primary-lighten4);
}

.no-border-radius-bottom{
  border-bottom-right-radius: 0px !important;
}

.grey-border{
  border-radius: 4px;
  border: 1px solid #DDDDDD !important;
  background: #FFF;
}
</style>
