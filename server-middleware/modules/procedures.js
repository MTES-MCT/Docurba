import { uniq } from 'lodash'
import dayjs from 'dayjs'
import communes from '../Data/referentiels/communes.json'
import groupements from '../Data/referentiels/groupements.json'
import regions from '../Data/INSEE/regions.json'
import departements from '../Data/INSEE/departements.json'
import supabase from './supabase.js'

import sudocuhCodes from './sudocuhCodes.js'

const eventsCategs = {
  approbation: ["Délibération d'approbation", "Arrêté d'abrogation", "Arrêté du Maire ou du Préfet ou de l'EPCI", 'Approbation du préfet'],
  arret: ['Arrêt de projet'],
  pac: ['Porter à connaissance'],
  pacComp: ['Porter à connaissance complémentaire'],
  prescription: ['Prescription', "Delibération de l'établissement public", 'Publication de périmetre'],
  exec: ['Caractère exécutoire']
}

// const eventsTypes = Object.keys(eventsCategs).flatMap(key => eventsCategs[key])

const proceduresCategs = {
  revision: ['Révision', 'Révision allégée (ou RMS)', 'Révision simplifiée'],
  modification: ['Modification', 'Modification simplifiée']
}

function sortEvents (events) {
  return events.sort((a, b) => {
    return +dayjs(a.date_iso) - +dayjs(b.date_iso)
  })
}

function sortProceduresByEvenCateg (procedures, eventCateg) {
  return procedures.sort((a, b) => {
    const dateA = a[eventCateg] ? +dayjs(a[eventCateg].date_iso) : 0
    const dateB = b[eventCateg] ? +dayjs(b[eventCateg].date_iso) : 0

    return dateA - dateB
  })
}

// This assume that events are sorted in chronological order
function findEventByType (events, types) {
  return events.find(e => types.includes(e.type))
}

function filterProcedures (procedures) {
  const sortedProcedures = sortProceduresByEvenCateg(procedures)

  let opposables = sortedProcedures.filter(p => p.status === 'opposable')
  opposables = sortProceduresByEvenCateg(opposables, 'approbation')

  let currents = sortedProcedures.filter(p => p.status === 'en cours')
  currents = sortProceduresByEvenCateg(currents, 'prescription')

  return { procedures: sortedProcedures, opposables, currents }
}

module.exports = {
  getCommuneMetadata (inseeCode) {
    const commune = communes.find(c => c.code === inseeCode && c.type === 'COM')
    const communeDepartement = departements.find(d => d.code === commune.departementCode)
    const communeRegion = regions.find(r => r.code === commune.regionCode)

    let intercommunalite = groupements.find(i => i.code === commune.intercommunaliteCode)
    if (intercommunalite) {
      intercommunalite = Object.assign({
        region: regions.find(r => r.code === intercommunalite.regionCode),
        departement: departements.find(d => d.code === intercommunalite.departementCode)
      }, intercommunalite)
    }

    return Object.assign({
      intercommunalite,
      departement: communeDepartement,
      region: communeRegion
    }, commune)
  },
  async fetchProcedures (inseeCodes) {
    const { data: procedures, error } = await supabase
      .rpc('procedures_by_insee_codes', {
        codes: inseeCodes
      })

    if (error) {
      console.log('fetchProcedures error', error)
    }

    return procedures
  },
  async fetchEvents (procedures) {
    const { data: events } = await supabase
      .rpc('events_by_procedures_ids', {
        procedures_ids: procedures.map(p => p.id)
      })

    return events.map((e) => {
      return Object.assign(e, {
        year: dayjs(e.date_iso).format('YYYY')
      })
    })
  },
  async getCommuneProcedures (inseeCode, procedures, events) {
    if (!procedures) {
      procedures = await this.fetchProcedures([inseeCode])
    }

    if (!events) {
      events = await this.fetchEvents(procedures)
    }

    return procedures.map((procedure) => {
      const procedureEvents = events.filter(e => e.procedure_id === procedure.id)

      const eventsByType = {}

      Object.keys(eventsCategs).forEach((key) => {
        eventsByType[key] = findEventByType(procedureEvents, eventsCategs[key])
      })

      if (eventsByType.prescription && eventsByType.approbation) {
        eventsByType.approbationDelay = dayjs(eventsByType.approbation.date_iso).diff(eventsByType.prescription.date_iso, 'day')
      }

      return Object.assign({
        events: sortEvents(procedureEvents),
        isSelfPorteuse: procedure.collectivite_porteuse_id === inseeCode
      }, eventsByType, procedure)
    })
  },
  async getCommune (inseeCode, rawProcedures, events) {
    const commune = this.getCommuneMetadata(inseeCode)

    let procedures = await this.getCommuneProcedures(inseeCode, rawProcedures, events)
    procedures = sortProceduresByEvenCateg(procedures, 'prescription')

    const {
      procedures: scots,
      opposables: scotOpposables,
      currents: scotCurrents
    } = filterProcedures(procedures.filter(p => p.doc_type === 'SCOT'))

    const scotOpposable = scotOpposables[0]
    const scotCurrent = scotCurrents[0]

    const {
      procedures: plans,
      opposables: planOpposables,
      currents: planCurrents
    } = filterProcedures(procedures.filter(p => p.doc_type !== 'SCOT'))

    const revisions = planCurrents.filter(p => proceduresCategs.revision.includes(p.type))
    const modifications = planCurrents.filter(p => proceduresCategs.modification.includes(p.type))

    const planOpposable = planOpposables[0]
    const planCurrent = planCurrents[0]

    const collectivitePorteuse = (planCurrent || planOpposable)?.collectivite_porteuse_id || inseeCode

    const sCodes = sudocuhCodes.getAllCodes(planOpposable, planCurrent, collectivitePorteuse)

    const currentsDocTypes = uniq(planCurrents.map(p => p.doc_type)).join(', ')

    return Object.assign({
      scots,
      scotOpposables,
      scotOpposable,
      scotCurrents,
      scotCurrent,
      plans,
      planOpposables,
      planOpposable,
      planCurrents,
      planCurrent,
      revisions,
      modifications,
      collectivitePorteuse,
      sudocuhCodes: sCodes,
      currentsDocTypes
    }, commune)
  },
  async getCommunes (inseeCodes) {
    const procedures = await this.fetchProcedures(inseeCodes)
    console.log('getCommunes', inseeCodes[0], procedures ? procedures.length : 'no procedures')

    const events = await this.fetchEvents(procedures)

    const communes = inseeCodes.map((inseeCode) => {
      const communeProcedures = procedures.filter((p) => {
        return !!p.current_perimetre.find(c => c.inseeCode === inseeCode)
      })

      const communeEvents = events.filter((e) => {
        return !!communeProcedures.find(p => p.id === e.procedure_id)
      })

      return this.getCommune(inseeCode, communeProcedures, communeEvents)
    })

    return await Promise.all(communes)
  }
}