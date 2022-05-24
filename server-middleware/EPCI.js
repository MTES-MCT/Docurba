const express = require('express')
const app = express()
app.use(express.json())

const EPCI = require('./Data/EPCI.json')

app.get('/:id', (req, res) => {
  const epciById = EPCI.find(e => e.EPCI === req.params.id)
  res.status(epciById ? 200 : 404).send(epciById)
})

module.exports = app
