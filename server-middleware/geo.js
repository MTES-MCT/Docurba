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

module.exports = app
