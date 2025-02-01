/* eslint-disable no-console */
const supabase = require('./supabase.js')

module.exports = {
  count () {
    return supabase.from('sido').select('collectivite_code', { count: 'exact', head: true })
  },
  async countDocuments (query) {
    try {
      const { count } = await this.count().match(query)
      return count
    } catch (err) {
      console.log('Error in sido module count', err)
      return 0
    }
  },
  async getCollectivitiesDocumentsType () {
    const { data: collectivites } = await supabase.from('sido').select('collectivite_code, type_du_opposable, is_sectoriel_opposable, is_intercommunal_opposable')
      .eq('collectivite_type', 'Commune')

    return collectivites.map((collectivite) => {
      const isEPCI = collectivite.is_intercommunal_opposable ? 'i' : ''
      const isSectoriel = collectivite.is_sectoriel_opposable ? 'S' : ''

      return {
        docType: collectivite.type_du_opposable + isEPCI + isSectoriel,
        code: collectivite.collectivite_code
      }
    })
  }
}
