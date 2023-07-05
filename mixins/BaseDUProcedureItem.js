export default {
  computed: {
    status () {
      // TODO: Attention, il faut surement comparer les précédents pour ne pas mettre précédent sur les procédure principales opposable qui n'ont pas eu de révision
      if ((this.procedure.dateExecutoire || this.procedure.dateApprobation) && this.procedure.idProcedurePrincipal) {
        return { text: 'opposable', color: 'success lighten-2' }
      } else if (this.procedure.dateExecutoire && !this.procedure.idProcedurePrincipal) {
        return { text: 'précédent', color: '' }
      } else if (this.procedure.dateLancement) {
        return { text: 'en cours', color: 'ongoing lighten-1' }
      } else {
        return { text: 'abandonné', color: 'error' }
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
