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
  return (await api.get('/api-internes/collectivites/', params)).map(parseCollectivite)
}

function parseCollectivite (collectivite) {
  return {
    ...collectivite,
    code: collectivite.codeInsee || collectivite.siren
  }
}
