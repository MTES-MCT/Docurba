import Vue from 'vue'
import axios from 'axios'
import { groupBy } from 'lodash'
import regions from '@/assets/data/Regions.json'

export default ({ route, store, $supabase, $user, $dayjs, $sudocu }, inject) => {
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
    async getCollectivite (code) {
      if (code.length > 5) {
        return (await axios({ url: `/api/geo/intercommunalites/${code}`, method: 'get' })).data
      } else {
        return (await axios({ url: `/api/geo/communes/${code}`, method: 'get' })).data
      }
    },
    async getCommuneProcedures (inseeCode) {
      const { data: perimetre } = await $supabase.from('procedures_perimetres').select('*').eq('collectivite_code', inseeCode)
      const { data: procedures } = await $supabase.from('procedures_duplicate')
        .select('*, projects(*)').eq('archived', false)
        .in('id', perimetre.map(p => p.procedure_id))

      return procedures
    },
    async getIntercoProcedures (collectiviteId) {
      const { data: procedures } = await $supabase.from('procedures_duplicate')
        .select('*, projects(*)').eq('archived', false)
        .eq('collectivite_porteuse_id', collectiviteId)

      return procedures
    },
    async getProceduresPerimetre (procedures) {
      const { data: perimetre } = await $supabase.from('procedures_perimetres').select('*')
        .in('procedure_id', procedures.map(p => p.id))

      procedures.forEach((procedure) => {
        // This is to manage legacy structure
        procedure.current_perimetre = perimetre.filter(p => p.procedure_id)
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
