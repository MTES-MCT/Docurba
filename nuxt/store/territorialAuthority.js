import { keyBy, orderBy } from 'lodash'

// interface TerritorialAuthority {
//   code: string
//   departmentCode: string
//   groups: TerritorialAuthority[]
//   groupsIncluded: boolean
//   higherGroups: TerritorialAuthority[]
//   higherGroupsIncluded: boolean
//   inseeCode: string
//   intermunicipalityCode: string
//   lowerMembers: TerritorialAuthority[]
//   lowerMembersIncluded: boolean
//   members: TerritorialAuthority[]
//   membersIncluded: boolean
//   name: string
//   regionCode: string
//   sirenCode: string
//   type: string
// }

export const state = () => ({
  codesByDepartmentCode: {},
  territorialAuthorityByCode: {},
})

export const getters = {
  exists(state) {
    return (params) => params.code in state.territorialAuthorityByCode && [
      ['includeGroups', 'groupsIncluded'],
      ['includeHigherGroups', 'higherGroupsIncluded'],
      ['includeLowerMembers', 'lowerMembersIncluded'],
      ['includeMembers', 'membersIncluded'],
    ].every(([paramsKey, stateKey]) =>
      !params[paramsKey]
      || state.territorialAuthorityByCode[params.code][stateKey]
    )
  },
}

export const mutations = {
  setCodes(state, { codes, departmentCode }) {
    state.codesByDepartmentCode = {
      ...state.codesByDepartmentCode,
      [departmentCode]: codes,
    }
  },
  setTerritorialAuthorities(state, territorialAuthorities) {
    state.territorialAuthorityByCode = {
      ...state.territorialAuthorityByCode,
      ...keyBy(territorialAuthorities.map((territorialAuthority) => {
        if (!(territorialAuthority.code in state.territorialAuthorityByCode)) {
          return territorialAuthority
        }

        const territorialAuthorityPatch = {
          ...state.territorialAuthorityByCode[territorialAuthority.code],
        }

        for (const key of [
          'groups',
          'higherGroups',
          'lowerMembers',
          'members',
        ]) {
          if (!territorialAuthority[`${key}Included`]) continue

          territorialAuthorityPatch[key] = territorialAuthority[key]
          territorialAuthorityPatch[`${key}Included`] = true
        }

        return territorialAuthorityPatch
      }), 'code'),
    }
  },
}

export const actions = {
  async get({ dispatch }, { code, ...params }) {
    const list = await dispatch('list', {
      ...params,
      codes: [code],
    })

    return list.length ? list[0] : null
  },
  async list({ commit, getters, rootGetters, state }, { codes, ...params }) {
    const apiParams = _toApiTerritorialAuthorityParams(params)

    if (codes) {
      if (codes.every((code) => getters.exists({ code, ...params }))) {
        return codes.map((code) => state.territorialAuthorityByCode[code])
      }

      const inseeCodes = []
      const queries = []
      const sirenCodes = []

      codes.forEach((code) => {
        if (getters.exists({ code, ...params })) return

        (isMunicipalityInseeCode(code) ? inseeCodes : sirenCodes).push(code)
      })

      if (inseeCodes.length) {
        queries.push(rootGetters['api/get']('/api-internes/collectivites/', {
          ...apiParams,
          codes_insee: inseeCodes,
        }))
      }
      if (sirenCodes.length) {
        queries.push(rootGetters['api/get']('/api-internes/collectivites/', {
          ...apiParams,
          codes_siren: sirenCodes,
        }))
      }

      commit('setTerritorialAuthorities', _fromApiTerritorialAuthorities(
        (await Promise.all(queries)).flat(),
        params,
      ))

      return codes.map((code) => state.territorialAuthorityByCode[code])
    }
    if (params.departmentCode) {
      if (state.codesByDepartmentCode[params.departmentCode]) {
        return state.codesByDepartmentCode[params.departmentCode]
          .map((code) => state.territorialAuthorityByCode[code])
      }

      const territorialAuthorities = _fromApiTerritorialAuthorities(
        await rootGetters['api/get']('/api-internes/collectivites/', apiParams),
        params,
      )

      commit('setTerritorialAuthorities', territorialAuthorities)

      if (params.departmentCode) {
        commit('setCodes', {
          codes: territorialAuthorities.map(({ code }) => code),
          departmentCode: params.departmentCode,
        })
      }

      return state.codesByDepartmentCode[params.departmentCode]
        .map((code) => state.territorialAuthorityByCode[code])
    }

    return []
  },
}

