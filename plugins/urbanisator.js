import Vue from 'vue'
import { groupBy, uniqBy, mapValues } from 'lodash'

export default ({ $supabase, $dayjs }, inject) => {
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
    async getProceduresByCommunes (departementCode) {
      // TODO: Update postgres to make order works
      // TODO: Optimise with index, selected fields, order and limit
      const { data } = await $supabase.from('procedures_perimetres')
        .select('*, procedures_duplicate(*, doc_frise_events_duplicate(*))')
        .eq('departement', departementCode)
        // .order('date_iso', { referencedTable: 'procedures_duplicate.doc_frise_events_duplicate', ascending: false })
      const groupedProceduresPerim = groupBy(data, e => e.collectivite_code)
      const planScotsSeparated = mapValues(groupedProceduresPerim, (e) => {
        const plans = e.filter(e => !e.procedures_duplicate.is_scot)
        const scots = e.filter(e => e.procedures_duplicate.is_scot)
        return { scots, plans }
      })
      return planScotsSeparated
    },
    async getProceduresForDept (departementCode, { minimal = false } = {}) {
      // TODO: Update postgres to make order works
      // TODO: Optimise with index, selected fields, order and limit
      let select = '*, procedures_duplicate(*, doc_frise_events_duplicate(*))'
      if (minimal) {
        select = '*, procedures_duplicate(*, doc_frise_events_duplicate(*))'
      }
      const { data } = await $supabase.from('procedures_perimetres')
        .select(select)
        .eq('departement', departementCode)
        // .order('date_iso', { referencedTable: 'procedures_duplicate.doc_frise_events_duplicate', ascending: false })
      const groupedProceduresPerim = groupBy(data, e => e.procedure_id)
      const procedures = data.map((e) => {
        const lastEvent = e.procedures_duplicate.doc_frise_events_duplicate[0]
        const prescriptionDate = e.procedures_duplicate.doc_frise_events_duplicate.find(e => e.code === 'PRES')
        return { ...e, perimetre: groupedProceduresPerim[e.procedure_id], last_event: lastEvent, prescription: prescriptionDate }
      })
      return uniqBy(procedures, e => e.procedure_id)
    },
    async getCommuneProcedures (inseeCode) {
      const { data: perimetre } = await $supabase.from('procedures_perimetres').select('*').eq('collectivite_code', inseeCode)
      const { data: procedures } = await $supabase.from('procedures_duplicate')
        .select('*').eq('archived', false)
        .in('id', perimetre.map(p => p.procedure_id))

      procedures.forEach((procedure) => {
        const perim = perimetre.find(p => p.procedure_id === procedure.id)
        if (procedure.status === 'opposable' && !perim.opposable) {
          procedure.status = 'precedent'
        }
      })

      return procedures
    },
    async getIntercoProcedures (collectiviteId) {
      const { data: procedures } = await $supabase.from('procedures_duplicate')
        .select('*').eq('archived', false)
        .eq('collectivite_porteuse_id', collectiviteId)

      return procedures
    },
    async getProceduresPerimetre (procedures) {
      const { data: perimetre } = await $supabase.from('procedures_perimetres').select('*')
        .in('procedure_id', procedures.map(p => p.id))

      procedures.forEach((procedure) => {
        // This is to manage legacy structure
        procedure.current_perimetre = perimetre.filter(p => p.procedure_id === procedure.id)
        procedure.current_perimetre.forEach((c) => {
          c.inseeCode = c.collectivite_code
        })
      })

      return procedures
    },
    async getProjects (collectiviteId) {
      try {
        let procedures = []

        if (collectiviteId.length > 5) {
          procedures = await this.getIntercoProcedures(collectiviteId)
        } else {
          procedures = await this.getCommuneProcedures(collectiviteId)
        }

        procedures = await this.getProceduresPerimetre(procedures)
        const groupedSubProcedures = groupBy(procedures, 'secondary_procedure_of')

        const proceduresPrincipales = procedures.filter(p => p.is_principale)
          .map((p) => {
            const { projects, ...rest } = p
            return { ...rest, project: projects, procSecs: groupedSubProcedures[p.id] }
          })

        proceduresPrincipales.sort((a, b) => {
          return +$dayjs(a.created_at) - +$dayjs(b.created_at)
        })

        const schemas = proceduresPrincipales.filter(e => e.doc_type === 'SCOT')
        const plans = proceduresPrincipales.filter(e => e.doc_type !== 'SCOT')

        // eslint-disable-next-line no-console
        console.log('urbanisator get projects', { schemas, plans })
        return { schemas, plans }
      } catch (error) {
        // eslint-disable-next-line no-console
        console.log('urbanisator error', error)
      }
    }
  })
}
