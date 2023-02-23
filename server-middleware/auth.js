const express = require('express')
const app = express()
app.use(express.json())

const { createClient } = require('@supabase/supabase-js')
const supabase = createClient('https://ixxbyuandbmplfnqtxyw.supabase.co', process.env.SUPABASE_ADMIN_KEY)

// modules
const sendgrid = require('./modules/sendgrid.js')
const pipedrive = require('./modules/pipedrive.js')
const slack = require('./modules/slack.js')

app.post('/password', async (req, res) => {
  // console.log('/password body', req.body)

  const { data: user, error } = await supabase.auth.admin.generateLink({
    type: 'recovery',
    email: req.body.email
  })

  // The user will be redirected to this url in case of password recovery.
  // https://docurba.beta.gouv.fr/#access_token=XXX&expires_in=3600&refresh_token=XXX&token_type=bearer&type=recovery

  // https://ixxbyuandbmplfnqtxyw.supabase.co/auth/v1/verify?token=XXX&type=recovery&redirect_to=https://docurba.beta.gouv.fr/
  // console.log('user.action_link', user.action_link)

  if (!error && user && user.properties.action_link) {
    sendgrid.sendEmail({
      to: req.body.email,
      template_id: 'd-06e865fdc30d42a398fdc6bc532deb82',
      dynamic_template_data: {
        redirectURL: user.properties.action_link
      }
    })

    res.status(200).send('OK')
  } else {
    // eslint-disable-next-line no-console
    console.log('Error reset password', error)
    res.status(400).send(error)
  }
})

app.post('/signup', async (req, res) => {
  // No email verifycation at the moment
  // Need to test the type of link generated -> https://supabase.com/docs/reference/javascript/auth-api-generatelink
  // const { data: user, error } = await supabase.auth.api.generateLink(
  //   'email_change_current',
  //   req.body.email,
  //   {
  //     redirectTo: req.body.redirectTo
  //   }
  // )

  // // console.log('auth signup', user, error)

  // if (!error && user && user.action_link) {
  //   sendgrid.sendEmail({
  //     to: req.body.email,
  //     template_id: 'd-766d017b51124a108cabc985d0dbf451',
  //     dynamic_template_data: {
  //       redirectURL: user.action_link
  //     }
  //   })
  // } else {
  //   // eslint-disable-next-line no-console
  //   console.log('error sending verifycation email', error, user)
  // }

  const { userData } = req.body

  if (userData.isDDT) {
    await slack.requestDepartementAccess(userData)
  }

  await pipedrive.signup(userData)

  res.status(200).send('OK')
})

module.exports = app
