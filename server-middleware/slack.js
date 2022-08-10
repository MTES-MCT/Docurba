const express = require('express')
const app = express()
app.use(express.json())

const axios = require('axios')

app.post('/notify/admin', (req, res) => {
  console.log('Notify team in slack')
  const { userData } = req.body

  // try {
  axios({
    url: 'https://hooks.slack.com/services/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',
    method: 'post',
    data: {
      text: `Demande d'accès DDT de ${userData.firstname} ${userData.lastname}`,
      blocks: [
        {
          type: 'header',
          text: {
            type: 'plain_text',
            text: `Demande d'accès DDT de ${userData.firstname} ${userData.lastname}`
          }
        },
        {
          type: 'section',
          text: {
            type: 'mrkdwn',
            text: `- departement: ${userData.dept.nom_departement} - ${userData.dept.code_departement} \n - email: ${userData.email}`
          }
        },
        {
          type: 'divider'
        }
      ]
    }
  }).then((res) => {
    console.log('then: ', res.data)
  }).catch((err) => {
    console.log('catch', err.response.data)
  })
  // } catch (err) {
  //   console.log(err)
  // }
})

module.exports = app
