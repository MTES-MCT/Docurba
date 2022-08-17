const express = require('express')
const app = express()
app.use(express.json())
app.use(express.urlencoded({ extended: true }))

const { createClient } = require('@supabase/supabase-js')
const supabase = createClient('https://ixxbyuandbmplfnqtxyw.supabase.co', process.env.SUPABASE_ADMIN_KEY)

const axios = require('axios')

app.post('/notify/admin', (req, res) => {
  // eslint-disable-next-line no-console
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
          type: 'actions',
          block_id: 'actions1',
          elements: [
            {
              type: 'button',
              text: {
                type: 'plain_text',
                text: `Valider ${userData.email}`
              },
              value: JSON.stringify(userData),
              action_id: 'ddt_validation'
            }
          ]
        },
        {
          type: 'divider'
        }
      ]
    }
  }).then((res) => {
    // eslint-disable-next-line no-console
    console.log('then: ', res.data)
  }).catch((err) => {
    // eslint-disable-next-line no-console
    console.log('catch', err.response.data)
  })
  // } catch (err) {
  //   console.log(err)
  // }
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

      const { data, error } = await supabase.from('admin_users_dept').update({ role: 'ddt' }).match({
        user_email: userData.email,
        dept: userData.dept.code_departement
      })

      if (data && !error) {
        res.status(200).send('OK')
        axios({
          url: responseUrl,
          method: 'post',
          data: {
            text: `Role DDT validé pour ${userData.email}`
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
