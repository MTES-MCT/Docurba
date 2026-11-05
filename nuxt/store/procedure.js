import { keyBy, orderBy } from 'lodash'
import { isMunicipalityInseeCode } from '~/store/territorialAuthority'

// interface Procedure {
//   approvalDate: string | null
//   comment: string | null
//   creationDate: string | null
//   docType: string
//   id: string
//   lastEvent: ProcedureEvent | null
//   lastStructuringEvent: ProcedureEvent | null
//   lastUpdateDate: string | null
//   name: string | null
//   nameDetails: string | null
//   number: string | null
//   parentId: string | null
//   prescriptionDate: string | null
//   privateComment: string | null
//   procedureIds: string[]
//   startedBeforeHuwartLaw: boolean
//   status: ProcedureStatus | null
//   sudocuhComment: string | null
//   sudocuhId: string | null
//   territorialAuthorityCode: string | null
//   topicDetails: string | null
//   topics: string[]
//   townCodes: string[]
//   type: string
// }
// interface ProcedureEvent {
//   date: string
//   id: string
//   typeId: string
// }
// enum ProcedureStatus {
//   Abandoned = 'abandoned',
//   Approved = 'approved',
//   Canceled = 'canceled',
//   InPlanning = 'in-planning',
//   InProgress = 'in-progress',
//   Obsolete = 'obsolete',
//   Opposable = 'opposable',
//   Previous = 'previous',
//   Repealed = 'repealed',
// }

export const ProcedureStatus = {
  Abandoned: 'abandoned',
  Approved: 'approved',
  Canceled: 'canceled',
  InPlanning: 'in-planning',
  InProgress: 'in-progress',
  Obsolete: 'obsolete',
  Opposable: 'opposable',
  Previous: 'previous',
  Repealed: 'repealed',
}

export const state = () => ({
  idsByDepartmentCode: {},
  idsByTerritorialAuthorityCode: {},
  procedureById: {},
})

export const getters = {}

export const mutations = {
  setProcedures(state, procedures) {
    state.procedureById = {
      ...state.procedureById,
      ...keyBy(procedures, 'id'),
    }
  },
  setDepartmentIds(state, { departmentCode, ids }) {
    state.idsByDepartmentCode = {
      ...state.idsByDepartmentCode,
      [departmentCode]: ids,
    }
  },
  setTerritorialAuthorityIds(state, { ids, territorialAuthorityCode }) {
    state.idsByTerritorialAuthorityCode = {
      ...state.idsByTerritorialAuthorityCode,
      [territorialAuthorityCode]: ids,
    }
  },
}

