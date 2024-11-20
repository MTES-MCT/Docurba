import departements from '../miscs/referentiels/departements.json' assert { type: 'json' };
import axios from 'axios';
import { createClient } from '@supabase/supabase-js';

async function updatePerimeterStatus(config) {
  const supabase = createClient(config.url, config.admin_key);

  // This should be useless, the API is in charge of properly setting status.
  // Also, this can create rollback error if this steps does not finish properly.
  // await supabase.from('procedures_perimetres').update({
  //   opposable: false
  // }).eq('opposable', true).eq('collectivite_type', 'COM');

  let currentRequest = 0;

  async function getDepartement() {
    if (currentRequest >= departements.length) {
      return;
    }

    const deptCode = departements[currentRequest].code;
    currentRequest += 1;

    console.log(`${currentRequest}/${departements.length}`);

    // The logic here was replaced by an API call to avoid having to maintain 2 ways of updating perimetres.
    // I've tested departements individualy but not in batch. So this might need some monitoring when we run the daily dump.
    await axios(`https://nuxt3.docurba.incubateur.net/api/urba/procedures/perimetres/update?departementCode=${deptCode}`);

    return getDepartement();
  }

  const concurrentRequests = 5;
  const promises = Array(concurrentRequests).fill().map(() => getDepartement());

  await Promise.all(promises);
}

export { updatePerimeterStatus };
