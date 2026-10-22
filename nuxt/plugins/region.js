// interface Region {
//   code: string
//   iso: string
//   name: string
// }
import regions from '~/assets/data/Regions.json'

export default (_, inject) => {
  inject('regionApi', {
    get (code) {
      return new Promise((resolve) => {
        resolve(regions.find(region => region.code === code) ?? null)
      })
    },
    list () {
      return new Promise((resolve) => {
        resolve(regions)
      })
    }
  })
}
