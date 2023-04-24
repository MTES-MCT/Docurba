<template>
  <div class="mb-4">
    <v-card outlined class="no-border-radius-bottom">
      <v-container>
        <DashboardDUProcedureItem :procedure="procedure" />
      </v-container>
    </v-card>
    <v-container>
      <v-row>
        <v-col cols="11" offset="1" class="border-sub-procedure">
          <v-expansion-panels flat>
            <v-expansion-panel>
              <v-expansion-panel-header>
                Procédures secondaires
              </v-expansion-panel-header>
              <v-expansion-panel-content>
                <DashboardDUSubProcedureItem
                  v-for="procSec in procedure.procSecs"
                  :key="'procSec_' + procSec[0].idProcedure"
                  :procedure="{events: procSec}"
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
      if (this.firstEvent.dateExecutoire && !this.firstEvent.idProcedurePrincipal) {
        return 'opposable'
      } else if (this.firstEvent.dateExecutoire && this.firstEvent.idProcedurePrincipal) {
        return 'précédent'
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

<style lang="scss">
.border-sub-procedure{
  border-left: 1px solid #DDDDDD;
  border-right: 1px solid #DDDDDD;
  border-bottom: 1px solid #DDDDDD;
  border-bottom-left-radius: 4px;
  border-bottom-right-radius: 4px;
}

.no-border-radius-bottom{
  border-bottom-right-radius: 0px !important;
}
</style>
