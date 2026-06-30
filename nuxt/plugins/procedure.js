import { maxBy, orderBy } from 'lodash'
import { addFormattedDate, getApprovalEvent, getPrescriptionEvent, getStopEvent } from '@/plugins/event'

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
