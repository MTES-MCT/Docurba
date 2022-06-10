const express = require('express')
const app = express()
app.use(express.json())

const { createClient } = require('@supabase/supabase-js')
const supabase = createClient('https://ixxbyuandbmplfnqtxyw.supabase.co', process.env.SUPABASE_ADMIN_KEY)

const sendgrid = require('./modules/sendgrid.js')

app.post('/password', async (req, res) => {
  const { data: user, error } = await supabase.auth.api.generateLink(
    'recovery',
    req.body.email,
    {
      redirectTo: req.body.redirectTo
    }
  )

  // console.log(user, error, req.body.redirectTo)
  if (!error && user && user.action_link) {
    sendgrid.sendEmail({
      to: req.body.email,
      template_id: 'd-06e865fdc30d42a398fdc6bc532deb82',
      dynamic_template_data: {
        redirectURL: user.action_link.replace('https://docurba.beta.gouv.fr/', req.body.redirectTo)
      }
    })
  }

  res.status(200).send('OK')
})

module.exports = app
