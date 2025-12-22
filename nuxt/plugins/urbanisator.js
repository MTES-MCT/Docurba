import Vue from 'vue'
import { groupBy, uniqBy, orderBy, maxBy } from 'lodash'

export default ({ $supabase }, inject) => {
  Vue.filter('docType', function (procedure) {
    if (procedure.doc_type === 'PLU') {
      let docType = procedure.doc_type
      if (procedure.current_perimetre.length > 1) { docType += 'i' }
      if (procedure.is_sectoriel && (procedure.status === 'opposable' || procedure.status === 'en cours')) {
        docType += 'S'
      }
      if (procedure.is_pluih) { docType += 'H' }
      if (procedure.is_pdu) { docType += 'D' }

      return docType
    } else { return procedure.doc_type }
  })

  inject('urbanisator', {
    isEpci (collectiviteId) {
      return collectiviteId.length > 5
    },
    async getProceduresForDept (departementCode) {
      const { data } = await $supabase.from('procedures_perimetres')
        .select('*, procedures!inner(*, doc_frise_events(*))')
        .eq('departement', departementCode)
        .is('procedures.archived', false)
        .throwOnError()
      const groupedProceduresPerim = groupBy(data, e => e.procedure_id)
      const procedures = data.map((e) => {
        const lastEvent = maxBy(e.procedures.doc_frise_events, 'date_iso')
        const prescriptionDate = e.procedures.doc_frise_events.find(y => y.code === 'PRES')
        return { ...e, perimetre: groupedProceduresPerim[e.procedure_id], last_event: lastEvent, prescription: prescriptionDate }
      })
      const uniqProcedures = uniqBy(procedures, e => e.procedure_id)
      const orderedProcedures = orderBy(uniqProcedures, e => e.last_event?.date_iso, ['desc'])
      return orderedProcedures
    },
    parseProceduresStatus (procedures) {
      procedures.forEach((procedure) => {
        const comd = procedure.procedures_perimetres.find(p => p.collectivite_type === 'COMD')

        // COMD specifique
        if (procedure.procedures_perimetres.length === 2 && comd) {
          procedure.procedures_perimetres = procedure.procedures_perimetres.filter((p) => {
            return p.collectivite_type === 'COMD'
          })
        }

        if (procedure.status === 'opposable') {
          const isOpposable = !!procedure.procedures_perimetres.find(p => p.opposable)

          if (!isOpposable) {
            procedure.status = 'precedent'
          }
        }
      })

      return procedures
    },
    async getCollectivitesProcedures (codes) {
      const { data: procedures } = await $supabase.rpc('procedures_by_collectivites', {
        codes
      })

      const filteredProcedures = procedures.filter((p) => {
        return p.type !== 'Abrogation' &&
          !p.secondary_procedure_of &&
          !p.archived &&
        // The specific ID here is to prevent a duplicated created by sudocuh. This is suposed to be temporary for a demo.
          p.id !== '760d88f0-008d-4505-98f6-a7a9a2ebaf61'
      })

      return this.parseProceduresStatus(filteredProcedures)
    }
  })
}
