import { getProcedureTypeLabel } from '@/plugins/procedure'

export default {
  computed: {
    procedureTypeLabel () {
      return getProcedureTypeLabel(this.procedure)
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
