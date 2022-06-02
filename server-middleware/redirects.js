const express = require('express')
const app = express()

app.get('/*', (req, res, next) => {
  if (req.hostname.includes('incubateur.net')) {
    res.redirect(301, `https://docurba.beta.gouv.fr${req.originalUrl}`)
  } else {
    next()
  }
})

module.exports = app
