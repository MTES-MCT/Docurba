// interface Procedure {
//   approvalDate: string | null
//   comment: string | null
//   creationDate: string | null
//   documentType: string
//   id: string
//   lastEvent: Event | null
//   lastStructuralEvent: Event | null
//   lastUpdateDate: string | null
//   name: string | null
//   nameDetails: string | null
//   number: string | null
//   parentId: string | null
//   prescriptionDate: string | null
//   privateComment: string | null
//   procedures: Omit<Procedure, 'procedures'>[]
//   startedBeforeHuwartLaw: boolean
//   status: string
//   sudocuhComment: string | null
//   sudocuhId: string | null
//   territorialAuthority: TerritorialAuthority | null
//   topicDetails: string | null
//   topics: string[]
//   towns: TerritorialAuthority[]
//   type: string
// }
// interface Event {
//   date: string
//   id: string
//   type: string
// }

import { maxBy, orderBy, groupBy, chunk, keyBy, uniq } from 'lodash'
import { addFormattedDate, getApprovalEvent, getPrescriptionEvent, getStopEvent, getEventImpact } from '@/plugins/event'

export default ({ $djangoApi, $supabase, $dayjs, $territorialAuthorityApi }, inject) => {
  async function computeProcedureStatus (procedure) {
    const { data: events } = await $supabase.from('doc_frise_events')
      .select('id, type')
      .eq('procedure_id', procedure.id)
      .is('archived_at', null)
      .or('is_valid.eq.true, type.eq.Abandon')
      .order('date_iso', { ascending: false })
      .order('type')

    for (const event of events) {
      const impact = getEventImpact(event.type, procedure.doc_type)
      if (impact) {
        return impact
      }
    }

    return 'en cours'
  }

  async function fetchCommunesProcedures (inseeCodes) {
    const { data: procedures } = await $supabase
      .from('procedures')
      .select('*, procedures_perimetres!inner ()')
      .eq('is_principale', true)
      .neq('doc_type', 'SD')
      .in('status', ['opposable', 'en cours'])
      .in('procedures_perimetres.collectivite_code', inseeCodes)
      .throwOnError()

    const proceduresIds = procedures.map(p => p.id)

    const { data: perimetres } = await $supabase
      .from('procedures_perimetres')
      .select()
      .in('procedure_id', proceduresIds)
      .throwOnError()

    const perimetresByProcedureId = groupBy(perimetres, 'procedure_id')

    const { data: events } = await $supabase
      .from('doc_frise_events')
      .select()
      .is('archived_at', null)
      .in('procedure_id', proceduresIds)
      .throwOnError()

    const eventsByProcedureId = groupBy(
      orderBy(events, e => $dayjs(e.date_iso), 'desc'),
      'procedure_id'
    )

    procedures.forEach((p) => {
      p.events = eventsByProcedureId[p.id] || [] // left join doc_frise_events e on e.procedure_id = procedure.id
      p.procedures_perimetres = perimetresByProcedureId[p.id] || [] // left join procedures_perimetres pp on pp.procedure_id = procedure.id
    })

    return procedures
  }

  function sortByApprobationEvent (procedures) {
    return procedures.sort((a, b) => {
      const dateA = a.approbation ? +$dayjs(a.approbation.date_iso) : 0
      const dateB = b.approbation ? +$dayjs(b.approbation.date_iso) : 0

      return dateB - dateA
    })
  }

  async function updatePerimetreOpposability (communes, procedures) {
    // Mark all procedures for communes as not opposable
    const communesByType = groupBy(communes, 'type')
    for (const [collectivityType, communesOfType] of Object.entries(communesByType)) {
      await $supabase
        .from('procedures_perimetres')
        .update({ opposable: false })
        .eq('opposable', true)
        .eq('collectivite_type', collectivityType)
        .in(
          'collectivite_code',
          communesOfType.map(c => c.code)
        )
        .throwOnError()
    }

    // Recompute opposability
    const updatesToPerform = []
    for (const commune of communes) {
      const communeProcedures = procedures.filter(p =>
        p.procedures_perimetres.some(c =>
          c.collectivite_code === commune.code && c.collectivite_type === commune.type
        )
      )

      const plan = sortByApprobationEvent(communeProcedures.filter(p => p.doc_type !== 'SCOT' && p.status === 'opposable'))[0]
      const scot = sortByApprobationEvent(communeProcedures.filter(p => p.doc_type === 'SCOT' && p.status === 'opposable'))[0]

      const proceduresOpposableForThisCommune = []
      if (plan) {
        proceduresOpposableForThisCommune.push(plan.id)
      }
      if (scot) {
        proceduresOpposableForThisCommune.push(scot.id)
      }

      if (proceduresOpposableForThisCommune.length) {
        updatesToPerform.push({
          collectivite_code: commune.code,
          collectivite_type: commune.type,
          procedure_ids: proceduresOpposableForThisCommune
        })
      }
    }

    // Update opposability, 30 at a time
    for (const [, chunkedUpdates] of chunk(updatesToPerform, 30).entries()) {
      const promisedUpdates = chunkedUpdates.map(
        // eslint-disable-next-line
        ({ collectivite_code, collectivite_type, procedure_ids }) => {
          return $supabase
            .from('procedures_perimetres')
            .update({ opposable: true })
            .match({ collectivite_code, collectivite_type })
            .in('procedure_id', procedure_ids)
            .throwOnError()
        }
      )
      await Promise.all(promisedUpdates)
    }
  }

  inject('procedure', {
    async updateOpposability (procedureId) {
      const APPROBATION_EVENT_TYPES = ["Délibération d'approbation", "Arrêté d'abrogation", "Arrêté du Maire ou du Préfet ou de l'EPCI", 'Approbation du préfet', "Délibération d'approbation du conseil municipal ou communautaire"]

      const { data: procedurePerim } = await $supabase
        .from('procedures_perimetres')
        .select('*')
        .eq('procedure_id', procedureId)
        .throwOnError()

      if (!procedurePerim.length) {
        return
      }

      let procedures = await fetchCommunesProcedures(
        procedurePerim.map(c => c.collectivite_code)
      )
      procedures = procedures.filter(p => !p.archived) // why at this step and not in fetchCommunesProcedures ?

      procedures = procedures.map(p => ({
        ...p,
        approbation: p.events.find(e => APPROBATION_EVENT_TYPES.includes(e.type)),
        communesPerimetres: p.procedures_perimetres.filter(c => c.collectivite_type === 'COM')
      }))

      const communes = procedurePerim.map(p => ({ code: p.collectivite_code, type: p.collectivite_type }))

      await updatePerimetreOpposability(communes, procedures)
    },
    async updateStatus (procedure) {
      const newStatus = await computeProcedureStatus(procedure)
      await $supabase.from('procedures').update({ status: newStatus }).eq('id', procedure.id)
    }
  })

  inject('procedureApi', {
    async listForTerritorialAuthorities (territorialAuthorityCodes) {
      const [{ data: rawProcedures }, eventTypes] = await Promise.all([
        $supabase.rpc('procedures_by_collectivites', { codes: territorialAuthorityCodes }),
        $djangoApi.get('/api-internes/types-evenement/')
      ])
      const eventStructuringByType = {}

      for (const eventType of eventTypes) {
        eventStructuringByType[eventType.name] = eventType.isStructuring
      }

      const territorialAuthorities = await $territorialAuthorityApi.list({
        codes: uniq(rawProcedures.flatMap(rawProcedure => [
          ..._getProcedurePerimeter(rawProcedure).map(p => p.collectivite_code),
          rawProcedure.collectivite_porteuse_id
        ]))
      })

      return _parseProcedures(rawProcedures, { eventStructuringByType, territorialAuthorities })
    }
  })
}

