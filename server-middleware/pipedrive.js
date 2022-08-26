/* eslint-disable no-console */
const express = require('express')
const app = express()
app.use(express.json())

const pipedrive = require('./modules/pipedrive.js')

app.post('/contacted', async (req, res) => {
  const email = req.body.email
  const isGouv = email.indexOf('gouv.fr') > email.indexOf('@')

  // eslint-disable-next-line prefer-const
  let { person, deals } = await pipedrive.findPerson(email)

  if (!person) {
    person = await pipedrive.addPerson({
      email,
      firstname: '',
      lastname: ''
    })
  }

  if (deals && deals.lenth) {
    const deal = deals.find(d => d.stage_id === 10)

    pipedrive.updateDeal(deal.id, {
      stage_id: 11
    })
  } else {
    pipedrive.addDeal({
      title: `New User ${email}`,
      personId: person.id,
      // 11 is stageId for contacted in DDT pipeline
      // 7 is stageId contacted in Collectivity pipeline
      stageId: isGouv ? 11 : 7
    })
  }

  res.status(200).send('OK')
})

module.exports = app
