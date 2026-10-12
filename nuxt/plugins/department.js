// interface Department {
//   code: string
//   name: string
//   regionCode: string
//   regionName: string
// }
import rawDepartments from '~/assets/data/departements-france.json'

export default (_, inject) => {
  const departments = rawDepartments.map(_parseDepartment)

  inject('departmentApi', {
    get (code) {
      return new Promise((resolve) => {
        resolve(departments.find(department => department.code === code) ?? null)
      })
    },
    list () {
      return new Promise((resolve) => {
        resolve(departments)
      })
    }
  })
}

function _parseDepartment (rawDepartment) {
  return {
    code: rawDepartment.code_departement.toString().padStart(2, '0'),
    name: rawDepartment.nom_departement,
    regionCode: rawDepartment.code_region.toString(),
    regionName: rawDepartment.nom_region
  }
}
