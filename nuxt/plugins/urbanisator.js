import Vue from 'vue'
import { groupBy, uniqBy, uniq, orderBy, maxBy } from 'lodash'
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
    async getCommuneProcedures (inseeCode) {
      const { data: perimetre } = await $supabase.from('procedures_perimetres').select('*').eq('collectivite_code', inseeCode)
      const { data: procedures } = await $supabase.from('procedures')
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
      const { data: procedures } = await $supabase.from('procedures')
        .select('*').eq('archived', false)
        .eq('collectivite_porteuse_id', collectiviteId)

      return procedures
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

        // Same as in the DB. Are the columns used?
        // current_perimetre is. See InsertForm.vue
        // initial_perimetre is not but is still referenced.
        procedure.current_perimetre = procedure.procedures_perimetres.filter(c => c.collectivite_type === 'COM').map((p) => {
          const commune = collectivites.find(com => com.code === p.collectivite_code)

          return Object.assign({
            inseeCode: p.collectivite_code,
            name: commune?.intitule || ''
          }, p, commune)
        })

        const comd = procedure.procedures_perimetres.find(p => p.collectivite_type === 'COMD')

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

      const { data: procedures } = await $supabase.rpc('procedures_by_collectivites', {
        codes: collectivites.filter(c => c.type === 'COM').map(c => c.code)
      })

      const filteredProcedures = procedures.filter((procedure) => {
        return !procedure.archived && procedure.type !== 'Abrogation'
      })

      return await this.getProceduresPerimetre(filteredProcedures, collectiviteId)
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
      // SELECT p.*, array_agg(pp.*) AS procedures_perimetres
      //   FROM procedures p
      //   JOIN procedures_perimetres pp ON p.id = pp.procedure_id
      //   WHERE p.id IN (
      //       SELECT procedure_id
      //       FROM procedures_perimetres
      //       WHERE collectivite_code IN (
      //           SELECT json_array_elements_text(codes)
      //       )
      //   ) GROUP BY p.id;
      // perimetre.*, procedures_perimetres[{id, created_at, added_at, collectivite_code, collectivite_type, procedure_id, opposable, departement, commune_id}]
      // commune_id == f"{collectivite_code}_{collectivite_type}"
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

        const schemas = proceduresPrincipales.filter(e => e.doc_type === 'SCOT' || e.doc_type === 'SD')
        // The specific ID here is to prevent a duplicated created by sudocuh. This is suposed to be temporary for a demo.
        const plans = proceduresPrincipales.filter(e => e.doc_type !== 'SCOT' && e.doc_type !== 'SD' && e.id !== '760d88f0-008d-4505-98f6-a7a9a2ebaf61')

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