export function displayProcedure (procedure) {
  const copiedKeys = [
    'topics',
    'towns'
  ]
  const dateKeys = [
    'approvalDate',
    'creationDate',
    'lastUpdateDate',
    'prescriptionDate'
  ]
  const skippedKeys = [
    'lastEvent',
    'lastStructuringEvent',
    'startedBeforeHuwartLaw',
    'territorialAuthority',
    'towns',
    'type'
  ]
  const keys = Object.keys(procedure)
  const displayedProcedureBase = {}

  for (const key of keys) {
    if (copiedKeys.includes(key)) {
      displayedProcedureBase[key] = procedure[key]

      continue
    }
    if (dateKeys.includes(key)) {
      displayedProcedureBase[key] = procedure[key]?.split('T')[0].split('-').reverse().join('/') ?? ''

      continue
    }
    if (skippedKeys.includes(key)) {
      continue
    }

    displayedProcedureBase[key] = procedure[key] ?? ''
  }

  const displayedProcedure = {
    ...displayedProcedureBase,
    lastEventDate: procedure.lastEvent?.date?.split('T')[0].split('-').reverse().join('/') ?? '',
    lastEventId: procedure.lastEvent?.id ?? '',
    lastEventType: procedure.lastEvent?.type ?? '',
    lastStructuringEventDate: procedure.lastStructuringEvent?.date?.split('T')[0].split('-').reverse().join('/') ?? '',
    lastStructuringEventId: procedure.lastStructuringEvent?.id ?? '',
    lastStructuringEventType: procedure.lastStructuringEvent?.type ?? '',
    startedBeforeHuwartLaw: procedure.startedBeforeHuwartLaw ? 'Oui' : 'Non',
    territorialAuthorityCode: procedure.territorialAuthority?.code ?? '',
    territorialAuthorityName: procedure.territorialAuthority?.name ?? '',
    townName: procedure.towns[0]?.name ?? '',
    towns: procedure.towns.map(({ code, name }) => ({
      code: code ?? '',
      name: name ?? ''
    })),
    type: `${procedure.type}${
      ['Élaboration', 'Modification', 'Révision'].includes(procedure.type) &&
      procedure.startedBeforeHuwartLaw
        ? ' (antérieure à la loi Huwart)'
        : ''
    }`
  }

  return 'procedures' in procedure
    ? {
        ...displayedProcedure,
        procedures: procedure.procedures.map(displayProcedure)
      }
    : displayedProcedure
}

