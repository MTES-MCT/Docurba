const express = require('express')
const app = express()
app.use(express.json())

const issues = require('./modules/github/issues.js')
const sendgrid = require('./modules/sendgrid.js')
const slack = require('./modules/slack.js')

app.post('/help', async (req, res) => {
  const { title, message, email, ref, path } = req.body

  await issues.createIssue(title, message, email, ref, path)
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
