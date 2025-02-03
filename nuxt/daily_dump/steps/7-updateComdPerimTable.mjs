import sudocuhApprouve from '../miscs/API_SUDOCUH_DU_approuve.json' assert {type: 'json'}
import sudocuhEncours from '../miscs/API_SUDOCUH_DU_encours.json' assert {type: 'json'}

import { createClient } from '@supabase/supabase-js'

async function updateComDPerimeter(config){
  const supabase = createClient(config.url, config.admin_key)

  await supabase.from('procedures_perimetres').delete().eq('collectivite_type', 'COMD')

  const COMDs = [...sudocuhApprouve, ...sudocuhEncours]

  COMDs.forEach(p => {
    p.from_sudocuh = p.App_IdProc ||  p.EnC_IdProc
  })

  const needInserts = []

  async function insertPerim (COMD) {
    const {data: procedures} = await supabase.from('procedures').select('*')
    .eq('from_sudocuh', COMD.from_sudocuh)

    const procedure = procedures[0]

    if(procedure) {
      const perim = {
        collectivite_code: COMD.Com_INSEE_CF,
        collectivite_type: 'COMD',
        procedure_id: procedure.id,
        opposable: procedure.status === 'opposable',
        departement: COMD.Com_Dep
      }

      // console.log('Need insert', perim.collectivite_code)

      await supabase.from('procedures_perimetres').insert([perim])

      needInserts.push(perim)
    } else {
      console.log('Procedure not found')
    }
  }

  // const  communeTest = COMDs.find(c => c.Com_INSEE_CF == '86245')
  // insertPerim(communeTest)

  for (let index = 0; index < COMDs.length; index++) {
    await insertPerim(COMDs[index])
  }

  console.log('Needed inserts', COMDs.length)
  console.log('NB inserts', needInserts.length)
}

export { updateComDPerimeter }