export function enrichProcedureWithEvents (procedure) {
  const events = procedure?.doc_frise_events

  // This filter is necessary here because the rpc 'procedures_by_collectivites' don't filter out archived events
  // and will be removed when using internal_apis/events
  const activeEvents = events?.filter(event => !event.archived_at)

  if (!activeEvents) {
    return procedure
  }

  const now = new Date()
  const lastEvent = maxBy(
    // Remove future events
    activeEvents.filter(event => new Date(event.date_iso) <= now),
    'date_iso'
  )
  let approvalEvent, prescriptionEvent, stopEvent

  for (const event of orderBy(activeEvents, 'date_iso', 'desc')) {
    const eventWithFormattedDate = addFormattedDate(event)

    if (!approvalEvent && getApprovalEvent(event)) {
      approvalEvent = eventWithFormattedDate
    }
    if (!prescriptionEvent && getPrescriptionEvent(event)) {
      prescriptionEvent = eventWithFormattedDate
    }
    if (!stopEvent && getStopEvent(event)) {
      stopEvent = eventWithFormattedDate
    }
    if (approvalEvent && prescriptionEvent && stopEvent) {
      break
    }
  }

  return {
    ...procedure,
    approval_event: approvalEvent,
    last_event: lastEvent,
    prescription_event: prescriptionEvent,
    stop_event: stopEvent
  }
}

export function getProcedureTypeLabel (procedure) {
  return procedure
    ? `${procedure.type}${
      [
        'Elaboration',
        'Modification',
        'Révision'
      ].includes(procedure.type) && procedure.started_before_huwart_law
        ? ' (antérieure à la loi Huwart)'
        : ''
    }`
    : ''
}

function _getProcedureDocumentType (rawProcedure) {
  return `${
    rawProcedure.doc_type === 'SCOT'
      ? 'SCoT'
      : rawProcedure.doc_type
  }${
    rawProcedure.is_pluih && !rawProcedure.doc_type.includes('H')
      ? 'H'
      : ''
  }`
}

