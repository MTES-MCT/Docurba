import { maxBy, orderBy, groupBy, chunk } from 'lodash'
import { addFormattedDate, getApprovalEvent, getPrescriptionEvent, getStopEvent, getEventImpact } from '@/plugins/event'

export default ({ $supabase, $dayjs }, inject) => {
  async function computeProcedureStatus (procedure) {
    const { data: events } = await $supabase.from('doc_frise_events')
      .select('id, type')
      .eq('procedure_id', procedure.id)
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
}

export function enrichProcedureWithEvents (procedure) {
  const events = procedure?.doc_frise_events

  if (!events) {
    return procedure
  }

  const now = new Date()
  const lastEvent = maxBy(
    // Remove future events
    events.filter(event => new Date(event.date_iso) <= now),
    'date_iso'
  )
  let approvalEvent, prescriptionEvent, stopEvent

  for (const event of orderBy(events, 'date_iso', 'desc')) {
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
