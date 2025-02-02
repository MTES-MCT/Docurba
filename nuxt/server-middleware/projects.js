const express = require('express')
const app = express()
app.use(express.json())

const _ = require('lodash')

const supabase = require('./modules/supabase.js')
const sendgrid = require('./modules/sendgrid.js')
const geo = require('./modules/geo.js')
const hour = 1000 * 60 * 60
const day = hour * 24

// app.post('/notify/shared/frp', async (req, res) => {
//   const { sharings } = req.body
//   console.log('sharings: ', sharings)
//   try {
//     await sendgrid.sendEmail({
//       to: sharings.to,
//       template_id: 'd-3d7eb5e8a8c441d48246cce0c751f812',
//       dynamic_template_data: {
//         sender_email: sharings.sender_email,
//         sender_firstname: sharings.sender_firstname || '',
//         sender_lastname: sharings.sender_lastname || '',
//         url_frp: 'https://docurba.beta.gouv.fr/frise/' + sharings.procedure_id || '',
//         procedure_name: sharings.procedure_name || ''
//       }
//     })
//     res.status(200).send('OK')
//   } catch (error) {
//     console.log('error: ', error)
//     res.status(400).send('Email Sharing FRP failed')
//   }
// })

app.post('/notify/shared', (req, res) => {
  const { sharings, sharedByData } = req.body

  sharings.forEach(async (sharing) => {
    const { data: notifications, error } = await supabase.from('projects_sharing').select('notified, shared_by').match({
      user_email: sharing.user_email,
      project_id: sharing.project_id
    })

    if (!error) {
      // Find a sharing that was not notified.
      const notification = notifications.find(n => !n.notified)

      const { data: admins } = await supabase.from('profiles')
        .select('*').eq('user_id', notification.shared_by)
      const admin = admins[0]

      const { data: projects } = await supabase.from('projects').select('*').eq('id', sharing.project_id)
      const project = projects[0]

      const collectivite = geo.getCollectivite(project.collectivite_id)

      if (notification) {
        sendgrid.sendEmail({
          to: sharing.user_email,
          template_id: sharing.role === 'write' ? 'd-bdd5ef31891546bcb6401fb6cdf2d391' : 'd-daf95559ce09481ca8d42d6e026fb9f3',
          dynamic_template_data: {
            project: sharing.project_id,
            firstname: admin.firstname || '',
            lastname: admin.lastname || '',
            dept: admin.departement,
            collectivite: collectivite.intitule
          }
        }).then(async () => {
          await supabase.from('projects_sharing').update({
            notified: true
          }).match({
            user_email: sharing.user_email,
            project_id: sharing.project_id
          })
        })
      }

      res.status(200).send('OK')
    } else {
      res.status(400).send('Sharing not notified')
    }
  })
})

app.post('/notify/update', async (req, res) => {
  const projectId = req.body.projectId
  const minDate = Date.now() - day

  const { data: sharings, error } = await supabase.from('projects_sharing')
    .select('id, user_email, last_update_notification').eq('project_id', projectId)

  if (!error) {
    // This is to prevent sending 2 emails for the same update.
    const uniqSharings = _.uniqBy(sharings, s => s.user_email)

    uniqSharings.forEach(async (sharing) => {
      const lastNotif = +new Date(sharing.last_update_notification)

      const { data: profile } = await supabase.from('profiles')
        .select('*').eq('email', sharing.user_email)

      const readingUrl = `https://docurba.beta.gouv.fr/documents/projet-${projectId}/pac`
      const writingUrl = `https://docurba.beta.gouv.fr/trames/projet-${projectId}`

      if (lastNotif < minDate) {
        sendgrid.sendEmail({
          to: sharing.user_email,
          template_id: 'd-2b1d871bc04141e69c56e5a89dc20a74',
          dynamic_template_data: {
            project_id: 'projet-' + projectId,
            firstname: profile.firstname,
            lastname: profile.lastname,
            url: sharing.role === 'write' ? writingUrl : readingUrl
          }
        }).then(async () => {
          await supabase.from('projects_sharing').update({
            last_update_notification: (new Date()).toISOString()
          }).eq('id', sharing.id)
        })
      }
    })
    res.status(200).send('OK')
  } else {
    res.status(400).send('Update not notified')
  }
})

module.exports = app
