const express = require('express')
const app = express()
app.use(express.json())

const sendgrid = require('./modules/sendgrid.js')
const slack = require('./modules/slack.js')
const supabase = require('./modules/supabase.js')

app.post('/help', async (req, res) => {
  const { title, message, section, email, dir } = req.body

  // Send an email to the team.
  sendgrid.sendEmail({
    to: ['fabien@quantedsquare.com', 'celia.vermicelli@beta.gouv.fr', 'celia.vermicelli@docurba.beta.gouv.fr', 'hermance.gauthier@docurba.beta.gouv.fr'],
    replyTo: email,
    template_id: 'd-c0c2bbdfc40546bbaa2e0c0f167d02f3',
    dynamic_template_data: {
      title,
      message,
      section,
      dir
    }
  })

  const { data: profile } = await supabase.from('profiles').select('firstname, lastname').eq('email', email)

  // Send a confirmation email to the user.
  sendgrid.sendEmail({
    to: email,
    template_id: 'd-23a3309075ab4710af6028e4639bf6dc',
    dynamic_template_data: {
      firstname: profile.firstname,
      lastname: profile.lastname
    }
  })

  res.status(200).send('OK')
})

app.post('/pac', (req, res) => {
  const { userData, pacData } = req.body

  // console.log(userData, pacData)

  slack.requestPAC(userData, pacData)

  // Todo: Test this email is working.
  sendgrid.sendEmail({
    to: [userData.email],
    template_id: 'd-adea54033fba4a2b9d6f814297f2eca7',
    dynamic_template_data: {
      firstname: userData.user_metadata.firstname,
      doc_type: pacData.doc_type,
      commune: pacData.town.nom_commune
      // town: pacData.tow
    }
  })
})

module.exports = app
