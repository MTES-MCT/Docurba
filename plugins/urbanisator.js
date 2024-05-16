import Vue from 'vue'
import { groupBy, uniqBy, mapValues, uniq, orderBy, maxBy } from 'lodash'
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
    async getProceduresByCommunes (departementCode) {
      // TODO: Update postgres to make order works
      // TODO: Optimise with index, selected fields, order and limit
      const { data } = await $supabase.from('procedures_perimetres')
        .select('*, procedures(*, doc_frise_events(*))')
        .eq('departement', departementCode)
        // .order('date_iso', { referencedTable: 'procedures.doc_frise_events', ascending: false })
      const groupedProceduresPerim = groupBy(data, e => e.collectivite_code)
      const planScotsSeparated = mapValues(groupedProceduresPerim, (e) => {
        const plans = e.filter(e => !e.procedures.is_scot)
        const scots = e.filter(e => e.procedures.is_scot)
        return { scots, plans }
      })
      return planScotsSeparated
    },
    async getProceduresForDept (departementCode, { minimal = false } = {}) {
      // TODO: Update postgres to make order works
      // TODO: Optimise with index, selected fields, order and limit
      // TODO: Essayer de faire le fetch depuis procedure et filter
      let select = '*, procedures(*, doc_frise_events(*))'
      if (minimal) {
        select = '*, procedures(*, doc_frise_events(*))'
      }
      const { data } = await $supabase.from('procedures_perimetres')
        .select(select)
        .eq('departement', departementCode)
      // .order('doc_frise_events(date_iso)', { ascending: false })
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
          let isOpposable = false

          if (collectiviteId.length > 5) {
            isOpposable = !!procedure.current_perimetre.find(p => p.opposable)
          } else {
            console.log(collectiviteId, procedure.current_perimetre[0])
            isOpposable = !!procedure.current_perimetre.find(p => p.opposable && p.collectivite_code === collectiviteId)
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

      const { data: perimetres } = await $supabase.from('procedures_perimetres')
        .select('*').in('collectivite_code', collectivites.filter(c => c.type === 'COM').map(c => c.code))

      const proceduresIds = uniq(perimetres.map(p => p.procedure_id))

      const { data: procedures } = await $supabase.from('procedures')
        .select('*').eq('archived', false)
        .in('id', proceduresIds)

      return await this.getProceduresPerimetre(procedures, collectiviteId)
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
        console.log('urbanisator get projects', { schemas, plans })
        return { schemas, plans }
      } catch (error) {
        // eslint-disable-next-line no-console
        console.log('urbanisator error', error)
      }
    }
  })
}
