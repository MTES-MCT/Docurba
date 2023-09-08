const express = require('express')
const app = express()
app.use(express.json())

const _ = require('lodash')

const communes = require('./Data/EnrichedCommunes.json')
const intercommunalites = require('./Data/EnrichedIntercommunalites.json')

const departements = require('./Data/INSEE/departements.json')
const regions = require('./Data/INSEE/regions.json')

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
    const departement = Object.assign({}, departements.find(d => d.code === commune.departementCode))
    delete departement.communes
    delete departement.region

    res.status(200).send(Object.assign({
      intercommunalite: intercommunalites.find(i => i.code === commune.intercommunaliteCode),
      region: regions.find(r => r.code === commune.regionCode),
      departement
    }, commune))
  } else {
    res.status(404).send(null)
  }
})

app.get('/intercommunalites', (req, res) => {
  const queryKeys = Object.keys(req.query)

  if (req.query.codes) {
    const intercommunalitesCodes = req.query.codes

    const filterredIntercomunalites = intercommunalites.filter((intercommunalite) => {
      return intercommunalitesCodes.includes(intercommunalite.code)
    })

    res.status(200).send(filterredIntercomunalites)
  }

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
