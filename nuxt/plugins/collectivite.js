export default ({ $djangoApi }, inject) => {
  inject('collectiviteApi', {
    get (id, params) {
      return getCollectivite($djangoApi, id, params)
    },
    list (params) {
      return listCollectivites($djangoApi, params)
    },
    listFromCodes (codes, params) {
      return listCollectivitesFromCodes($djangoApi, codes, params)
    }
  })
}

export async function getCollectivite (api, id, params) {
  return parseCollectivite(await api.get(`/api-internes/collectivites/${id}/`, params))
}

export async function listCollectivites (api, params) {
  if (
    (!params.codes_insee || params.codes_insee.length < 100) &&
    (!params.codes_siren || params.codes_siren.length < 100)
  ) {
    return (await api.get('/api-internes/collectivites/', params)).map(parseCollectivite)
  }

  const collectivitesQueries = []

  if (params.codes_insee) {
    for (let i = 0; i < params.codes_insee.length; i += 100) {
      collectivitesQueries.push(api.get('/api-internes/collectivites/', {
        ...params,
        codes_insee: params.codes_insee.slice(i, i + 100)
      }))
    }
  }
  if (params.codes_siren) {
    for (let i = 0; i < params.codes_siren.length; i += 100) {
      collectivitesQueries.push(api.get('/api-internes/collectivites/', {
        ...params,
        codes_siren: params.codes_siren.slice(i, i + 100)
      }))
    }
  }

  return sortCollectivites((await Promise.all(collectivitesQueries)).flatMap(c => c.map(parseCollectivite)))
}

export async function listCollectivitesFromCodes (api, codes, params = {}) {
  const inseeCodes = []
  const sirenCodes = []
  const collectivitesQueries = []

  codes.forEach((code) => {
    (code.length > 5 ? sirenCodes : inseeCodes).push(code)
  })

  if (inseeCodes.length) {
    collectivitesQueries.push(listCollectivites(api, { ...params, codes_insee: inseeCodes }))
  }
  if (sirenCodes.length) {
    collectivitesQueries.push(listCollectivites(api, { ...params, codes_siren: sirenCodes }))
  }

  return sortCollectivites((await Promise.all(collectivitesQueries)).flat())
}

function parseCollectivite (collectivite) {
  return {
    ...collectivite,
    code: collectivite.codeInsee || collectivite.siren,
    membres: collectivite.membres?.map((el) => { return parseCollectivite(el) }),
    membres_niveaux_inferieurs: collectivite.membres_niveaux_inferieurs?.map((el) => { return parseCollectivite(el) }),
    groupements: collectivite.groupements?.map((el) => { return parseCollectivite(el) }),
    groupements_niveaux_superieurs: collectivite.groupements_niveaux_superieurs?.map((el) => { return parseCollectivite(el) })
  }
}

function sortCollectivites (collectivites) {
  return [...collectivites].sort((a, b) => {
    const aCode = Number(a.code)
    const bCode = Number(b.code)

    return aCode === bCode ? 0 : aCode > bCode ? 1 : -1
  })
}
