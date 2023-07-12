import axios from 'axios'
import regions from '@/assets/data/Regions.json'

export default ({ route, store, $supabase }, inject) => {
  inject('urbanisator', {
    isEpci (collectiviteId) {
      return collectiviteId.toString().length > 5
    },
    getRegionDetails (regionCode) {
      if (typeof regionCode === 'number') { regionCode = regionCode.toString() }
      return regions.find(e => e.code.toString().padStart(2, '0') === regionCode)
    },
    async getCurrentCollectivite (collectiviteId) {
      try {
        const { data: collectivite } = await axios({
          url: `/api/${this.isEpci(collectiviteId) ? 'epci' : 'communes'}/${collectiviteId}`,
          method: 'get'
        })

        const isEpci = this.isEpci(collectiviteId)
        collectivite.id = isEpci ? collectivite.EPCI : collectivite.code_commune_INSEE.toString().padStart(5, '0')
        collectivite.name = isEpci ? collectivite.label : collectivite.nom_commune
        collectivite.type = isEpci ? 'epci' : 'commune'
        const regionCode = isEpci ? collectivite.towns[0].code_region : collectivite.code_region
        collectivite.region = this.getRegionDetails(regionCode)
        return collectivite
      } catch (error) {
        console.log('Error getCurrentCollectivite: ', error)
      }
    }
  })
}
