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

function parseCollectivite (rawCollectivite) {
  const collectivite = {
    ...rawCollectivite,
    code: rawCollectivite.codeInsee || rawCollectivite.siren
  }

  if (collectivite.groupements) {
    collectivite.groupements = collectivite.groupements.map(parseCollectivite)
  }
  if (collectivite.membres) {
    collectivite.membres = collectivite.membres.map(parseCollectivite)
  }

  return collectivite
}
