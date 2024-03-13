const axios = require('axios')
const express = require('express')
const app = express()

app.use(express.json())
app.use(express.urlencoded({ extended: true }))

const sendgrid = require('./modules/sendgrid.js')
const supabase = require('./modules/supabase.js')

// modules
const admin = require('./modules/admin.js')
const slack = require('./modules/slack.js')

app.post('/notify/admin/acte', (req, res) => {
  // eslint-disable-next-line no-console
  console.log('Notify team in slack')
  const { userData } = req.body

  // try {
  slack.requestDepotActe(userData).then((res) => {
    // eslint-disable-next-line no-console
    console.log('Slack then: ', res.data)
  }).catch((err) => {
    // eslint-disable-next-line no-console
    console.log('Slack catch', err.response.data)
  })

  console.log("'Notify team in slack userData: ", userData)

  // const { data: { firstname, lastname, departement, region } } = await supabase.from('profiles').select('firstname, lastname, departement, region')

  sendgrid.sendEmail(
    {
      to: userData.email,
      template_id: 'd-ff4df2141eda4723800cae1f0a63982c',
      dynamic_template_data: {
        collectiviteName: userData.collectivite.label ?? userData.collectivite.nom_commune,
        collectiviteId: userData.collectivite.EPCI ?? userData.collectivite.code_commune_INSEE,
        docs: userData.attachements
      }
    })

  res.status(200).send('OK')
})

app.post('/notify/admin', (req, res) => {
  // eslint-disable-next-line no-console
  console.log('Notify team in slack')
  const { userData } = req.body

  // try {
  slack.requestStateAgentAccess(userData).then((res) => {
    // eslint-disable-next-line no-console
    console.log('Slack then: ', res.data)
  }).catch((err) => {
    // eslint-disable-next-line no-console
    console.log('Slack catch', err.response.data)
  })
  // } catch (err) {
  //   console.log(err)
  // }

  res.status(200).send('OK')
})

app.post('/notify/frp', (req, res) => {
  slack.notifyFrpEvent(req.body).then((res) => {
    // eslint-disable-next-line no-console
    console.log('Slack then: ', res.data)
  }).catch((err) => {
    // eslint-disable-next-line no-console
    console.log('Slack catch', err.response.data)
  })
})

async function collectiviteValidation (data, responseUrl) {
  try {
    console.log('collectiviteValidation data: ', data)
    const { error: errorUpdateProfile } = await supabase.from('profiles').update({ verified: true }).eq('user_id', data.user_id)
    if (errorUpdateProfile) { throw errorUpdateProfile }
    axios({
      url: responseUrl,
      method: 'post',
      data: {
        text: `${data.firstname} ${data.lastname} (${data.email})
        pour la collectivité de code INSEE ${data.collectivite_id} est vérifier et validé.`
      }
    })
  } catch (error) {
    console.log(error)
  }
}

// Webhook  from slack
app.post('/webhook/interactivity', async (req, res) => {
  const payload = JSON.parse(req.body.payload)

  // eslint-disable-next-line no-console
  console.log('slack payload: ', payload)

  const responseUrl = payload.response_url

  if (payload.actions && payload.actions.length) {
    const action = payload.actions[0]

    // eslint-disable-next-line no-console
    console.log('slack action: ', action)
    const userData = JSON.parse(action.value)

    if (action.action_id === 'ddt_validation') {
      // eslint-disable-next-line no-console
      console.log('userData:', userData)

      const { data, error } = await admin.updateUserRole(userData, 'admin')
      const { error: errorUpdateProfile } = await supabase.from('profiles').update({ verified: true }).eq('user_id', userData.user_id)
      if (errorUpdateProfile) { throw errorUpdateProfile }
      if (data && !error) {
        res.status(200).send('OK')
        axios({
          url: responseUrl,
          method: 'post',
          data: {
            text: `Role DDT/DEAL validé pour ${userData.email}`
          }
        })
      } else {
        // eslint-disable-next-line no-console
        console.log('err updating role', error)
      }
    } else if (action.action_id === 'collectivite_validation') {
      console.log('collectivite_validation')
      collectiviteValidation(userData, responseUrl)
    }
  }
})

module.exports = app
