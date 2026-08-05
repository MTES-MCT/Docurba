
export default ({ $djangoApi }, inject) => {
  const eventsTypesByDocumentType = {}

  async function getEventTypesByDocumentType (documentType) {
    if (!(documentType in eventsTypesByDocumentType)) {
      eventsTypesByDocumentType[documentType] = (await $djangoApi.get('/api-internes/types-evenement/', {
        document_type: documentType
      })).map((eventType, index) => ({
        ...eventType,
        order: index + 1,
        structurant: eventType.isStructuring
      }))
    }

    return eventsTypesByDocumentType[documentType]
  }

  inject('procedureEvent', {
    getTypes (documentType) {
      if (!documentType) {
        return []
      }
      if (documentType.match(/i|H|M/)) {
        return getEventTypesByDocumentType('PLU')
      }
      switch (documentType) {
        case 'PLU':
        case 'POS':
          return getEventTypesByDocumentType('PLU')
        case 'SCOT':
        case 'SD':
          return getEventTypesByDocumentType('SCOT')
        case 'CC':
          return getEventTypesByDocumentType('CC')
        default:
          return []
      }
    }
  })
}

export function addFormattedDate (event) {
  return event && event.date_iso && !event.date_iso_formattee
    ? {
        ...event,
        date_iso_formattee: event.date_iso.split('-').reverse().join('/')
      }
    : event
}

export function getApprovalEvent (event) {
  return !!event.is_valid && [
    'Approbation du préfet',
    'Arrêté de mise à jour',
    'Arrêté du Maire ou du Préfet ou de l\'EPCI',
    'Déclaration d\'intérêt général',
    'Délibération d\'approbation',
    'Délibération d\'approbation du conseil municipal ou communautaire',
    'DUP emportant mise en compatibilité'
  ].includes(event.type)
}

export function getLaunchEvent (eventType) {
  return [
    'Arrêté de lancement de la procédure',
    'Délibération de l\'Etablissement Public',
    'Délibération de l\'établissement public qui prescrit',
    'Délibération de prescription du conseil métropolitain',
    'Délibération de prescription du conseil municipal',
    'Délibération de prescription du conseil municipal ou communautaire',
    'Prescription'
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
      return `pp${
        procedure.current_perimetre.length > 1 && procedure.doc_type !== 'CC' ? 'i' : ''
      }${
        procedure.started_before_huwart_law ? '' : 'lh'
      }`
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

export function getStopEvent (event) {
  return !!event.is_valid && [
    'Arrêt de projet',
    'Délibération du conseil communautaire qui arrête le projet de PLU',
    'Délibération qui arrête le projet de SCoT'
  ].includes(event.type)
}

export function getEventImpact (eventType, documentType) {
  // This logic must evolve to reflects event_types table
  const IMPACTFUL_EVENTS = {
    CC: {
      'en cours': [
        'Délibération de prescription du conseil municipal'
      ],
      opposable: [
        'Approbation du préfet',
        'Caractère exécutoire',
        'Retrait de l\'annulation totale'
      ],
      abandon: [
        'Abandon',
        'Retrait de la délibération de prescription'
      ],
      annule: [
        'Annulation TA totale',
        'Annulation TA',
        'Abrogation effective'
      ],
      caduc: []
    },
    SCOT: {
      'en cours': [
        'Délibération de l\'établissement public qui prescrit',
        'Retrait de la délibération d\'approbation'
      ],
      opposable: [
        'Délibération d\'approbation',
        'Caractère exécutoire',
        'Retrait de l\'annulation totale'
      ],
      abandon: [
        'Abandon',
        'Retrait de la délibération de prescription'
      ],
      annule: [
        'Annulation TA totale',
        'Annulation TA'
      ],
      caduc: [
        'Caducité'
      ]
    },
    SD: {
      'en cours': [
        'Délibération de l\'établissement public qui prescrit'
      ],
      opposable: [
        'Délibération d\'approbation',
        'Caractère exécutoire'
      ],
      abandon: [
        'Abandon'
      ],
      annule: [
        'Annulation TA totale',
        'Annulation TA'
      ],
      caduc: [
        'Caducité'
      ]
    },
    PLU: {
      'en cours': [
        'Délibération de prescription du conseil municipal ou communautaire'
      ],
      opposable: [
        'Caractère exécutoire',
        'Retrait de l\'annulation totale',
        'Délibération d\'approbation du municipal ou communautaire',
        'Délibération d\'approbation du conseil municipal ou communautaire',
        'Délibération d\'approbation'
      ],
      abandon: [
        'Abandon',
        'Retrait de la délibération de prescription'
      ],
      annule: [
        'Annulation TA totale',
        'Annulation TA',
        'Abrogation',
        'Arrêté d\'abrogation'
      ],
      caduc: [
        'Caducité'
      ]
    },
    POS: {
      'en cours': [
        'Délibération de prescription du conseil municipal ou communautaire'
      ],
      opposable: [
        'Caractère exécutoire',
        'Délibération d\'approbation du municipal ou communautaire',
        'Délibération d\'approbation du conseil municipal ou communautaire',
        'Délibération d\'approbation'
      ],
      abandon: [
        'Abandon'
      ],
      annule: [
        'Annulation TA',
        'Annulation TA totale',
        'Caducité'
      ],
      caduc: []
    }
  }
  const IMPACTS = ['caduc', 'opposable', 'annule', 'en cours', 'abandon']

  const docType = documentType.startsWith('PLU') ? 'PLU' : documentType

  return IMPACTS.find(impact => IMPACTFUL_EVENTS[docType][impact].includes(eventType)) ?? null
}
