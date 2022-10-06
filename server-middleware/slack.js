const express = require('express')
const app = express()
app.use(express.json())
app.use(express.urlencoded({ extended: true }))

const axios = require('axios')

// modules
const admin = require('./modules/admin.js')
const slack = require('./modules/slack.js')

app.post('/notify/admin', (req, res) => {
  // eslint-disable-next-line no-console
  console.log('Notify team in slack')
  const { userData } = req.body

  // try {
  slack.requestDepartementAccess(userData).then((res) => {
    // eslint-disable-next-line no-console
    console.log('Slack then: ', res.data)
  }).catch((err) => {
    // eslint-disable-next-line no-console
    console.log('Slack catch', err.response.data)
  })
  // } catch (err) {
  //   console.log(err)
  // }

  res.status(200).send('OK')
})

// Webhook  from slack
app.post('/webhook/interactivity', async (req, res) => {
  const payload = JSON.parse(req.body.payload)

  // eslint-disable-next-line no-console
  console.log('slack payload: ', payload)

  const responseUrl = payload.response_url

  if (payload.actions && payload.actions.length) {
    const action = payload.actions[0]

    // eslint-disable-next-line no-console
    console.log('slack action: ', action)

    if (action.action_id === 'ddt_validation') {
      const userData = JSON.parse(action.value)

      // eslint-disable-next-line no-console
      console.log('userData:', userData)

      const { data, error } = await admin.updateUserRole(userData, 'ddt')

      if (data && !error) {
        res.status(200).send('OK')
        axios({
          url: responseUrl,
          method: 'post',
          data: {
            text: `Role DDT/DEAL validé pour ${userData.email}`
          }
        })
      } else {
        // eslint-disable-next-line no-console
        console.log('err updating role', error)
      }
    }
  }
})

module.exports = app