function _getProcedureName (rawProcedure, { territorialAuthority }) {
  const suffix = (
    rawProcedure.name_complement &&
    !rawProcedure.name?.endsWith(rawProcedure.name_complement)
  )
    ? ` - ${rawProcedure.name_complement}`
    : ''

  if (rawProcedure.name) {
    return `${rawProcedure.name}${suffix}`
  }

  const parts = [
    _parseProcedureType(rawProcedure.type),
    rawProcedure.numero,
    _getProcedureDocumentType(rawProcedure),
    territorialAuthority?.name
  ].filter(Boolean)

  return `${parts.join(' ')}${suffix}`
}

function _getProcedurePerimeter (rawProcedure) {
  if (rawProcedure.procedures_perimetres.length === 2) {
    const comdPerimeter = rawProcedure.procedures_perimetres
      .filter(p => p.collectivite_type === 'COMD')

    if (comdPerimeter.length === 1) {
      return comdPerimeter || []
    }
  }

  return rawProcedure.procedures_perimetres || []
}

function _getProcedureStatus (rawProcedure, { territorialAuthority }) {
  switch (rawProcedure.status) {
    case 'abandon':
      return 'Abandonné'
    case 'abrogé':
      return 'Abrogé'
    case 'annulé':
      return 'Annulé'
    case 'approuvé':
      return 'Approuvé'
    case 'caduc':
      return 'Caduc'
    case 'en cours':
      return 'En cours'
    case 'en projet':
      return 'En projet'
    case 'opposable':
      return _getProcedurePerimeter(rawProcedure).some(
        territorialAuthority?.code
          ? p => p.opposable && (
            p.collectivite_code === territorialAuthority.code ||
            p.collectivite_type === 'COMD'
          )
          : ({ opposable }) => opposable
      )
        ? 'Opposable'
        : 'Précédent'
    default:
      return null
  }
}

function _getProcedureTerritorialAuthorityCode (rawProcedure) {
  const perimeter = _getProcedurePerimeter(rawProcedure)

  return (
    perimeter.length === 1
      ? perimeter[0].collectivite_code
      : rawProcedure.collectivite_porteuse_id
  ) || null
}

function _getProcedureTowns (rawProcedure, { territorialAuthorities }) {
  const perimeter = _getProcedurePerimeter(rawProcedure)
  const territorialAuthoritiesByCode = keyBy(territorialAuthorities, 'code')
  const towns = []

  for (const p of perimeter) {
    const town = territorialAuthoritiesByCode[p.collectivite_code]

    if (town) {
      towns.push(town)
    }
  }

  return towns
}

