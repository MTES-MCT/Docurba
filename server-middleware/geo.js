/* eslint-disable no-console */
const express = require('express')
const app = express()
app.use(express.json())

const geo = require('./modules/geo.js')

const fullTopojson = require('./Data/a-com2022-topo.json')

app.get('/communes', (req, res) => {
  const communes = geo.getCommunes(req.query)
  res.status(200).send(communes)
})

app.get('/communes/:code', (req, res) => {
  const commune = geo.getCommune(req.params.code)
  if (commune) {
    res.status(200).send(commune)
  } else {
    res.status(404).send(null)
  }
})

app.get('/intercommunalites', (req, res) => {
  const intercommunalites = geo.getIntercommunalites(req.query)
  res.status(200).send(intercommunalites)
})

app.get('/intercommunalites/:code', (req, res) => {
  const intercommunalite = geo.getIntercommunalite(req.params.code)
  if (intercommunalite) {
    res.status(200).send(intercommunalite)
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

app.get('/geojson/communes', (req, res) => {
  try {
    if (!req.query.codes) {
      throw new Error('"codes" parameter is mandatory')
    }
    const geojson = geo.getCommunesGeoJSON(req.query.codes)
    res.status(200).send(geojson)
  } catch (error) {
    res.status(400).send({ message: error.message })
  }
})

app.get('/topojson/communes', (req, res) => {
  try {
    if (!req.query.codes) {
      res.status(200).send(fullTopojson)
      return
    }

    const topojson = geo.getCommunesTopoJSON(req.query.codes)
    res.status(200).send(topojson)
  } catch (error) {
    res.status(400).send({ message: error.message })
  }
})

module.exports = app
