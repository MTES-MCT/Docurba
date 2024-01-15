const express = require('express')
const app = express()
app.use(express.json())

const sendgrid = require('./modules/sendgrid.js')
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

  const { data: profiles } = await supabase.from('profiles').select('firstname, lastname').eq('email', email)
  const profile = profiles[0] || {}

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

module.exports = app
