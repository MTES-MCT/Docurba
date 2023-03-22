import Vue from 'vue'
import departements from '@/assets/data/departements-france.json'
import regions from '@/assets/data/Regions.json'

export default () => {
  Vue.filter('githubRef', function (ref) {
    if (ref.includes('dept-')) {
      const deptCode = ref.replace('dept-', '')
      const dept = departements.find(d => d.code_departement === +deptCode)

      return dept.nom_departement
    }

    if (ref.includes('region-')) {
      const regionCode = ref.replace('region-', '')
      const region = regions.find(r => r.code === regionCode)

      return region.name
    }

    return ref
  })
}
