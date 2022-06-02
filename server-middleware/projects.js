const express = require('express')
const app = express()
app.use(express.json())

const { createClient } = require('@supabase/supabase-js')
const supabase = createClient('https://ixxbyuandbmplfnqtxyw.supabase.co', process.env.SUPABASE_ADMIN_KEY)

const sendgrid = require('./modules/sendgrid.js')

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
        })
      }

      res.statusCode(200).send('OK')
    } else {
      res.statusCode(400).send('Sharing not notified')
    }
  })
})

module.exports = app
