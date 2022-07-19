const express = require('express')
const app = express()
app.use(express.json())

const EPCI = require('./Data/EPCI.json')

app.get('/', (req, res) => {
  const dep = req.query.departement

  const epciByDep = EPCI.filter((e) => {
    // eslint-disable-next-line eqeqeq
    return !!e.towns.find(t => +t.code_departement == dep)
  }) || []

  res.status(epciByDep.length ? 200 : 404).send(epciByDep)
})

app.get('/:id', (req, res) => {
  // eslint-disable-next-line eqeqeq
  const epciById = EPCI.find(e => e.EPCI == req.params.id)
  res.status(epciById ? 200 : 404).send(epciById)
})

module.exports = app
