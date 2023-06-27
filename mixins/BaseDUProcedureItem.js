export default {
  computed: {
    firstEvent () {
      return this.procedure.events[0]
    },
    status () {
      // TODO: Attention, il faut surement comparer les précédents pour ne pas mettre précédent sur les procédure principales opposable qui n'ont pas eu de révision
      if ((this.firstEvent.dateExecutoire || this.firstEvent.dateApprobation) && this.firstEvent.idProcedurePrincipal) {
        return { text: 'opposable', color: 'success lighten-2' }
      } else if (this.firstEvent.dateExecutoire && !this.firstEvent.idProcedurePrincipal) {
        return { text: 'précédent', color: '' }
      } else if (this.firstEvent.dateLancement) {
        return { text: 'en cours', color: '' }
      } else {
        return { text: 'abandonné', color: 'error' }
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
