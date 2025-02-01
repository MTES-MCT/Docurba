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

function getCommunesDetails (inseeArray) {
  // console.log('inseeArray: ', inseeArray)
  return communes.filter(e => inseeArray.includes(e.code_commune_INSEE.toString()))
}

app.get('/:inseeId', (req, res) => {
  try {
    const isCorse = (req.params.inseeId.includes('A') || req.params.inseeId.includes('B'))
    const inseeCode = isCorse ? req.params.inseeId : parseInt(req.params.inseeId)
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
  if (req.query.communes && req.query.communes.length > 0) {
    res.status(200).send(getCommunesDetails(req.query.communes))
  } else {
    let departementCode = req.query.departements
    if (departementCode !== '2A' && departementCode !== '2B') {
      departementCode = parseInt(req.query.departements)
    }
    res.status(200).send(getCommunesByDepartements(departementCode))
  }
})

module.exports = app
