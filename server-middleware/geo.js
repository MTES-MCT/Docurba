/* eslint-disable no-console */
const express = require('express')
const app = express()
app.use(express.json())

const geo = require('./modules/geo.js')

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

app.get('/collectivites', (req, res) => {
  console.log('ENDPOINT collectivites')
  const communes = geo.getCollectivites(req.query)
  res.status(200).send(communes)
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

app.get('/geojson/:locality', (req, res) => {
  try {
    let geojson
    if (req.params.locality === 'communes') {
      geojson = geo.getCommunesGeoJson(req.query.codes)
    } else if (req.params.locality === 'departements') {
      geojson = geo.getDepartementsGeoJson(req.query.codes)
    } else if (req.params.locality === 'regions') {
      geojson = geo.getRegionsGeoJson(req.query.codes)
    } else {
      throw new Error('Type de localité invalide')
    }
    res.status(200).send(geojson)
  } catch (error) {
    res.status(400).send({ message: error.message })
  }
})

app.get('/topojson/:locality', (req, res) => {
  try {
    let topojson
    if (req.params.locality === 'communes') {
      topojson = geo.getCommunesTopoJson(req.query.codes)
    } else if (req.params.locality === 'departements') {
      topojson = geo.getDepartementsTopoJson(req.query.codes)
    } else if (req.params.locality === 'regions') {
      topojson = geo.getRegionsTopoJson(req.query.codes)
    } else {
      throw new Error('Type de localité invalide')
    }
    res.status(200).send(topojson)
  } catch (error) {
    res.status(400).send({ message: error.message })
  }
})

module.exports = app
