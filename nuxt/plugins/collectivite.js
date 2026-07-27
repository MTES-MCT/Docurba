export default ({ $djangoApi }, inject) => {
  inject('collectiviteApi', {
    get (codeInseeOrSiren, params) {
      return getCollectivite($djangoApi, codeInseeOrSiren, params)
    },
    list (params) {
      return listCollectivites($djangoApi, params)
    }
  })
}

export async function getCollectivite (api, codeInseeOrSiren, params) {
  return parseCollectivite(await api.get(`/api-internes/collectivites/${codeInseeOrSiren}/`, params))
}

export async function listCollectivites (api, params) {
  return (await api.get('/api-internes/collectivites/', params)).map(parseCollectivite)
}

function parseCollectivite (collectivite) {
  return {
    ...collectivite,
    code: collectivite.codeInsee || collectivite.siren
  }
}
