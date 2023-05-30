/* eslint-disable no-console */
const express = require('express')
const app = express()
app.use(express.json())

const axios = require('axios')
const FormData = require('form-data')

// const isDev = process.env.NODE_ENV === 'development'

const gotenbergUrl = 'https://gotenberg-5hkjqo623a-od.a.run.app'
// const gotenbergUrl = isDev ? 'http://localhost:8080' : 'https://gotenberg-5hkjqo623a-od.a.run.app'
const printUrl = 'https://docurba.beta.gouv.fr'
// const printUrl = isDev ? 'https://dev-dot-docurba.ew.r.appspot.com' : 'https://docurba.beta.gouv.fr'

app.get('/:ref', (req, res) => {
  const { ref } = req.params

  console.log('PRINTING URL: ', `${printUrl}/print/${ref}`)

  try {
    const form = new FormData()
    form.append('url', `${printUrl}/print/${ref}`)
    form.append('preferCssPageSize', true)
    form.append('marginTop', '0')
    form.append('marginBottom', '0')
    form.append('marginLeft', '0')
    form.append('marginRight', '0')

    axios.post(
      `${gotenbergUrl}/forms/chromium/convert/url`,
      form,
      {
        headers: {
          ...form.getHeaders()
        },
        responseType: 'stream'
      }
    ).then((response) => {
      res.setHeader('Content-Type', 'application/pdf')
      res.setHeader('Content-Disposition', 'attachment; filename="pac.pdf"')
      response.data.pipe(res)
    }).catch((err) => {
      console.log('err pdf', err)
    })
  } catch (err) {
    console.log('err pdf', err)
    // res.status(400).send(err.toJSON())
  }
})

module.exports = app