export function displayTerritorialAuthorityCode(territorialAuthority) {
  if (!territorialAuthority) {
    return ''
  }
  if (territorialAuthority.inseeCode) {
    return `Code INSEE ${territorialAuthority.inseeCode}`
  }

  const firstGroupSize = territorialAuthority.sirenCode.length % 3

  return `SIREN ${[
    territorialAuthority.sirenCode.slice(0, firstGroupSize),
    ...territorialAuthority.sirenCode.slice(firstGroupSize).match(/.{1,3}/g) ?? []
  ].join(' ')}`
}

export function isMunicipalityInseeCode(code) {
  return !!code && code.length === 5
}

export function sortTerritorialAuthorities(territorialAuthorities) {
  return orderBy(territorialAuthorities, ({ code }) => Number(code))
}

function _fromApiTerritorialAuthorities(apiTerritorialAuthorities, params) {
  return sortTerritorialAuthorities(
    apiTerritorialAuthorities.map((apiTerritorialAuthority) =>
      _fromApiTerritorialAuthority(apiTerritorialAuthority, params),
    ),
  )
}

function _fromApiTerritorialAuthority(apiTerritorialAuthority, params) {
  return {
    code: apiTerritorialAuthority.codeInsee || apiTerritorialAuthority.siren,
    departmentCode: apiTerritorialAuthority.departementCode,
    groups: apiTerritorialAuthority.groupements
      ? apiTerritorialAuthority.groupements.map((apiGroup) =>
        _fromApiTerritorialAuthority(apiGroup, params)
      )
      : [],
    groupsIncluded: !!params.includeGroups,
    higherGroups: apiTerritorialAuthority.groupements_niveaux_superieurs
      ? apiTerritorialAuthority.groupements_niveaux_superieurs.map((apiGroup) =>
        _fromApiTerritorialAuthority(apiGroup, params)
      )
      : [],
    higherGroupsIncluded: !!params.includeHigherGroups,
    inseeCode: apiTerritorialAuthority.codeInsee,
    intermunicipalityCode: apiTerritorialAuthority.intercommunaliteCode,
    lowerMembers: apiTerritorialAuthority.membres_niveaux_inferieurs
      ? apiTerritorialAuthority.membres_niveaux_inferieurs.map((apiMember) =>
        _fromApiTerritorialAuthority(apiMember, params)
      )
      : [],
    lowerMembersIncluded: !!params.includeLowerMembers,
    members: apiTerritorialAuthority.membres
      ? apiTerritorialAuthority.membres.map((apiMember) =>
        _fromApiTerritorialAuthority(apiMember, params)
      )
      : [],
    membersIncluded: !!params.includeMembers,
    name: apiTerritorialAuthority.intitule,
    regionCode: apiTerritorialAuthority.regionCode,
    sirenCode: apiTerritorialAuthority.siren,
    type: apiTerritorialAuthority.type,
  }
}

function _toApiTerritorialAuthorityParams(params) {
  return {
    avec_groupements: params.includeGroups,
    avec_groupements_niveaux_superieurs: params.includeHigherGroups,
    avec_membres: params.includeMembers,
    avec_membres_niveaux_inferieurs: params.includeLowerMembers,
    code_departement: params.departmentCode,
  }
}
