/* eslint-disable no-console */
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
const geo = require('./modules/geo.js')
const sharing = require('./modules/sharing.js')

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

app.post('/notify/frp_shared', async (req, res) => {
  try {
    // Send notification to Slack
    const slackRes = await slack.shareProcedure(req.body)
    console.log('Slack response:', slackRes.data)

    // Prepare email data
    const { to, from, procedure, title } = req.body
    const senderName = from.firstname && from.lastname
      ? `M(me) ${from.firstname} ${from.lastname}`
      : from.email

    const { data: existingEmails, error: emailError } = await supabase
      .from('profiles')
      .select('email')
      .in('email', to.emails)

    if (emailError) {
      console.error('Error fetching new emails:', emailError)
    }
    const existingEmailsSet = new Set(existingEmails.map(profile => profile.email))
    const emailsWithoutSender = to.emails.filter(email => from.email !== email)
    const emailPromises = emailsWithoutSender.map((email) => {
      const isNewEmail = !existingEmailsSet.has(email)

      const procedureUrl = isNewEmail
        ? `${process.env.APP_URL}/login?redirect=${procedure.url}`
        : `${process.env.APP_URL}${procedure.url}`

      return sendgrid.sendEmail({
        to: email,
        template_id: 'd-3d7eb5e8a8c441d48246cce0c751f812',
        dynamic_template_data: {
          name: senderName,
          procedure_name: procedure.name,
          procedure_url: procedureUrl,
          title
        }
      })
    })

    // Send emails concurrently
    const emailResponses = await Promise.all(emailPromises)

    let projectId = procedure.project_id
    if (!projectId) {
      const { data: pp, error: errorGetProcedure } = await supabase.from('procedures').select('id, project_id').eq('secondary_procedure_of', procedure.id).single()
      if (errorGetProcedure) { console.log('errorGetProcedure: ', errorGetProcedure) }
      projectId = pp.project_id
    }

    if (projectId) {
      await sharing.updateNotifiedStatus(emailsWithoutSender, projectId)
    }

    // Log email responses
    emailResponses.forEach((response) => {
      console.log(`Email sent. Status: ${response[0].statusCode}`)
      console.log('Headers:', response[0].headers)
    })

    res.status(200).send('Notifications sent successfully')
  } catch (error) {
    console.error('Error in notification process:', error)
    res.status(500).send('Internal server error')
  }
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
    const { error: errorUpdateProfile } = await supabase.from('profiles')
      .update({ verified: true }).eq('user_id', data.user_id)
    if (errorUpdateProfile) { throw errorUpdateProfile }

    axios({
      url: responseUrl,
      method: 'post',
      data: {
        text: `${data.firstname} ${data.lastname} (${data.email})
        pour la collectivité de code INSEE ${data.collectivite_id} est vérifié et validé.`
      }
    })

    const { data: profiles } = await supabase.from('profiles').select('*')
      .eq('user_id', data.user_id)

    const profile = profiles[0]
    const collectivite = geo.getCollectivite(profile.collectivite_id)

    const sharedProcedureUrl = await sharing.hasProcedureShared(data.email)
    sendgrid.sendEmail({
      to: profile.email,
      template_id: 'd-0143010573f6497b86abbd4e4c96f46e',
      dynamic_template_data: Object.assign({
        collectivite_name: collectivite.intitule,
        shared_procedure_url: sharedProcedureUrl ?? false,
        base_url: process.env.APP_URL
      }, profile),
      send_at: Math.round((Date.now() / 1000)) + (60 * 5)
    })
  } catch (error) {
    console.log('collectiviteValidation', error)
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
