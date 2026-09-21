/* eslint-disable no-console */
const express = require('express')
const app = express()
app.use(express.json())

const geo = require('./modules/geo.js')

app.get('/collectivites', (req, res) => {
  const collectivites = geo.getCollectivites(req.query)
  // console.log('collectivitesSEND: ', collectivites)
  if (collectivites) {
    res.status(200).send(collectivites)
  } else {
    res.status(404).send(null)
  }
})

app.get('/collectivites/:code', (req, res) => {
  if (req.params.code.length > 5) {
    const intercommunalite = geo.getIntercommunalite(req.params.code)
    if (intercommunalite) {
      res.status(200).send(intercommunalite)
    } else {
      res.status(404).send(null)
    }
  } else {
    const commune = geo.getCommune(req.params.code)
    if (commune) {
      res.status(200).send(commune)
    } else {
      res.status(404).send(null)
    }
  }
})

app.get('/collectivites/:code/center', (req, res) => {
  if (req.params.code.length > 5) {
    res.status(200).send(geo.getIntercommunaliteCenter(req.params.code))
  } else {
    res.status(200).send(geo.getCommuneCenter(req.params.code))
  }
})

module.exports = app
