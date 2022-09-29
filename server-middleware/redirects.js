const express = require('express')
const app = express()

app.get('/*', (req, res, next) => {
  // The user will be redirected to this url in case of password recovery.
  // https://docurba.beta.gouv.fr/#access_token=XXX&expires_in=3600&refresh_token=XXX&token_type=bearer&type=recovery

  if (req.hostname.includes('incubateur.net')) {
    res.redirect(301, `https://docurba.beta.gouv.fr${req.originalUrl}`)
  } else {
    next()
  }
})

module.exports = app
