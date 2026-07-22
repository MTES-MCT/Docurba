export default ({ $djangoApi }, inject) => {
  inject('collectiviteApi', {
    async get (id, params) {
      return parseCollectivite(await $djangoApi.get(`/collectivites/${id}/`, params))
    },
    async list (params) {
      return (await $djangoApi.get('/collectivites/', params)).map(parseCollectivite)
    }
  })
}

function parseCollectivite (collectivite) {
  return {
    ...collectivite,
    code: collectivite.codeInsee || collectivite.siren
  }
}
