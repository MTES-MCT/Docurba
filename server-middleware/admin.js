const express = require('express')
const app = express()
app.use(express.json())

const sendgrid = require('./modules/sendgrid.js')
const slack = require('./modules/slack.js')

app.post('/help', (req, res) => {
  const { title, message, email } = req.body

  sendgrid.sendEmail({
    to: ['fabien@quantedsquare.com', 'celia.vermicelli@beta.gouv.fr', 'hermance.gauthier@developpement-durable.gouv.fr'],
    replyTo: email,
    template_id: 'd-23a3309075ab4710af6028e4639bf6dc',
    dynamic_template_data: {
      title,
      message
    }
  })

  res.status(200).send('OK')
})

app.post('/pac', (req, res) => {
  const { userData, pacData } = req.body

  // console.log(userData, pacData)

  slack.requestPAC(userData, pacData)

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
