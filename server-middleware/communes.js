const express = require('express')
const app = express()
app.use(express.json())

const communes = require('./Data/communes-france.json')
const cache = {}

function getCommunesByDepartements (code) {
  if (!cache[code]) {
    cache[code] = communes.filter((c) => {
      // eslint-disable-next-line eqeqeq
      return c.code_departement == code
    })
  }

  return cache[code]
}

app.get('/:inseeId', (req, res) => {
  try {
    const inseeCode = parseInt(req.params.inseeId)
    const commune = communes.find(e => e.code_commune_INSEE === inseeCode)
    if (!commune) { throw new Error(`Le code commune INSEE ${req.params.inseeId} n'existe pas.`) }
    res.status(200).send(commune)
  } catch (error) {
    res.status(400).send({ message: error.message })
  }
})

// query params:
// departement - Departement code. eg. 22, 47
app.get('/', (req, res) => {
  // console.log('/communes ', req.query)
  res.status(200).send(getCommunesByDepartements(parseInt(req.query.departements)))
})

module.exports = app