export const actions = {
  async get({ dispatch }, { id, ...params }) {
    const list = await dispatch('list', {
      ...params,
      ids: [id],
    })

    return list.length ? list[0] : null
  },
  async list({ commit, rootGetters, state }, params) {
    const apiParams = _toApiProcedureParams(params)

    if (
      params.departmentCode
      && params.departmentCode in state.idsByDepartmentCode
    ) {
      return state.idsByDepartmentCode[params.departmentCode]
        .map((id) => state.procedureById[id])
    }
    if (params.ids && params.ids.every((id) => id in state.procedureById)) {
      return sortProcedures(params.ids.map((id) => state.procedureById[id]))
    }
    if (
      params.territorialAuthorityCode
      && params.territorialAuthorityCode in state.idsByTerritorialAuthorityCode
    ) {
      return state.idsByTerritorialAuthorityCode[params.territorialAuthorityCode]
        .map((id) => state.procedureById[id])
    }
    if (
      params.territorialAuthorityCodes
      && params.territorialAuthorityCodes.every((code) =>
        code in state.idsByTerritorialAuthorityCode,
      )
    ) {
      return Object.fromEntries(params.territorialAuthorityCodes.map((code) => [
        code,
        state.idsByTerritorialAuthorityCode[code].map((id) => state.procedureById[id]),
      ]))
    }
    if (params.ids) {
      apiParams.ids = apiParams.ids.filter((id) => !(id in state.procedureById))
    }
    if (params.territorialAuthorityCodes) {
      if ('collectivites_porteuses' in apiParams) {
        apiParams.collectivites_porteuses = apiParams.collectivites_porteuses.filter((code) =>
          !(code in state.idsByTerritorialAuthorityCode)
        )
      }
      if ('communes_perimetre' in apiParams) {
        apiParams.communes_perimetre = apiParams.communes_perimetre.filter((code) =>
          !(code in state.idsByTerritorialAuthorityCode)
        )
      }
    }

    const procedures = _fromApiProcedures(
      await rootGetters['api/get']('/api-internes/procedures/', apiParams),
      params,
    )
    commit('setProcedures', procedures)

    if (params.departmentCode) {
      commit('setDepartmentIds', {
        departmentCode: params.departmentCode,
        ids: procedures.map(({ id }) => id),
      })

      return procedures
    }
    if (params.ids) {
      return sortProcedures(params.ids.map((id) => state.procedureById[id]))
    }
    if (params.territorialAuthorityCode) {
      commit('setTerritorialAuthorityIds', {
        ids: procedures.map(({ id }) => id),
        territorialAuthorityCode: params.territorialAuthorityCode,
      })

      return procedures
    }
    if (params.territorialAuthorityCodes) {
      const proceduresByTerritorialAuthorityCode = {}
      const territorialAuthorityCodeProcedureIdPairs = {}

      procedures.forEach((procedure) => {
        (
          procedure.territorialAuthorityCode
            ? [procedure.territorialAuthorityCode, ...procedure.townCodes]
            : procedure.townCodes
        ).forEach((code) => {
          const pair = [code, procedure.id].join()

          if (territorialAuthorityCodeProcedureIdPairs[pair]) return

          territorialAuthorityCodeProcedureIdPairs[pair] = true

          if (code in proceduresByTerritorialAuthorityCode) {
           proceduresByTerritorialAuthorityCode[code].push(procedure)
          } else {
           proceduresByTerritorialAuthorityCode[code] = [procedure]
          }
        })
      })

      params.territorialAuthorityCodes.forEach((code) => {
        if (
          code in state.idsByTerritorialAuthorityCode
          || !(code in proceduresByTerritorialAuthorityCode)
        ) return

        commit('setTerritorialAuthorityIds', {
          ids: sortProcedures(proceduresByTerritorialAuthorityCode[code])
            .map(({ id }) => id),
          territorialAuthorityCode: code,
        })
      })

      return Object.fromEntries(params.territorialAuthorityCodes.map((code) => [
        code,
        code in state.idsByTerritorialAuthorityCode
          ? state.idsByTerritorialAuthorityCode[code].map((id) =>
            state.procedureById[id],
          )
          : [],
      ]))
    }

    return []
  },
}

export function displayProcedureStatus(status) {
  switch (status) {
    case ProcedureStatus.Abandoned:
      return 'Abandonné'
    case ProcedureStatus.Approved:
      return 'Approuvé'
    case ProcedureStatus.Canceled:
      return 'Annulé'
    case ProcedureStatus.InPlanning:
      return 'En projet'
    case ProcedureStatus.InProgress:
      return 'En cours'
    case ProcedureStatus.Obsolete:
      return 'Caduc'
    case ProcedureStatus.Opposable:
      return 'Opposable'
    case ProcedureStatus.Previous:
      return 'Précédent'
    case ProcedureStatus.Repealed:
      return 'Abrogé'
    default:
      return ''
  }
}

export function sortProcedures(procedures) {
  return orderBy(procedures, [
    ({ type }) => type === 'SCoT' ? 2 : 1,
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
    ({ approvalDate }) => approvalDate || '0000-00-00',
  ], ['asc', 'asc', 'desc', 'desc', 'desc'])
}

