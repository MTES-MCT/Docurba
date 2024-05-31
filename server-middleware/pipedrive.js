/* eslint-disable no-console */
const express = require('express')
const app = express()
app.use(express.json())

const supabase = require('./modules/supabase.js')
const pipedrive = require('./modules/pipedrive.js')

app.post('/collectivite_inscrite', async (req, res) => {
  console.log('-- COLLECTIVITE INSCRITE PIPEDRIVE --')
  const userData = req.body.userData
  await pipedrive.movePersonDealTo(userData.email, pipedrive.COLLECTIVITE_DEAL.TRY_INSCRIPTION, pipedrive.COLLECTIVITE_DEAL.INSCRIT)
  res.status(200).send('OK')
})

app.post('/depot_acte', async (req, res) => {
  console.log('-- DEPOT D\'ACTE COLLECTIVITE PIPEDRIVE --')

  const userData = req.body.userData

  const { person } = await pipedrive.findPerson(userData.email)

  if (!person) {
    const deal = {
      title: `Nouvel utilisateur inconnu: ${userData.email} - ${userData.collectivite.label} (${userData.collectivite.region.iso})`
    }
    const { data } = await pipedrive.addDeal({ ...deal, stageId: pipedrive.COLLECTIVITE_DEAL.DEPOT_ACTE })
  } else {
    const personDeals = await pipedrive.getPersonDeals(person.id)
    const dealIdToUpdate = personDeals.filter(e => e.stage_id === pipedrive.COLLECTIVITE_DEAL.INSCRIT)[0]?.id
    const { data } = await pipedrive.updateDeal(dealIdToUpdate, { stage_id: pipedrive.COLLECTIVITE_DEAL.DEPOT_ACTE })
  }
  res.send({ success: true })
})

app.post('/contacted', async (req, res) => {
  const email = req.body.email
  const isGouv = email.indexOf('gouv.fr') > email.indexOf('@')

  try {
  // eslint-disable-next-line prefer-const
    let { person, deals } = await pipedrive.findPerson(email)

    if (!person) {
      person = await pipedrive.addPerson({
        email,
        firstname: 'New',
        lastname: 'User'
      })
    }

    console.log('Contacted Person', person)

    if (deals && deals.lenth) {
      const deal = deals.find(d => d.stage_id === 10)

      console.log('Updated Deal', deal)

      pipedrive.updateDeal(deal.id, {
        stage_id: 11
      })
    } else {
      const deal = await pipedrive.addDeal({
        title: `New User ${email}`,
        personId: person.id,
        // 11 is stageId for contacted in DDT pipeline
        // 7 is stageId contacted in Collectivity pipeline
        stageId: isGouv ? 11 : 7
      })

      console.log('Created Deal', deal)
    }
  } catch (err) {
    console.log('Error on contacted service', err)
  }

  res.status(200).send('OK')
})

app.post('/deals', async (req, res) => {
  const project = req.body.record
  const ownerId = project.owner

  const { data: owner, error } = await supabase.auth.admin.getUserById(ownerId)

  console.log(owner)

  if (!error) {
    const email = owner.user.email

    let { person } = await pipedrive.findPerson(email)

    if (!person) {
      person = await pipedrive.addPerson({
        email,
        firstname: 'New',
        lastname: 'User'
      })
    }

    try {
      const deal = await pipedrive.addDeal({
        title: `Nouvelle procedure: ${project.doc_type} - ${project.name}`,
        personId: person.id,
        // StageWithPipelineInfo
        //   id: 37,
        //   order_nr: 1,
        //   name: 'Intentions',
        //   active_flag: true,
        //   deal_probability: 100,
        //   pipeline_id: 7,
        //   rotten_flag: false,
        //   rotten_days: null,
        //   add_time: '2023-04-27 09:01:51',
        //   update_time: '2023-06-27 07:16:34',
        //   pipeline_name: 'Procédures',
        //   pipeline_deal_probability: false
        stageId: 37
      })

      console.log('Created Deal', deal)
      res.status(200).send(deal)
    } catch (err) {
      console.log('Err creating Deal', err)
      res.status(400).send(err)
    }
  }
})

// async function testPipedrive () {
//   const { person } = await pipedrive.findPerson('fabien@quantedsquare.com')
//   console.log(person)

//   const test = await pipedrive.updatePerson(person.id, {
//     verified: false,
//     other_poste: ["suivi_procedures", "redacteur_pac", "test"],
//     poste: 'ddt',
//     successfully_logged_once: false
//   })

//   console.log('testPipedrive ', test)
// }

// testPipedrive()

app.post('/profiles', async (req, res) => {
  const { record: profile } = req.body

  const { person } = await pipedrive.findPerson(profile.email)
  const update = await pipedrive.updatePerson(person.id, profile)

  if (update.success) {
    console.log('Person updated in pipedrive', profile.email)
    res.status(200).send('OK')
  } else {
    console.log('Error updating person', update)
    res.status(500).send(update)
  }
})

module.exports = app
