const express = require('express')
const app = express()
app.use(express.json())

const communes = require('./Data/EnrichedCommunes.json')
const urba = require('./modules/urba.js')
// const intercommunalites = require('../Data/EnrichedIntercomunalites.json')

// app.get('/communes', (req, res) => {

// })

app.get('/communes/:code', async (req, res) => {
  const commune = communes.find(c => c.code === req.params.code)

  if (commune) {
    const communeState = await urba.getCommuneState(req.params.code)
    res.status(200).send(communeState)
  } else {
    res.status(404).send(null)
  }
})

// app.get('/intercommunalites', (req, res) => {

// })

// app.get('/intercommunalites/:code', (req, res) => {

// })

module.exports = app
