import axios from 'axios'

export default ({ route, store, $supabase }, inject) => {
  inject('urbanisator', {
    isEpci (collectiviteId) {
      return collectiviteId.toString().length > 5
    },
    async getCurrentCollectivite (collectiviteId) {
      try {
        const { data: collectivite } = await axios({
          url: `/api/${this.isEpci(collectiviteId) ? 'epci' : 'communes'}/${collectiviteId}`,
          method: 'get'
        })
        collectivite.name = this.isEpci(collectiviteId) ? collectivite.label : collectivite.nom_commune
        collectivite.type = this.isEpci(collectiviteId) ? 'epci' : 'commune'
        return collectivite
      } catch (error) {
        console.log('Error getCurrentCollectivite: ', error)
      }
    }
  })
}
