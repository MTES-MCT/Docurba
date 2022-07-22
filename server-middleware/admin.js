const express = require('express')
const app = express()
app.use(express.json())

const sendgrid = require('./modules/sendgrid.js')

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

module.exports = app
