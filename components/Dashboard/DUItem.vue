<template>
  <div class="mb-4">
    <v-card outlined class="no-border-radius-bottom">
      <v-container>
        <DashboardDUProcedureItem :procedure="procedure" :censored="censored" />
      </v-container>
    </v-card>
    <v-container v-if="procedure.procSecs.length > 0">
      <v-row>
        <v-col cols="11" offset="1" class="border-sub-procedure">
          <v-expansion-panels flat>
            <v-expansion-panel>
              <v-expansion-panel-header>
                <span class="font-weight-bold">Procédures secondaires</span>
              </v-expansion-panel-header>
              <v-expansion-panel-content>
                <DashboardDUSubProcedureItem
                  v-for="procSec in procedure.procSecs"
                  :key="'procSec_' + procSec[0].idProcedure"
                  :procedure="{events: procSec}"
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
