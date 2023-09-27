const express = require('express')
const csw = require('./modules/csw.js')
const app = express()
app.use(express.json())

app.get('/:codeInsee/categories', async (req, res) => {
  const data = await csw.getCategories(req.params.codeInsee, req.query.isEpci)
  res.status(200).send(data)
})

app.get('/:codeInsee', async (req, res) => {
  const data = await csw.getData(req.params.codeInsee, req.query.isEpci, req.query.category)
  res.status(200).send(data)
})

module.exports = app
