/* eslint-disable no-console */
const express = require('express')
const app = express()

app.use(express.json())
app.use(express.urlencoded({ extended: true }))

const sendgrid = require('./modules/sendgrid.js')
const supabase = require('./modules/supabase.js')

// modules
const { requireProcedureSharable, requireStateAgent } = require('./modules/auth.js')
const slack = require('./modules/slack.js')
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

app.post('/notify/frp_shared', async (req, res) => {
  try {
    await requireProcedureSharable(req)
  } catch (error) {
    return res.status(403).send({ message: error.message })
  }
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

app.post('/notify/frp', async (req, res) => {
  try {
    await requireStateAgent(req)
  } catch (error) {
    return res.status(403).send({ message: error.message })
  }

  slack.notifyFrpEvent(req.body).then((res) => {
    // eslint-disable-next-line no-console
    console.log('Slack then: ', res.data)
    res.status(200).send('OK')
  }).catch((err) => {
    // eslint-disable-next-line no-console
    console.log('Slack catch', err.response.data)
    res.status(500).send(err.response.data)
  })
})

module.exports = app
