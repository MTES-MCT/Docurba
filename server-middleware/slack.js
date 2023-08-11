const express = require('express')
const app = express()
const { createClient } = require('@supabase/supabase-js')

const supabase = createClient('https://ixxbyuandbmplfnqtxyw.supabase.co', process.env.SUPABASE_ADMIN_KEY)

app.use(express.json())
app.use(express.urlencoded({ extended: true }))

const axios = require('axios')
const sendgrid = require('./modules/sendgrid.js')

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

  const dynamic_template_data = {
    collectiviteName: userData.label ?? userData.name,
    collectiviteId: userData.EPCI ?? userData.collectivite_id,
    docs: userData.attachements
  }
  console.log("'Notify team in slack userData: ", userData, ' dynamic_template_data: ', dynamic_template_data)

  sendgrid.sendEmail(
    {
      to: userData.email,
      template_id: 'd-ff4df2141eda4723800cae1f0a63982c',
      dynamic_template_data: {
        collectiviteName: userData.collectivite.label ?? userData.collectivite.name,
        collectiviteId: userData.collectivite.EPCI ?? userData.collectivite.collectivite_id,
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

async function collectiviteValidation (data, responseUrl) {
  try {
    console.log('collectiviteValidation data: ', data)
    const { error: errorUpdateProfile } = await supabase.from('profiles').update({ verified: true }).eq('id', data.id)
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
      const { error: errorUpdateProfile } = await supabase.from('profiles').update({ verified: true }).eq('id', userData.id)
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
