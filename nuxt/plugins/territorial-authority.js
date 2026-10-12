// interface TerritorialAuthority {
//   code: string
//   departmentCode: string
//   groups: TerritorialAuthority[]
//   inseeCode: string
//   intermunicipalityCode: string
//   members: TerritorialAuthority[]
//   name: string
//   regionCode: string
//   sirenCode: string
//   type: string
// }

export default ({ $djangoApi }, inject) => {
  inject('territorialAuthorityApi', {
    get (code, params) {
      return getTerritorialAuthority($djangoApi, code, params)
    },
    list (params) {
      return listTerritorialAuthorities($djangoApi, params)
    }
  })
}

export function displaySirenCode (sirenCode) {
  if (!sirenCode) {
    return ''
  }

  const firstGroupSize = sirenCode.length % 3

  return [
    sirenCode.slice(0, firstGroupSize),
    ...sirenCode.slice(firstGroupSize).match(/.{1,3}/g) ?? []
  ].join(' ')
}

export async function getTerritorialAuthority (api, code, params) {
  const territorialAuthorities = await listTerritorialAuthorities(api, {
    codes: [code],
    ...params
  })

  return territorialAuthorities[0] ?? null
}

export async function listTerritorialAuthorities (api, params) {
  const apiParams = {}
  const inseeCodes = []
  const queries = []
  const sirenCodes = []

  if (params.codes) {
    params.codes.forEach((code) => {
      (code.length > 5 ? sirenCodes : inseeCodes).push(code)
    })
  }
  if (params.includeMembers) {
    apiParams.avec_membres = params.includeMembers
  }
  if (inseeCodes.length) {
    if (inseeCodes.length < 100) {
      queries.push(api.get('/api-internes/collectivites/', {
        ...apiParams,
        codes_insee: inseeCodes
      }))
    } else {
      for (let i = 0; i < inseeCodes.length; i += 100) {
        queries.push(api.get('/api-internes/collectivites/', {
          ...apiParams,
          codes_insee: inseeCodes.slice(i, i + 100)
        }))
      }
    }
  }
  if (sirenCodes.length) {
    if (sirenCodes.length < 100) {
      queries.push(api.get('/api-internes/collectivites/', {
        ...apiParams,
        codes_siren: sirenCodes
      }))
    } else {
      for (let i = 0; i < sirenCodes.length; i += 100) {
        queries.push(api.get('/api-internes/collectivites/', {
          ...apiParams,
          codes_siren: sirenCodes.slice(i, i + 100)
        }))
      }
    }
  }

  return _parseTerritorialAuthorities((await Promise.all(queries)).flat())
}

function _parseTerritorialAuthorities (rawTerritorialAuthorities) {
  return rawTerritorialAuthorities.map(_parseTerritorialAuthority).sort((a, b) => {
    const aCode = Number(a.code)
    const bCode = Number(b.code)

    return aCode === bCode ? 0 : aCode > bCode ? 1 : -1
  })
}

function _parseTerritorialAuthority (rawTerritorialAuthority) {
  return {
    code: rawTerritorialAuthority.codeInsee || rawTerritorialAuthority.siren,
    departmentCode: rawTerritorialAuthority.departementCode,
    groups: rawTerritorialAuthority.membres?.map(_parseTerritorialAuthority) ?? [],
    inseeCode: rawTerritorialAuthority.codeInsee,
    intermunicipalityCode: rawTerritorialAuthority.intercommunaliteCode,
    members: rawTerritorialAuthority.membres?.map(_parseTerritorialAuthority) ?? [],
    name: rawTerritorialAuthority.intitule,
    regionCode: rawTerritorialAuthority.regionCode,
    sirenCode: rawTerritorialAuthority.siren,
    type: rawTerritorialAuthority.type
  }
}
