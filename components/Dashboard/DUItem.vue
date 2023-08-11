<template>
  <div class="mb-4">
    <v-card outlined class="no-border-radius-bottom">
      <v-card-text>
        <DashboardDUProcedureItem :procedure="procedure" :censored="censored" />
      </v-card-text>
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
                  :key="'procSec_' +procSec.id"
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
      if (this.procedure.enforceable_date && !this.procedure.procedure_id) {
        return 'opposable'
      } else if (this.procedure.enforceable_date && this.procedure.procedure_id) {
        return 'précédent'
      } else if (this.procedure.launch_date || this.procedure.approval_date) {
        return 'en cours'
      } else {
        return 'abandonné'
      }
    },
    step () {
      if (this.procedure.abort_date) {
        return `Abandon (${this.procedure.abort_date})`
      } else if (this.procedure.enforceable_date) {
        return `Executoire (${this.procedure.enforceable_date})`
      } else if (this.procedure.approval_date) {
        return `Approbation (${this.procedure.approval_date})`
      } else if (this.procedure.launch_date) {
        return `Lancement (${this.procedure.launch_date})`
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
