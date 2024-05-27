import departements from '../miscs/referentiels/departements.json' assert {type: 'json'}
import axios from 'axios'

import { createClient } from '@supabase/supabase-js'

async function updatePerimeterStatus(config){
  const supabase = createClient(config.url, config.admin_key)

  await supabase.from('procedures_perimetres').update({
    opposable: false
  }).eq('opposable', true).eq('collectivite_type', 'COM')

  let curentRequest = 0

  async function getDepartement() {
    const deptCode = departements[curentRequest].code
    curentRequest += 1

    console.log(`${curentRequest}/${departements.length}`)

    try {
      const {data: communes} = await axios(`http://localhost:3000/api/urba/departements/${deptCode}`)

      const {data: perimetre} = await supabase.from('procedures_perimetres')
        .select('*').match({
        departement: deptCode,
        collectivite_type: 'COM'
      })

      const opposablePerimetre = []

      communes.forEach(commune => {
        const plan = commune.planOpposable
        const scot = commune.scotOpposable

        // console.log('plan opposable', plan?.id)

        if(plan) {
          const perimPlan = perimetre.find(p => {
            return p.procedure_id === plan.id && p.collectivite_code === commune.code
          })

          // console.log('perim', perimPlan?.id)

          if(perimPlan) {
            opposablePerimetre.push(Object.assign(perimPlan, {
              opposable: true
            }))
          }
        }

        if(scot) {
          const perimScot = perimetre.find(p => {
            return p.procedure_id === scot.id && p.collectivite_code === commune.code
          })

          if(perimScot) {
            opposablePerimetre.push(Object.assign(perimScot, {
              opposable: true
            }))
          }
        }
      })

      console.log(deptCode, 'perim oposable', opposablePerimetre.length)

      const {data, error} = await supabase.from('procedures_perimetres')
        .upsert(opposablePerimetre)

    } catch (err) {
      console.log('error on dept', deptCode)
    }

    if(departements[curentRequest]) {
      getDepartement()
    }
  }

  getDepartement()
  getDepartement()
  getDepartement()
  getDepartement()
  getDepartement()
}

export { updatePerimeterStatus }
