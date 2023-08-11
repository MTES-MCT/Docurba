export default {
  computed: {
    status () {
      // TODO: Attention, il faut surement comparer les précédents pour ne pas mettre précédent sur les procédure principales opposable qui n'ont pas eu de révision
      if ((this.procedure.enforceable_date || this.procedure.approval_date) && this.procedure.procedure_id) {
        return { text: 'opposable', color: 'success lighten-2' }
      } else if (this.procedure.enforceable_date && !this.procedure.procedure_id) {
        return { text: 'précédent', color: '' }
      } else if (this.procedure.launch_date) {
        return { text: 'en cours', color: 'ongoing lighten-1' }
      } else {
        return { text: 'abandonné', color: 'error' }
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
