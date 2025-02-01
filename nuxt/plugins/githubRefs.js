import Vue from 'vue'
import departements from '@/assets/data/departements-france.json'
import regions from '@/assets/data/Regions.json'

export default () => {
  Vue.filter('githubRef', function (ref) {
    if (ref.includes('dept-')) {
      const deptCode = ref.replace('dept-', '')
      const dept = departements.find((d) => {
        if (deptCode.includes('A') || deptCode.includes('B')) {
          return d.code_departement === deptCode
        } else {
          return d.code_departement === +deptCode
        }
      })

      return dept.nom_departement
    }

    if (ref.includes('region-')) {
      const regionCode = ref.replace('region-', '')
      const region = regions.find(r => r.code === regionCode)

      return region.name
    }

    return ref
  })

  Vue.filter('deptToRef', function (deptCode) {
    if (deptCode?.includes('A') || deptCode?.includes('B')) {
      return deptCode
    } else {
      return +deptCode
    }
  })

  Vue.filter('deptNumberToString', function (deptCode) {
    if (deptCode) {
      const codeString = deptCode.toString()
      return (codeString.length < 2 ? '0' : '') + codeString
    } else { return deptCode }
  })

  Vue.filter('headRef', function (gitRef, project) {
    if (gitRef.startsWith('projet-')) {
      return `dept-${window.$nuxt.$options.filters.deptToRef(project.trame)}`
    }

    if (gitRef.startsWith('dept-')) {
      const deptCode = gitRef.replace('dept-', '')
      // eslint-disable-next-line eqeqeq
      const regionCode = departements.find(d => d.code_departement == deptCode).code_region
      return `region-${regionCode}`
    }

    return 'main'
  })

  Vue.filter('allHeadRefs', function (gitRef, project) {
    const refs = [gitRef]

    while (refs.at(-1) !== 'main') {
      refs.push(window.$nuxt.$options.filters.headRef(refs.at(-1), project))
    }

    return refs
  })
}
