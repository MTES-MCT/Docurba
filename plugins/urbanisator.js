import Vue from 'vue'
import { groupBy, uniq } from 'lodash'
import axios from 'axios'

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
    async getCommuneProcedures (inseeCode) {
      const { data: perimetre } = await $supabase.from('procedures_perimetres')
        .select('*')
        .eq('collectivite_code', inseeCode)
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

      const { data: collectivites } = await axios({
        url: '/api/geo/collectivites',
        params: { codes: uniq(perimetre.map(p => p.collectivite_code)) }
      })

      procedures.forEach((procedure) => {
        // This is to manage legacy structure
        procedure.current_perimetre = perimetre.filter(p => p.procedure_id === procedure.id)
        procedure.current_perimetre.forEach((c) => {
          const commune = collectivites.find(com => com.code === c.collectivite_code)

          c.inseeCode = c.collectivite_code
          c.name = commune.intitule
        })

        // update status
        if (procedure.status === 'opposable') {
          const isOpposable = !!procedure.current_perimetre.find(p => p.opposable)
          if (!isOpposable) {
            procedure.status = 'precedent'
          }
        }
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
          return +$dayjs(b.created_at) - +$dayjs(a.created_at)
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
