<template>
  <div class="mb-4">
    <v-card outlined class="no-border-radius-bottom">
      <v-card-text>
        <DashboardDUProcedureItem
          :procedure="procedure"
          :censored="censored"
          :collectivite="collectivite"
          :code-insee-si-communal="codeInseeSiCommunal"
          @delete="$emit('delete', arguments[0])"
        />
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
                  v-for="procSec in secondaryProcs"
                  :key="'procSec_' +procSec.id"
                  class="grey-border mb-8"
                  :procedure="procSec"
                  :censored="censored"
                  @delete="$emit('delete', arguments[0])"
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
import dayjs from 'dayjs'

export default {
  name: 'DUItem',
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
    const secondaryProcs = [...(this.procedure.procSecs || [])].sort((a, b) => {
      return +dayjs(b.created_at || 0) - +dayjs(a.created_at || 0)
    })

    return {
      secondaryProcs,
      collectivite: null
    }
  },
  computed: {
    codeInseeSiCommunal () {
      if (this.procedure.procedures_perimetres.length === 1) {
        return this.procedure.procedures_perimetres[0].code
      }
      return null
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