// TODO :: Parse all fields
function _fromApiProcedure(apiProcedure, params) {
  return {
    approvalDate: apiProcedure.approval_date || null,
    // comment: apiProcedure.commentaire || null,
    // creationDate: apiProcedure.created_at
    //   ? apiProcedure.created_at.split('T')[0]
    //   : null,
    departmentCode: params.departmentCode,
    docType: apiProcedure.docType === 'SCOT' ? 'SCoT' : apiProcedure.docType,
    id: apiProcedure.id,
    // lastEvent: null,
    // lastStructuringEvent: null,
    // lastUpdateDate: apiProcedure.last_updated_at
    //   ? apiProcedure.last_updated_at.split('T')[0]
    //   : null,
    name: apiProcedure.name || null,
    // nameDetails: apiProcedure.name_complement
    //   ? /^\(.*\)$/.test(apiProcedure.name_complement)
    //     ? apiProcedure.name_complement.slice(1, -1)
    //     : apiProcedure.name_complement
    //   : null,
    number: apiProcedure.numero || null,
    parentId: apiProcedure.parentId || null,
    // prescriptionDate: null,
    // privateComment: apiProcedure.comment_dgd || null,
    // procedureIds: [],
    startedBeforeHuwartLaw: !!apiProcedure.startedBeforeHuwartLaw,
    status: _fromApiProcedureStatus(apiProcedure),
    // sudocuhComment: apiProcedure.comment_from_sudocuh || null,
    // sudocuhId: apiProcedure.from_sudocuh || null,
    territorialAuthorityCode: _fromApiProcedureTerritorialAuthorityCode(apiProcedure),
    // topicDetails: apiProcedure.topics__other__comment || null,
    topics: apiProcedure.topics
      ? apiProcedure.topics.map(({ name }) => name)
      : [],
    townCodes: _fromApiProcedurePerimeter(apiProcedure).map(({ code }) => code),
    type: apiProcedure.type === 'Elaboration'
      ? 'Élaboration'
      : apiProcedure.type,
  }
}

function _fromApiProcedurePerimeter(apiProcedure) {
  if (apiProcedure.perimetre.length === 2) {
    const comdPerimeter = apiProcedure.perimetre
      .filter((p) => p.type === 'COMD')

    if (comdPerimeter.length === 1) {
      return comdPerimeter
    }
  }

  return apiProcedure.perimetre
}

function _fromApiProcedureStatus(apiProcedure) {
  switch (apiProcedure.status) {
    case 'abandon':
      return ProcedureStatus.Abandoned
    case 'abroge':
      return ProcedureStatus.Repealed
    case 'annule':
      return ProcedureStatus.Canceled
    case 'approuve':
      return ProcedureStatus.Approved
    case 'caduc':
      return ProcedureStatus.Obsolete
    case 'en cours':
      return ProcedureStatus.InProgress
    case 'en projet':
      return ProcedureStatus.InPlanning
    case 'opposable': {
      const perimeter = _fromApiProcedurePerimeter(apiProcedure)
      const code = (
        perimeter.length === 1
          ? perimeter[0].code
          : apiProcedure.collectivite_porteuse
            ? apiProcedure.collectivite_porteuse.siren
            : null
      ) || null

      return perimeter.some(
        isMunicipalityInseeCode(code)
          ? (p) => p.is_opposable === 'True' && (
            p.code === code || p.type === 'COMD'
          )
          : ({ is_opposable }) => is_opposable === 'True'
      )
        ? ProcedureStatus.Opposable
        : ProcedureStatus.Previous
    }
    default:
      return null
  }
}

function _fromApiProcedureTerritorialAuthorityCode(apiProcedure) {
  const perimeter = _fromApiProcedurePerimeter(apiProcedure)

  return perimeter.length === 1
    ? perimeter[0].code || null
    : apiProcedure.collectivite_porteuse
      ? apiProcedure.collectivite_porteuse.siren || null
      : null
}

function _fromApiProcedures(apiProcedures, params) {
  return sortProcedures(
    apiProcedures.map((apiProcedure) =>
      _fromApiProcedure(apiProcedure, params)
    )
  )
}

// TODO :: Improve this
function _toApiProcedureParams(params) {
  const apiParams = {}

  if (params.ids) {
    apiParams.ids = params.ids
  }
  if (params.territorialAuthorityCode) {
    apiParams[
      isMunicipalityInseeCode(params.territorialAuthorityCode)
        ? 'communes_perimetre'
        : 'collectivites_porteuses'
    ] = params.territorialAuthorityCode
  }
  if (params.territorialAuthorityCodes) {
    const inseeCodes = []
    const sirenCodes = []

    params.territorialAuthorityCodes.forEach((code) => {
      (isMunicipalityInseeCode(code) ? inseeCodes : sirenCodes).push(code)
    })

    if (inseeCodes.length) {
      apiParams.communes_perimetre = inseeCodes
    }
    if (sirenCodes.length) {
      apiParams.collectivites_porteuses = sirenCodes
    }
  }

  return apiParams
}
