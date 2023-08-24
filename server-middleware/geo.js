const express = require('express')
const app = express()
app.use(express.json())

const _ = require('lodash')

const communes = require('./Data/EnrichedCommunes.json')
const intercommunalites = require('./Data/EnrichedIntercomunalites.json')

app.get('/communes', (req, res) => {
  const queryKeys = Object.keys(req.query)

  if (queryKeys.length) {
    const filterredCommunes = _.filter(communes, req.query)
    res.status(200).send(filterredCommunes)
  } else {
    res.status(200).send(communes)
  }
})

app.get('/communes/:code', (req, res) => {
  const commune = communes.find((c) => {
    return c.code === req.params.code
  })

  if (commune) {
    res.status(200).send(commune)
  } else {
    res.status(404).send(null)
  }
})

app.get('/intercommunalites', (req, res) => {
  const queryKeys = Object.keys(req.query)

  if (queryKeys.length) {
    const filterredIntercomunalites = _.filter(intercommunalites, req.query)
    res.status(200).send(filterredIntercomunalites)
  } else {
    res.status(200).send(intercommunalites)
  }
})

app.get('/intercommunalites/:code', (req, res) => {
  const intercommunalite = intercommunalites.find((c) => {
    return c.code === req.params.code
  })

  if (intercommunalite) {
    res.status(200).send(intercommunalite)
  } else {
    res.status(404).send(null)
  }
})

module.exports = app
