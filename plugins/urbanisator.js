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
    async getProceduresPerimetre (procedures, collectiviteId) {
      const collectivitesCodes = [collectiviteId]
      procedures.forEach((p) => {
        collectivitesCodes.push(...p.procedures_perimetres.map(c => c.collectivite_code))
      })

      const { data: collectivites } = await axios({
        url: '/api/geo/collectivites',
        params: { codes: uniq(collectivitesCodes) }
      })

      procedures.forEach((procedure) => {
        procedure.procedures_perimetres = procedure.procedures_perimetres.map((p) => {
          const collectivite = collectivites.find(c => c.code === p.collectivite_code && c.type === p.collectivite_type)
          return Object.assign({}, collectivite, p)
        })

        procedure.current_perimetre = procedure.procedures_perimetres.filter(c => c.collectivite_type === 'COM').map((p) => {
          const commune = collectivites.find(com => com.code === p.collectivite_code)

          return Object.assign({
            inseeCode: p.collectivite_code,
            name: commune?.intitule || ''
          }, p, commune)
        })

        const comd = procedure.procedures_perimetres.find(p => p.type === 'COMD')

        // COMD specifique
        if (procedure.procedures_perimetres.length === 2 && comd) {
          procedure.procedures_perimetres = procedure.procedures_perimetres.filter((p) => {
            return p.collectivite_type === 'COMD'
          })
        }

        if (procedure.status === 'opposable') {
          let isOpposable = false

          if (collectiviteId.length > 5) {
            isOpposable = !!procedure.procedures_perimetres.find(p => p.opposable)
          } else {
            isOpposable = !!procedure.procedures_perimetres.find((p) => {
              return p.opposable && (p.collectivite_code === collectiviteId || p.collectivite_type === 'COMD')
            })
          }

          if (!isOpposable) {
            procedure.status = 'precedent'
          }
        }
      })

      return procedures
    },
    async getCollectiviteProcedures (collectiviteId) {
      const { data: collectivite } = await axios(`/api/geo/collectivites/${collectiviteId}`)
      const collectivites = [collectivite]
      if (collectivite.membres) { collectivites.push(...collectivite.membres) }

      const { data: procedures } = await $supabase
        .rpc('procedures_by_collectivites', {
          codes: collectivites.filter(c => c.type === 'COM').map(c => c.code)
        })

      return await this.getProceduresPerimetre(procedures.filter(p => !p.archived), collectiviteId)
    },
    async getProjects (collectiviteId) {
      try {
        const procedures = await this.getCollectiviteProcedures(collectiviteId)
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
        // console.log('urbanisator get projects', { schemas, plans })
        return { schemas, plans }
      } catch (error) {
        // eslint-disable-next-line no-console
        console.log('urbanisator error', error)
      }
    }
  })
}