function _parseProcedure (rawProcedure, { eventStructuringByType, territorialAuthorities }) {
  // This filter is necessary here because the rpc 'procedures_by_collectivites' don't filter out archived events
  // and will be removed when using internal_apis/events
  const activeEvents = orderBy(
    rawProcedure.doc_frise_events?.filter(e => !e.archived_at) ?? [],
    'date_iso',
    'desc'
  )
  const now = new Date()
  const lastEvent = activeEvents.find(event =>
    new Date(event.date_iso) <= now
  ) ?? null
  const lastStructuringEvent = activeEvents.find(event =>
    eventStructuringByType[event.type] &&
    new Date(event.date_iso) <= now
  ) ?? null
  const territorialAuthorityCode = _getProcedureTerritorialAuthorityCode(rawProcedure)
  const territorialAuthority = territorialAuthorityCode
    ? territorialAuthorities.find(({ code }) => code === territorialAuthorityCode)
    : null
  let approvalDate = null
  let prescriptionDate = null

  for (const event of activeEvents) {
    if (!approvalDate && getApprovalEvent(event)) {
      approvalDate = event.date_iso
    }
    if (!prescriptionDate && getPrescriptionEvent(event)) {
      prescriptionDate = event.date_iso
    }
    if (approvalDate && prescriptionDate) {
      break
    }
  }

  return {
    approvalDate,
    comment: rawProcedure.commentaire || null,
    creationDate: rawProcedure.created_at?.split('T')[0] || null,
    documentType: _getProcedureDocumentType(rawProcedure),
    id: rawProcedure.id,
    lastEvent: lastEvent && {
      date: lastEvent.date_iso,
      id: lastEvent.id,
      type: lastEvent.type
    },
    lastStructuringEvent: lastStructuringEvent && {
      date: lastStructuringEvent.date_iso,
      id: lastStructuringEvent.id,
      type: lastStructuringEvent.type
    },
    lastUpdateDate: rawProcedure.last_updated_at?.split('T')[0] || null,
    name: _getProcedureName(rawProcedure, { territorialAuthority }),
    nameDetails: _parseProcedureNameDetails(rawProcedure.name_complement),
    number: rawProcedure.numero || null,
    parentId: rawProcedure.procedure_id || null,
    prescriptionDate,
    privateComment: rawProcedure.comment_dgd || null,
    startedBeforeHuwartLaw: !!rawProcedure.started_before_huwart_law,
    status: _getProcedureStatus(rawProcedure, { territorialAuthority }),
    sudocuhComment: rawProcedure.comment_from_sudocuh || null,
    sudocuhId: rawProcedure.from_sudocuh || null,
    territorialAuthority,
    topicDetails: rawProcedure.topics__other__comment || null,
    topics: rawProcedure.topics ?? [],
    towns: _getProcedureTowns(rawProcedure, { territorialAuthorities }),
    type: _parseProcedureType(rawProcedure.type)
  }
}

function _parseProcedureNameDetails (rawNameDetails) {
  return rawNameDetails
    ? /^\(.*\)$/.test(rawNameDetails)
      ? rawNameDetails.slice(1, -1)
      : rawNameDetails
    : null
}

function _parseProcedureType (rawType) {
  return rawType === 'Elaboration' ? 'Élaboration' : rawType
}

function _parseProcedures (rawProcedures, { eventStructuringByType, territorialAuthorities }) {
  const procedures = []
  const procedureIndexById = {}

  for (const rawProcedure of rawProcedures) {
    const procedure = _parseProcedure(rawProcedure, {
      eventStructuringByType,
      territorialAuthorities
    })

    if (rawProcedure.secondary_procedure_of) {
      if (rawProcedure.secondary_procedure_of in procedureIndexById) {
        procedures[
          procedureIndexById[
            rawProcedure.secondary_procedure_of
          ]
        ].procedures.push(procedure)
      } else {
        procedureIndexById[rawProcedure.secondary_procedure_of] = procedures.length
        procedures.push({ procedures: [procedure] })
      }
    } else if (procedureIndexById[procedure.id]) {
      procedures[procedureIndexById[procedure.id]] = {
        ...procedure,
        procedures: procedures[procedureIndexById[procedure.id]].procedures
      }
    } else {
      procedureIndexById[procedure.id] = procedures.length
      procedures.push({
        ...procedure,
        procedures: []
      })
    }
  }

  return orderBy(
    procedures
      .filter(procedure => 'id' in procedure)
      .map(procedure => ({
        ...procedure,
        procedures: orderBy(
          procedure.procedures,
          [
            ({ prescriptionDate }) => prescriptionDate || '0000-00-00',
            ({ lastUpdateDate }) => lastUpdateDate || '0000-00-00',
            ({ approvalDate }) => approvalDate || '0000-00-00'
          ],
          ['desc', 'desc', 'desc']
        )
      })),
    [
      ({ status }) => {
        switch (status) {
          case 'En cours':
            return 1
          case 'Opposable':
            return 2
          default:
            return 3
        }
      },
      ({ prescriptionDate }) => prescriptionDate || '0000-00-00',
      ({ lastUpdateDate }) => lastUpdateDate || '0000-00-00',
      ({ approvalDate }) => approvalDate || '0000-00-00'
    ],
    ['asc', 'desc', 'desc', 'desc']
  )
}
