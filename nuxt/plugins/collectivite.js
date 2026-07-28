export default ({ $djangoApi }, inject) => {
  inject('collectiviteApi', {
    get (id, params) {
      return getCollectivite($djangoApi, id, params)
    },
    list (params) {
      return listCollectivites($djangoApi, params)
    }
  })
}

export async function getCollectivite (api, id, params) {
  return parseCollectivite(await api.get(`/api-internes/collectivites/${id}/`, params))
}

export async function listCollectivites (api, params) {
  if (!params.codes_siren || params.codes_siren.length < 100) {
    return (await api.get('/api-internes/collectivites/', params)).map(parseCollectivite)
  }

  const collectivitesQueries = []

  for (let i = 0; i < params.codes_siren.length; i += 100) {
    collectivitesQueries.push(api.get('/api-internes/collectivites/', {
      ...params,
      codes_siren: params.codes_siren.slice(i, i + 100)
    }))
  }

  return (await Promise.all(collectivitesQueries))
    .flatMap(c => c.map(parseCollectivite))
    .sort((a, b) => {
      const aCode = Number(a.code)
      const bCode = Number(b.code)

      return aCode === bCode ? 0 : aCode > bCode ? 1 : -1
    })
}

function parseCollectivite (collectivite) {
  return {
    ...collectivite,
    code: collectivite.codeInsee || collectivite.siren
  }
}
