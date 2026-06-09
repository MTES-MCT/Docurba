
import CCEvents from '@/assets/data/events/CC_events.json'
import PLUEvents from '@/assets/data/events/PLU_events.json'
import SCoTEvents from '@/assets/data/events/SCOT_events.json'

export function getDocumentTypeEvents (documentType) {
  if (!documentType) {
    return []
  }
  if (documentType.match(/i|H|M/)) {
    return PLUEvents
  }
  switch (documentType) {
    case 'PLU':
    case 'POS':
      return PLUEvents
    case 'SCOT':
    case 'SD':
      return SCoTEvents
    case 'CC':
      return CCEvents
    default:
      return []
  }
}

export function getLaunchEvent (eventType) {
  return [
    'Arrêté de lancement de la procédure',
    'Délibération de l\'établissement public qui prescrit',
    'Délibération de prescription du conseil métropolitain',
    'Délibération de prescription du conseil municipal',
    'Délibération de prescription du conseil municipal ou communautaire'
  ].includes(eventType)
}

export function getPrescriptionEvent (event) {
  return !!event.is_valid && [
    'Délibération de l\'établissement public qui prescrit',
    'Délibération de l\'Etablissement Public',
    'Délibération de prescription du conseil métropolitain',
    'Délibération de prescription du conseil municipal ou communautaire',
    'Délibération de prescription du conseil municipal',
    'Prescription'
  ].includes(event.type)
}

export function getProcedureEventsScope (procedure) {
  if (!procedure) {
    return 'aucun'
  }
  switch (procedure.type) {
    case 'Elaboration':
    case 'Révision':
      return procedure.current_perimetre.length > 1 && procedure.doc_type !== 'CC' ? 'ppi' : 'pp'
    case 'Mise à jour':
      return 'mj'
    case 'Mise en compatibilité':
      return 'mc'
    case 'Modification':
      return procedure.started_before_huwart_law ? 'm' : 'mlh'
    case 'Modification simplifiée':
      return 'ms'
    case 'Révision allégée (ou RMS)':
    case 'Révision à modalité simplifiée ou Révision allégée':
      return 'rms'
    default:
      return 'aucun'
  }
}
