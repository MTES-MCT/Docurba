const express = require('express')
const app = express()
app.use(express.json())

const _ = require('lodash')

const { createClient } = require('@supabase/supabase-js')
const supabase = createClient('https://ixxbyuandbmplfnqtxyw.supabase.co', process.env.SUPABASE_ADMIN_KEY)

const sendgrid = require('./modules/sendgrid.js')

const hour = 1000 * 60 * 60
const day = hour * 24

app.post('/notify/shared', (req, res) => {
  const sharings = req.body.sharings

  sharings.forEach(async (sharing) => {
    const { data: notifications, error } = await supabase.from('projects_sharing').select('notified').match({
      user_email: sharing.user_email,
      project_id: sharing.project_id
    })

    if (!error) {
      const notified = !!notifications.find(n => n.notified)

      if (!notified) {
        sendgrid.sendEmail({
          to: sharing.user_email,
          template_id: 'd-daf95559ce09481ca8d42d6e026fb9f3',
          dynamic_template_data: {
            project_id: sharing.project_id
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

    uniqSharings.forEach((sharing) => {
      const lastNotif = +new Date(sharing.last_update_notification)

      if (lastNotif < minDate) {
        sendgrid.sendEmail({
          to: sharing.user_email,
          template_id: 'd-2b1d871bc04141e69c56e5a89dc20a74',
          dynamic_template_data: {
            project_id: projectId
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
