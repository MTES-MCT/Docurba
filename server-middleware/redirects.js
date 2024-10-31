const express = require('express')
const app = express()

app.get('/*', (req, res, next) => {
  // The user will be redirected to this url in case of password recovery.
  // https://docurba.beta.gouv.fr/#access_token=XXX&expires_in=3600&refresh_token=XXX&token_type=bearer&type=recovery

  if (req.path === '/faq') {
    return res.redirect(301, 'https://docurba.crisp.help/fr/')
  }

  res.setHeader('Strict-Transport-Security', 'max-age=31536000; includeSubDomains')
  res.setHeader('X-Frame-Options', 'SAMEORIGIN')
  res.setHeader('X-Content-Type-Options', 'nosniff')

  if (req.hostname.includes('incubateur.net')) {
    res.redirect(301, `https://docurba.beta.gouv.fr${req.originalUrl}`)
  } else {
    next()
  }
})

module.exports = app
