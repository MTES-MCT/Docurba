import { maxBy } from 'lodash'
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
  let approval, prescription, stop

  for (const event of events) {
    const eventWithFormattedDate = addFormattedDate(event)

    if (!approval && getApprovalEvent(event)) {
      approval = eventWithFormattedDate
    }
    if (!prescription && getPrescriptionEvent(event)) {
      prescription = eventWithFormattedDate
    }
    if (!stop && getStopEvent(event)) {
      stop = eventWithFormattedDate
    }
    if (approval && prescription && stop) {
      break
    }
  }

  return {
    ...procedure,
    approval,
    last_event: lastEvent,
    prescription,
    stop
  }
}
