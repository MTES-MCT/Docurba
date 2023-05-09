/* eslint-disable no-console */
const fs = require('fs')

const express = require('express')
const app = express()
app.use(express.json())

const axios = require('axios')
const FormData = require('form-data')

app.get('/:ref', (req, res) => {
  try {
    const form = new FormData()
    form.append('url', 'https://www.google.com/')
    form.append('marginTop', '0')
    form.append('marginBottom', '0')
    form.append('marginLeft', '0')
    form.append('marginRight', '0')

    axios.post(
      'https://gotenberg-5hkjqo623a-od.a.run.app/forms/chromium/convert/url',
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
    })
  } catch (err) {
    console.log(err)
    // res.status(400).send(err.toJSON())
  }
})

module.exports = app
